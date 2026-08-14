import numpy
from diffpy.srfit.fitbase import (
    Profile,
)
from diffpy.srfit.pdf import PDFParser
from diffpy.structure import Structure

from diffpy.apps.refinebase.parametric_model import (
    ParametricModel,
    ParametricModelPDF,
)
from diffpy.apps.refinebase.refinement_session import RefinementSession


def test_refine_sine():
    # C1: Refinement session without additional calculator or functions
    session = RefinementSession()
    xobs = numpy.linspace(-numpy.pi, numpy.pi, 100)
    yobs = numpy.sin(xobs) + 1e-2 * numpy.random.normal(size=xobs.shape)
    sine_profile = Profile()
    sine_profile.setObservedProfile(xobs, yobs)
    sine_model = ParametricModel("sine_model")
    sine_model.set_equation("A*sin(a*x)")
    sine_model.prepare()
    session.solve(
        profiles=[sine_profile],
        models=[sine_model],
        variables=[
            sine_model.parameters["sine_model.A"],
            sine_model.parameters["sine_model.a"],
        ],
        initial_values=[0.5, 0.5],
    )
    assert numpy.isclose(
        sine_model.parameters["sine_model.A"].value,
        1.0,
        rtol=1e-2,
    )
    assert numpy.isclose(
        sine_model.parameters["sine_model.a"].value,
        1.0,
        rtol=1e-2,
    )


def test_refine_ni():
    # C1: Refinement session with one PDFCalculator
    profile_path = "tests/data/Ni.gr"
    profile = Profile()
    parser = PDFParser()
    parser.parseFile(profile_path)
    profile.loadParsedData(parser)
    profile.setCalculationRange(xmax=20)
    stru = Structure()
    structure_path = "tests/data/Ni.cif"
    stru.read(structure_path)

    pdf_model = ParametricModelPDF("pdf", structure=stru, meta=profile.meta)
    pdf_model.prepare()
    ni_model = ParametricModel("ni_model")
    ni_model.register_submodel("g", pdf_model)
    ni_model.set_equation("s*g")
    ni_model.prepare()

    ni_model.parameters["ni_model.s"].value = 1.0

    session = RefinementSession()
    session.solve(
        profiles=[profile],
        models=[ni_model],
        variables=[
            ni_model.parameters["ni_model.s"],
            pdf_model.parameters["pdf.phase.lattice.a"],
        ],
    )
