from pathlib import Path

import networkx as nx

from diffpy.srfit.fitbase import Profile
from diffpy.srfit.fitbase.parameter import Parameter
from diffpy.srfit.fitbase.parameterset import ParameterSet
from diffpy.srfit.pdf.pdfparser import PDFParser
from diffpy.srfit.structure import struToParameterSet
from diffpy.structure import Structure


class RefinenableModel(ParameterSet):
    """
    A RefinenableModel instance provides access to both the ParameterSet
    and the underlying model object.
    """

    def __init__(self, name):
        super().__init__(name=name)
        self.model = None
        self.parameters = None


class ParameterSetTree:
    """
    A TreeView instance provides a tree view of the ParameterSet.
    """

    def __init__(self, parameter_set):
        self.graph = nx.DiGraph()
        self._construct_parameter_tree_view(parameter_set, prefix="")

    def _construct_parameter_tree_view(self, parameterset, prefix=""):
        parent_name = f"{prefix}{parameterset.name}"
        self.graph.add_node(parent_name, parameter=parameterset)

        for par in parameterset._iterManaged():
            child_name = f"{parent_name}.{par.name}"
            self.graph.add_node(child_name, parameter=par)
            self.graph.add_edge(parent_name, child_name)
            if hasattr(par, "_iterManaged"):
                self._construct_parameter_tree_view(
                    par,
                    prefix=f"{parent_name}.",
                )


class ParameterParser:
    def __init__(self):
        pass

    MISSING_FILE_WARNING = (
        "{description} file '{file}' is missing. "
        "Please check the path and try again."
    )

    def _parse_pdf(
        self, profile_file: str, parset_name: str = "profile_parameterset"
    ):
        if not Path(profile_file).exists():
            raise FileNotFoundError(
                self.MISSING_FILE_WARNING.format(
                    description="Profile", file=profile_file
                )
            )
        pass
        parser = PDFParser()
        parser.parseFile(profile_file)
        profile = Profile()
        profile.loadParsedData(parser)
        parameter_values = parser.getData()
        parameter_names = ["x", "y", "dx", "dy"]
        parameter_set = _create_parameter_set(
            parameter_names, parameter_values, parset_name
        )
        profile_model = RefinenableModel(name=parset_name)
        profile_model.model = profile
        profile_model.parameters = parameter_set
        meta = dict(parser.getMetaData())
        return profile_model, meta

    def _parse_structure(
        self, structure_file: str, parset_name: str = "structure_parameterset"
    ):
        if not Path(structure_file).exists():
            raise FileNotFoundError(
                self.MISSING_FILE_WARNING.format(
                    description="Structure", file=structure_file
                )
            )
        stru = Structure()
        stru.read(structure_file)
        stru_diffpy_parset = struToParameterSet(parset_name, stru)
        structure_model = RefinenableModel(name=parset_name)
        structure_model.model = stru
        structure_model.parameters = ParameterSet(name=parset_name)
        structure_model.parameters.addParameterSet(
            stru_diffpy_parset.getLattice()
        )
        for atom_parset in stru_diffpy_parset.getScatterers():
            structure_model.parameters.addParameterSet(atom_parset)
        return structure_model


def _create_parameter_set(names, values, parset_name):
    """
    Construct a ParameterSet from a list of variables.

    Parameters
    ----------
    names : list of str
        The names of the variables.
    values : list of values
        The list of values corresponding to the variable names.
    parset_name : str
        The name of the ParameterSet.

    Returns
    -------
    ParameterSet
        The converted ParameterSet.
    """
    parameter_set = ParameterSet(name=parset_name)
    for name, value in zip(names, values):
        parameter = Parameter(name)
        parameter.setValue(value)
        parameter_set.addParameter(parameter)
    return parameter_set
