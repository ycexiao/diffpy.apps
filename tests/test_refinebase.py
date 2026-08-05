from diffpy.srreal.pdfcalculator import PDFCalculator
from diffpy.apps.refinebase.refinement_session import RefinementSession
from diffpy.apps.refinebase.parsers import (
    ProfileParser,
    StructureParser,
    ParameterAdapter,
)


def test_refinement_session():
    profile_path = "tests/data/Ni.gr"
    structure_path = "tests/data/Ni.cif"
    profile_parset = ProfileParser(profile_path)
    structure_parset = StructureParser(structure_path)

    session = RefinementSession()
    session.addParameterSet(profile_parset)
    session.addParameterSet(structure_parset)
    session.addParameter(
        ParameterAdapter(
            name="g1", callable=lambda: PDFCalculator(structure_parset)[1]
        )
    )
    session.addParameter(ParameterAdapter(name="s1", value=1.0))
    session.register_loss_function(name="l1", expression="s1*g1")
    session.set_master_loss_function(name="l1")
    session.refine()
