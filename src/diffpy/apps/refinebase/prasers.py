class ProfileParser:
    """
    A ProfileParser class contains methods to parse profile files and
    generate parameters for refinement.
    """

    pass


class StructureParser:
    """
    A StructureParser class contains methods to parse structure files and
    generate parameters for refinement.
    """

    pass


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
