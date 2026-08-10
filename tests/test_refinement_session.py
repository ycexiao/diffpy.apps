import numpy

from diffpy.apps.refinebase.refinable_model import ParameterSetTree
from diffpy.apps.refinebase.refinement_session import RefinementSession


def test_refinement_session():
    # C1: Refinement session without additional calculator or functions
    session = RefinementSession()
    xobs = numpy.linspace(-numpy.pi, numpy.pi, 100)
    yobs = 2 * numpy.sin(2 * xobs) + 0.1 * numpy.random.normal(size=xobs.shape)
    session.add_case(
        name="sine_fit",
        x=xobs,
        y=yobs,
        expression="A*sin(a*x)",
        xname="x",
    )
    session.solve(
        case_names=["sine_fit"],
        case_weights=[1.0],
        var_names=["main.sine_fit.A", "main.sine_fit.a"],
        initial_values=[1.0, 1.0],
    )
    tree = ParameterSetTree(session.main_parameter_set).graph
    assert numpy.isclose(tree.nodes["main.sine_fit.A"]["parameter"].value, 1.0)
    assert numpy.isclose(tree.nodes["main.sine_fit.a"]["parameter"].value, 1.0)

    # C2: Refinement session with one PDFCalculator
    # parser = ParameterParser()
    # profile_path = "tests/data/Ni.gr"
    # structure_path = "tests/data/Ni.cif"
    # profile_model, profile_meta = parser._parse_pdf(profile_path)
    # structure_model = parser._parse_structure(structure_path)

    # session = RefinementSession()
    # session.addParameterSet(profile_model.parameters)
    # session.addParameterSet(structure_model.parameters)
    # session.addParameter(
    #     ParameterAdapter(
    #         name="g1",
    #         callable=lambda: PDFCalculator(structure_model.model)[1]
    #     )
    # )
    # session.addParameter(ParameterAdapter(name="s1", value=1.0))
    # session.register_loss_function(name="l1", expression="s1*g1")
    # session.set_master_loss_function(name="l1")
    # session.refine()
