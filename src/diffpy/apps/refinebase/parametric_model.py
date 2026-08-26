from collections import OrderedDict

import networkx as nx
import numpy
from diffpy.srfit.equation.literals import Operator, makeOperator
from diffpy.srfit.fitbase import FitContribution, Profile
from diffpy.srfit.pdf.pdfgenerator import PDFGenerator
from diffpy.structure import Structure


class ParametricModel:
    # TODO: add constraints and restraints method
    def __init__(self, name):
        self.meta = OrderedDict()
        self.name = name
        self._contribution = FitContribution(name)
        self._graph = nx.DiGraph()
        # NOTE: all submodels will share the same profile
        self._submodels = []
        old_validate = self._contribution._validate
        self._contribution._validate = lambda: self.validate(old_validate)

    def validate(self, old_validate):
        # must provide placeholders to pass the validation
        if self._contribution.profile is None:
            placeholder_profile = Profile()
            placeholder_profile.set_observed_profile(
                numpy.arange(100), numpy.arange(100)
            )
            self.set_profile(placeholder_profile)
        if self._contribution._eq is None:
            placeholder_equation = makeOperator(
                name=self.pdf_generator.name,
                symbol="g",
                operation=self.pdf_generator.operation,
                nin=0,  # NOTE: make sure nin=0 and nout=1 is correct
                nout=1,
            )
            self._contribution.set_equation(
                "g", ns={"g": placeholder_equation}
            )
        old_validate()

    def _construct_parameter_graph(self, parameterset, prefix=""):
        parent_name = f"{prefix}{parameterset.name}"
        self._graph.add_node(parent_name, parameter=parameterset)

        for par in parameterset._iter_managed():
            child_name = f"{parent_name}.{par.name}"
            self._graph.add_node(child_name, parameter=par)
            self._graph.add_edge(parent_name, child_name)
            if hasattr(par, "_iter_managed"):
                self._construct_parameter_graph(
                    par,
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
                nin=0,  # NOTE: make sure nin=0 and nout=1 is correct
                nout=1,
            )
        # FIXME: registerOperator -> register_operator
        #   once updated in diffpy.srfit.
        self._contribution._eqfactory.registerOperator(symbol, op)
        # Allow iterPars to traverse the submodel's parameters
        self._contribution.add_parameter_set(model._contribution)
        self._submodels.append(model)

    @property
    def parameters(self):
        return {
            par_node_id: self._graph.nodes[par_node_id]["parameter"]
            for par_node_id in self._graph.nodes
            if self._graph.out_degree(par_node_id) == 0
        }

    def set_profile(self, profile):
        self._contribution.set_profile(profile)
        if hasattr(self, "pdf_generator"):
            self.pdf_generator.set_profile(profile)
        for submodel in self._submodels:
            submodel.set_profile(profile)

    def set_equation(self, equation_str, ns={}):
        self._contribution.set_equation(equation_str, ns=ns)

    def get_equation(self):
        return self._contribution.get_equation()

    def add_parameter(self, parameter):
        self._contribution.add_parameter(parameter)

    def remove_parameter(self, parameter):
        self._contribution._remove_parameter(parameter)

    def add_parameter_set(self, parameterset):
        self._contribution.add_parameter_set(parameterset)

    def remove_parameter_set(self, parameterset):
        self._contribution.remove_parameter_set(parameterset)

    def prepare(self):
        self._graph.clear()
        self._construct_parameter_graph(self._contribution, prefix="")

    def evaluate(self):
        return self._contribution._eq()

    def residual(self):
        # TODO: Implement residual calculation for the model
        pass


class ParametricModelPDF(ParametricModel):
    def __init__(self, name, structure: Structure, meta=None):
        super().__init__(name=name)
        self._initialize_pdf_generator(structure, meta)

    def _initialize_pdf_generator(self, structure: Structure, meta: dict):
        self.pdf_generator = PDFGenerator(self.name)
        # FIXME: setStructure -> set_structure
        #  once updated
        self.pdf_generator.setStructure(structure)
        self._contribution.add_parameter_set(self.pdf_generator)
        self._contribution._RecipeContainer__managed = (
            self.pdf_generator._RecipeContainer__managed
        )
        self._contribution._parameters = self.pdf_generator._parameters

        if meta is not None:
            self.process_metadata(meta)

    def process_metadata(self, meta: dict = None):
        self.pdf_generator.meta.update(meta)
        # FIXME: processMetaData -> process_meta_data
        #  once updated in diffpy.srfit.
        self.pdf_generator._process_metadata()

    def evaluate(self):
        if self._contribution.profile is None:
            raise ValueError("Profile is not set for the PDF model.")
        return self.pdf_generator.operation()
