from diffpy.apps.refinebase.parsers import (
    ParameterAdapter,
    ParameterParser,
)
from diffpy.apps.refinebase.refinement_session import RefinementSession
from diffpy.srreal.pdfcalculator import PDFCalculator


def test_refinement_session():
    parser = ParameterParser()
    profile_path = "tests/data/Ni.gr"
    structure_path = "tests/data/Ni.cif"
    profile_parset, profile_meta = parser._parse_pdf(profile_path)
    structure_parset = parser._parse_structure(structure_path)

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
