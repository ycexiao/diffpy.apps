def get_pdf_profile(profile_path: str):
    from diffpy.srfit.fitbase import Profile
    from diffpy.srfit.pdf import PDFParser

    profile = Profile()
    parser = PDFParser()
    parser.parse_file(profile_path)
    profile.load_parsed_data(parser)
    return profile


def get_dat_profile(profile_path: str):
    from diffpy.srfit.fitbase import Profile

    profile = Profile()
    profile.loadtxt(profile_path)

    return profile


def get_text_profile(xarray, yarray, dx=None, dy=None):
    from diffpy.srfit.fitbase import Profile

    profile = Profile()
    profile.setObservedProfile(xarray, yarray, dx=dx, dy=dy)

    return profile


def get_pdf_model(structure_path: str, name="pdf"):
    from diffpy.structure import Structure

    from diffpy.apps.refinebase.parametric_model import ParametricModelPDF

    stru = Structure()
    stru.read(structure_path)
    pdf_model = ParametricModelPDF(name, structure=stru)
    return pdf_model
