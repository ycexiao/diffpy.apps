from diffpy.apps.refinebase.refinable_model import (
    ParameterParser,
)


def test_parse_pdf():
    # C1: reading a valid .gr file
    #  Expect return  valid ParameterSet and meta data
    profile_path = "tests/data/Ni.gr"
    parser = ParameterParser()
    profile_model, meta = parser._parse_pdf(
        profile_path, parset_name="profile_parameterset"
    )
    expected_parameter_names = ["x", "y", "dx", "dy"]
    actual_parameter_names = [par.name for par in profile_model.parameters]
    assert set(actual_parameter_names) == set(expected_parameter_names)
    expected_meta = {
        "stype": "X",
        "qmin": 0.5,
        "qmax": 25.0,
        "filename": "tests/data/Ni.gr",
        "bank": 0,
        "nbanks": 1,
    }
    actual_meta = meta
    assert actual_meta == expected_meta


def test_parse_structure():
    # C1: reading a valid .cif file
    #  Expect return valid ParameterSet
    structure_path = "tests/data/Ni.cif"
    parser = ParameterParser()
    structure_model = parser._parse_structure(structure_path)
    expected_parameter_names = ["a", "b", "c", "alpha", "beta", "gamma"]
    actual_parameter_names = [
        name
        for name in structure_model.parameters._parsets[
            "lattice"
        ]._parameters.keys()
    ]
    assert set(actual_parameter_names) == set(expected_parameter_names)
    expected_atom_parameter_names = [
        "x",
        "y",
        "z",
        "Uiso",
        "Biso",
        "occ",
        "occupancy",
    ]
    expected_atom_parameter_names += [
        f"U{j+1}{k+1}" for j in range(3) for k in range(3)
    ]
    expected_atom_parameter_names += [
        f"B{j+1}{k+1}" for j in range(3) for k in range(3)
    ]
    for i in range(len(structure_model.model)):
        actual_atom_parameter_names = [
            name
            for name in structure_model.parameters._parsets[
                f"Ni{i}"
            ]._parameters.keys()
        ]
        assert set(actual_atom_parameter_names) == set(
            expected_atom_parameter_names
        )
