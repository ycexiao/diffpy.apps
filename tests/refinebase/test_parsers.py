from diffpy.apps.refinebase.parsers import (
    ParameterParser,
)


def test_parse_pdf():
    # C1: reading a valid .gr file
    #  Expect return  valid ParameterSet and meta data
    profile_path = "tests/data/Ni.gr"
    parser = ParameterParser()
    parameter_set, meta = parser._parse_pdf(
        profile_path, parset_name="profile_parameterset"
    )
    expected_parameter_names = ["x", "y", "dx", "dy"]
    actual_parameter_names = [
        name for name in parameter_set._parameters.keys()
    ]
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
    structure_parameterset = parser._parse_structure(structure_path)
    expected_lat_parameter_names = ["a", "b", "c", "alpha", "beta", "gamma"]
    actual_lat_parameter_names = [
        name for name in structure_parameterset.getLattice()._parameters.keys()
    ]
    assert set(actual_lat_parameter_names) == set(expected_lat_parameter_names)
    for i, atom in enumerate(structure_parameterset.getScatterers()):
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
        actual_atom_parameter_names = [
            name for name in atom._parameters.keys()
        ]
        assert set(actual_atom_parameter_names) == set(
            expected_atom_parameter_names
        )
