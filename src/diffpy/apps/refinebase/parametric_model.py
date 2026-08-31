import re
from collections import OrderedDict

import networkx as nx

from diffpy.srfit.equation.literals import Operator, makeOperator
from diffpy.srfit.fitbase import FitContribution
from diffpy.srfit.fitbase.parameter import Parameter, ParameterProxy
from diffpy.srfit.pdf.pdfgenerator import PDFGenerator
from diffpy.srfit.structure import constrain_as_space_group
from diffpy.structure import Structure


class ParametricModel:
    def __init__(self, name):
        self.name = name
        self.description = ""
        self._contribution = FitContribution(name)
        self._graph = nx.DiGraph()
        self.meta = OrderedDict()
        # all submodels will share the same profile
        self._submodels = []

    def _construct_parameter_graph(
        self, parameterset, prefix="", old_graph=None
    ):
        parent_name = f"{prefix}{parameterset.name}"
        self._graph.add_node(parent_name, parameter=parameterset)
        for par in parameterset._iter_local_parameters(
            regexp=re.compile("")  # regex is a required argument
        ):
            par_node_id = f"{parent_name}.{par.name}"
            if not old_graph or par_node_id not in old_graph.nodes:
                self._graph.add_node(
                    par_node_id,
                    parameter=par,
                    constrained_or_constant=False,
                )
            else:
                # apply stored constrained_or_constant information
                # from the old graph
                self._graph.add_node(
                    par_node_id,
                    parameter=par,
                    constrained_or_constant=old_graph.nodes[par_node_id][
                        "constrained_or_constant"
                    ],
                )
            self._graph.add_edge(parent_name, par_node_id)

        for obj in parameterset._iter_managed_parameter_containers():
            if hasattr(obj, "_iter_managed_parameter_containers"):
                child_name = f"{parent_name}.{obj.name}"
                # obj is handled as unconstrained by default
                self._graph.add_node(
                    child_name,
                    parameter=None,
                    constrained_or_constant=False,
                )
                self._graph.add_edge(parent_name, child_name)
                self._construct_parameter_graph(
                    obj,
                    prefix=f"{parent_name}.",
                )

    def register_submodel(self, symbol, model):
        """Register a parametric model to the current model."""
        op = model.evaluate
        if not isinstance(model.evaluate, Operator):
            op = makeOperator(
                name=model.name,
                symbol=symbol,
                operation=model.evaluate,
                nin=0,  # NOTE: make this (nin, nout) work for all scenarios
                nout=1,
            )
        # NOTE: registerOperator -> register_operator
        #   once updated in diffpy.srfit.
        self._contribution._eqfactory.registerOperator(symbol, op)
        # Replace parameter with the submodel's parameterset
        if symbol in self._contribution._parameters:
            self._contribution._remove_parameter(
                self._contribution._parameters[symbol]
            )
        self._contribution.add_parameter_set(model._contribution)
        self._submodels.append(model)
        self._rebuild_graph()

    @property
    def parameters(self):
        return {
            par_node_id: self._graph.nodes[par_node_id]["parameter"]
            for par_node_id in self._graph.nodes
            if isinstance(
                self._graph.nodes[par_node_id]["parameter"], Parameter
            )
        }

    @property
    def independent_parameters(self):
        return {
            par_node_id: self._graph.nodes[par_node_id]["parameter"]
            for par_node_id in self._graph.nodes
            if isinstance(
                self._graph.nodes[par_node_id]["parameter"], Parameter
            )
            and not (
                (
                    hasattr(
                        self._graph.nodes[par_node_id]["parameter"], "const"
                    )
                    and self._graph.nodes[par_node_id]["parameter"].const
                )
                or self._graph.nodes[par_node_id]["parameter"].constrained
                # NOTE: this is a workaround for the constraints not reflected
                #   in par.constrained
                or self._graph.nodes[par_node_id]["constrained_or_constant"]
            )
        }

    def set_profile(self, profile):
        self._contribution.set_profile(profile)
        if hasattr(self, "pdf_generator"):
            self.pdf_generator.set_profile(profile)
        for submodel in self._submodels:
            submodel.set_profile(profile)

    def _rebuild_graph(self):
        """
        Rebuild the parameter graph based on the current contribution.
        """
        old_graph = self._graph
        self._graph.clear()
        self._construct_parameter_graph(
            self._contribution, prefix="", old_graph=old_graph
        )

    def evaluate(self):
        return self._contribution._eq()


class ParametricModelEquation(ParametricModel):
    def __init__(self, name, equation_str):
        super().__init__(name=name)
        self._contribution.set_equation(equation_str)
        self.description = f"ParametricModelEq: {equation_str}"
        self._rebuild_graph()


class ParametricModelPDF(ParametricModel):
    def __init__(self, name, structure: Structure, meta=None):
        super().__init__(name=name)
        self.description = f"ParametricModelPDF: {name}"
        self._initialize_pdf_generator(structure, meta)
        self._rebuild_graph()
        # Constrain aliased parameters
        constrained_par_names = [
            r"\.U21$",  # U21=U12
            r"\.U31$",
            r"\.U32$",
            r"\.B21$",
            r"\.B31$",
            r"\.B32$",
            r"\.occupancy$",  # occupancy=oc
        ]
        constrained_par_regex = re.compile("|".join(constrained_par_names))
        for par_name in self.parameters.keys():
            if constrained_par_regex.search(par_name):
                self._graph.nodes[par_name]["constrained_or_constant"] = True

        if meta is not None:
            self.process_metadata(meta)

        # Add a placeholder equation to pass the validation
        old_validate = self._contribution._validate
        self._contribution._validate = lambda: self.validate(old_validate)

    def validate(self, old_validate):
        if self._contribution._eq is None:
            placeholder_equation = makeOperator(
                name=self.pdf_generator.name,
                symbol=f"{self.name}_eq_placeholder",
                operation=self.pdf_generator.operation,
                nin=0,
                nout=1,
            )
            self._contribution.set_equation(
                "g", ns={"g": placeholder_equation}
            )
        old_validate()

    def _initialize_pdf_generator(self, structure: Structure, meta: dict):
        self.pdf_generator = PDFGenerator(self.name)
        # NOTE: setStructure -> set_structure
        #   once updated in diffpy.srfit.
        self.pdf_generator.setStructure(structure)
        # Get access to all parameters in the PDFGenerator
        self._contribution.add_parameter_set(self.pdf_generator)
        self._contribution._RecipeContainer__managed = (
            self.pdf_generator._RecipeContainer__managed
        )
        self._contribution._parameters = self.pdf_generator._parameters

    def process_metadata(self, meta: dict = None):
        self.pdf_generator.meta.update(meta)
        self.pdf_generator._process_metadata()

    def evaluate(self):
        if self._contribution.profile is None:
            raise ValueError("Profile is not set for the PDF model.")
        return self.pdf_generator.operation()

    def constrain_symmetry(self, space_group: str):
        space_group_parset = constrain_as_space_group(
            self.pdf_generator.phase, space_group
        )
        # Get the independent parameters from spacegroup symmetry
        free_variables = []
        for latpar in space_group_parset.latpars:
            free_variables.append(latpar)
        for adpar in space_group_parset.adppars:
            free_variables.append(adpar)
        for xyzpar in space_group_parset.xyzpars:
            free_variables.append(xyzpar)
        for i in range(len(free_variables)):
            while isinstance(free_variables[i], ParameterProxy):
                free_variables[i] = free_variables[i].par
        # Add constraints information for dependent parameters
        symmetry_parnames = [
            r"\.a$",
            r"\.b$",
            r"\.c$",
            r"\.alpha$",
            r"\.beta$",
            r"\.gamma$",
            r"\.x$",
            r"\.y$",
            r"\.z$",
            r"\.Uiso$",
            r"\.U11$",
            r"\.U22$",
            r"\.U33$",
            r"\.U12$",
            r"\.U13$",
            r"\.U23$",
            r"\.Biso$",
            r"\.B11$",
            r"\.B22$",
            r"\.B33$",
            r"\.B12$",
            r"\.B13$",
            r"\.B23$",
        ]
        symmetry_par_regex = re.compile("|".join(symmetry_parnames))
        for par_name, par in self.parameters.items():
            if par.constrained or par.const:
                self._graph.nodes[par_name]["constrained_or_constant"] = True
            elif symmetry_par_regex.search(par_name):
                while isinstance(par, ParameterProxy):
                    par = par.par
                if par not in free_variables:
                    self._graph.nodes[par_name][
                        "constrained_or_constant"
                    ] = True
