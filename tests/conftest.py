import json
from pathlib import Path

import pytest
from diffpy.srfit.fitbase import (
    Profile,
)
from diffpy.srfit.pdf import PDFParser
from diffpy.structure import Structure

from diffpy.apps.refinebase.parametric_model import (
    ParametricModelPDF,
)


@pytest.fixture
def user_filesystem(tmp_path):
    base_dir = Path(tmp_path)
    home_dir = base_dir / "home_dir"
    home_dir.mkdir(parents=True, exist_ok=True)
    cwd_dir = base_dir / "cwd_dir"
    cwd_dir.mkdir(parents=True, exist_ok=True)

    home_config_data = {"username": "home_username", "email": "home@email.com"}
    with open(home_dir / "diffpyconfig.json", "w") as f:
        json.dump(home_config_data, f)

    yield tmp_path


@pytest.fixture
def nested_sine_model():
    from diffpy.apps.refinebase.parametric_model import ParametricModelEquation

    model = ParametricModelEquation("main", "A*sin(u)")
    submodel = ParametricModelEquation("sub", "a*x")
    model.register_submodel("u", submodel)
    return model, submodel


@pytest.fixture
def ni_model():
    profile_path = "tests/data/Ni.gr"
    profile = Profile()
    parser = PDFParser()
    parser.parse_file(profile_path)
    profile.load_parsed_data(parser)
    profile.set_calculation_range(xmax=20)
    stru = Structure()
    structure_path = "tests/data/Ni.cif"
    stru.read(structure_path)
    pdf_model = ParametricModelPDF("ni", structure=stru, meta=profile.meta)
    return pdf_model
