import numpy

from diffpy.apps.refinebase.parametric_model import (
    ParametricModelEquation,
)
from diffpy.apps.refinebase.refinement_session import RefinementSession


def test_refine_sine(nested_sine_model, sine_profile):
    # C1: Refinement session without additional calculator or functions
    sine_model, submodel = nested_sine_model
    session = RefinementSession()
    session._solve(
        profiles=[sine_profile],
        models=[sine_model],
        variables=[
            sine_model.parameters["main.A"],
            sine_model.parameters["main.sub.a"],
        ],
        initial_values=[0.8, 0.5],
    )
    assert numpy.isclose(
        sine_model.parameters["main.A"].value,
        1.0,
        rtol=1e-2,
    )
    assert numpy.isclose(
        sine_model.parameters["main.sub.a"].value,
        1.0,
        rtol=1e-2,
    )


def test_refine_ni(ni_pdf_model, ni_pdf_profile, ni_refined_parameters):
    # C1: Refine Ni example
    #  Expect the refined parameters are close to the ones
    #  obtained using diffpy.srfit script
    ni_pdf_model.process_meta_data(ni_pdf_profile.meta)
    ni_pdf_model.constrain_symmetry("Fm-3m")
    ni_model = ParametricModelEquation(name="ni", equation_str="s*pdf")
    ni_model.register_submodel(ni_pdf_model, symbol="pdf")
    session = RefinementSession()
    session._solve(
        profiles=[ni_pdf_profile],
        models=[ni_model],
        variables=[
            ni_pdf_model.parameters["pdf.phase.lattice.a"],
            ni_model.parameters["ni.s"],
            ni_pdf_model.parameters["pdf.phase.Ni0.Uiso"],
            ni_pdf_model.parameters["pdf.delta2"],
            ni_pdf_model.parameters["pdf.qdamp"],
            ni_pdf_model.parameters["pdf.qbroad"],
        ],
        initial_values=[
            3.52,
            0.4,
            0.005,
            2,
            0.04,
            0.02,
        ],
    )
    name_to_cmi_name = {
        "ni.s": "s0",
        "ni.pdf.phase.lattice.a": "G1_a",
        "ni.pdf.phase.Ni0.Uiso": "G1_Uiso_0",
        "ni.pdf.delta2": "G1_delta2",
        "ni.pdf.qdamp": "qdamp",
        "ni.pdf.qbroad": "qbroad",
    }
    for name, cmi_name in name_to_cmi_name.items():
        assert numpy.isclose(
            ni_model.parameters[name].value,
            ni_refined_parameters[cmi_name],
            rtol=1e-2,
        )
