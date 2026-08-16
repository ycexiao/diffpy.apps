def get_pdf_profile(profile_path: str):
    from diffpy.srfit.fitbase import Profile
    from diffpy.srfit.pdf import PDFParser

    profile = Profile()
    parser = PDFParser()
    parser.parseFile(profile_path)
    profile.loadParsedData(parser)
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


def get_variable(models_dict, variable_name):
    objs = variable_name.split(".")
    if objs[0] not in models_dict:
        raise ValueError(f"Model '{objs[0]}' not found in the session.")
    if variable_name not in models_dict[objs[0]].parameters:
        raise ValueError(
            f"Variable '{variable_name}' not found in the model '{objs[0]}'."
        )

    return models_dict[objs[0]].parameters[variable_name]


# if __name__ == "__main__":
# import numpy as np
# xarray = np.linspace(-2*np.pi, 2*np.pi, 400)
# yarray = np.sin(xarray) + 0.05*np.random.normal(size=len(xarray))
# X = np.stack((xarray,yarray), axis=1)
# np.savetxt("sine.dat",X)
