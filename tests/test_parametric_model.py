import numpy
import pytest


def test_parametric_model_graph(nested_sine_model):
    model, submodel = nested_sine_model
    # C1: Create a nested parametric model
    # Expect the graph to be constructed correctly
    expected_parameters = ["main.A", "main.sub.a", "main.sub.x"]
    actual_parameters = list(model.parameters.keys())
    assert set(expected_parameters) == set(actual_parameters)
    expected_nodes = ["main", "main.A", "main.sub", "main.sub.a", "main.sub.x"]
    actual_nodes = list(model._graph.nodes)
    assert set(expected_nodes).issubset(set(actual_nodes))
    expected_edges = [
        ("main", "main.A"),
        ("main", "main.sub"),
        ("main.sub", "main.sub.a"),
        ("main.sub", "main.sub.x"),
    ]
    actual_edges = list(model._graph.edges)
    assert set(expected_edges) == set(actual_edges)


def test_parametric_model_parameter_access(nested_sine_model):
    # C1: Create a nested sine parametric model
    # Expect to models to share the same parameter obj
    model, submodel = nested_sine_model
    assert model.parameters["main.sub.a"] is submodel.parameters["sub.a"]


@pytest.mark.parametrize(
    "A, a, x, expected",
    [
        (1.0, 1.0, numpy.pi / 2, 1.0),
        (2.0, 2.0, numpy.pi / 4, 2.0),
        (1.0, 1.0, numpy.pi, 0.0),
    ],
)
def test_parametric_model_evaluation(nested_sine_model, A, a, x, expected):
    # C1: Create a nested sine parametric model
    # Expect the model to evaluate correctly
    model, submodel = nested_sine_model
    model.parameters["main.A"].value = A
    submodel.parameters["sub.a"].value = a
    submodel.parameters["sub.x"].value = x
    actual = model.evaluate()
    assert numpy.isclose(actual, expected, rtol=1e-6)


def test_parametric_model_constrain(ni_model):
    # C1: Constrain Ni with Fm-3m space group
    #   Expect structure parameters except a, Uiso_0 to be constrained
    # TODO: handle prepare stuff. It refreshes the 'constrained_or_constant'.
    ni_model.constrain_symmetry("Fm-3m")
    free_parnames = [
        "ni.phase.lattice.a",
        "ni.phase.lattice.alpha",
        "ni.phase.Ni0.Uiso",
        "ni.delta1",
        "ni.delta2",
        "ni.qbroad",
        "ni.scale",
        "ni.qdamp",
        "ni.phase.Ni0.occ",
        "ni.phase.Ni1.occ",
        "ni.phase.Ni2.occ",
        "ni.phase.Ni3.occ",
    ]
    for par_name in ni_model.parameters.keys():
        if par_name not in free_parnames:
            assert (
                ni_model._graph.nodes[par_name]["constrained_or_constant"]
                is True
            )
