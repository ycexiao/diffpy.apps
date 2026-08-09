from pathlib import Path

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
        parameter_set = _construct_parameterset(
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
        structure_mdel = RefinenableModel(name=parset_name)
        structure_mdel.model = stru
        structure_mdel.parameters = ParameterSet(name=parset_name)
        structure_mdel.parameters.addParameterSet(
            stru_diffpy_parset.getLattice()
        )
        for atom_parset in stru_diffpy_parset.getScatterers():
            structure_mdel.parameters.addParameterSet(atom_parset)
        return structure_mdel


def _construct_parameterset(names, values, parset_name):
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
