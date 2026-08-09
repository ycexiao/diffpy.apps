import numpy

from diffpy.apps.refinebase.refinement_session import RefinementSession


def test_refinement_session():
    # C1: Refinement session without additional calculator or functions
    session = RefinementSession()
    xobs = numpy.linspace(-numpy.pi, numpy.pi, 100)
    yobs = numpy.sin(xobs) + 0.1 * numpy.random.normal(size=xobs.shape)
    session.add_profile(name="profile", x=xobs, y=yobs)
    session.add_parameter(name="x", delegates_to="profile.x")
    session.set_profile_equation(profile="profile", expression="A*sin(a*x)")
    session.set_profile_weights(["profile"], [1.0])
    session.refine(name=["A", "a"], initial_values=[1.0, 0.5])

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
