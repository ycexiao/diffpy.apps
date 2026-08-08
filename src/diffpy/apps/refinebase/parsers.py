from pathlib import Path

from diffpy.srfit.fitbase.parameter import Parameter
from diffpy.srfit.fitbase.parameterset import ParameterSet
from diffpy.srfit.pdf.pdfparser import PDFParser
from diffpy.srfit.structure import struToParameterSet
from diffpy.structure import Structure


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
        parameter_values = parser.getData()
        parameter_names = ["x", "y", "dx", "dy"]
        parameter_set = _construct_parameterset(
            parameter_names, parameter_values, parset_name
        )
        meta = dict(parser.getMetaData())
        return parameter_set, meta

    def _parse_structure(self, structure_file: str):
        if not Path(structure_file).exists():
            raise FileNotFoundError(
                self.MISSING_FILE_WARNING.format(
                    description="Structure", file=structure_file
                )
            )
        stru = Structure()
        stru.read(structure_file)
        structure_parameterset = struToParameterSet(
            "structure_parameterset", stru
        )
        return structure_parameterset


class ParameterAdapter:
    """
    A ParameterAdapter class contains methods to adapt parameters of
    variables format to the standard format used in diffpy
    """

    def __init__(self):
        pass

    def _adapt_string(self, parameter: str):
        pass

    def _adapt_code(self, function_code: str):
        pass

    def _adapt_special(self, special_parameter: str):
        pass

    def _adapt_structure_file(self, phase_file: str):
        pass

    def _adapt_profile_file(self, profile_file: str):
        pass


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
