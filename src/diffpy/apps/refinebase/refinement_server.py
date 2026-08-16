import uuid
from typing import Annotated

from mcp.server import MCPServer

from diffpy.apps.refinebase.refinement_session import RefinementSession

session = RefinementSession()
mcp = MCPServer("diffpy.apps")


@mcp.tool()
async def add_pdf_profile(
    profile_path: Annotated[str, "Path to the PDF profile file"],
    profile_name: Annotated[str, "Unique name for the profile"] = uuid.uuid4(),
) -> str:
    """Add a pdf profile to the refinement session."""
    from diffpy.apps.refinebase.util import (
        get_pdf_profile,
    )

    profile = get_pdf_profile(profile_path)
    session.add_profile(profile, profile_name=profile_name)
    return f"Profile {profile_name} added successfully."


@mcp.tool()
async def add_dat_profile(
    profile_path: Annotated[str, "Path to the .dat profile file"],
    profile_name: Annotated[str, "Unique name for the profile"] = uuid.uuid4(),
) -> str:
    """Add a profile to the refinement session.

    The profile should satisfy that
    xarray, yarray = np.loadtxt(profile_path)"""
    from diffpy.apps.refinebase.util import (
        get_dat_profile,
    )

    profile = get_dat_profile(profile_path)
    session.add_profile(profile, profile_name=profile_name)
    return f"Profile {profile_name} added successfully."


@mcp.tool()
def add_text_profile(
    xarray: Annotated[list, "X-values of the profile"],
    yarray: Annotated[list, "Y-values of the profile"],
    dx: Annotated[list, "Uncertainties in the x-values"] = None,
    dy: Annotated[list, "Uncertainties in the y-values"] = None,
    profile_name: Annotated[str, "Unique name for the profile"] = uuid.uuid4(),
) -> str:
    """Add a profile to the refinement session.

    The profile is constructed from the provided xarray and yarray data."""
    from diffpy.apps.refinebase.util import (
        get_text_profile,
    )

    profile = get_text_profile(xarray, yarray, dx=dx, dy=dy)
    session.add_profile(profile, profile_name=profile_name)
    return f"Profile {profile_name} added successfully."


@mcp.tool()
async def add_pdf_model(
    structure_path: Annotated[str, "Path to the structure file"],
    model_name: Annotated[str, "Name of the parametric model"] = uuid.uuid4(),
) -> str:
    """Add a PDF parametric model to the refinement session."""
    from diffpy.apps.refinebase.util import get_pdf_model

    pdf_model = get_pdf_model(structure_path=structure_path, name=model_name)
    pdf_model.prepare()
    session.add_model(pdf_model)
    return f"Model {pdf_model.name} added successfully."


@mcp.tool()
async def add_equation_model(
    equation: Annotated[str, "Equation for the parametric model"],
    model_name: Annotated[str, "Name of the parametric model"] = uuid.uuid4(),
) -> str:
    """Add an equation-based parametric model to the refinement session."""
    from diffpy.apps.refinebase.parametric_model import ParametricModel

    equation_model = ParametricModel(name=model_name)
    equation_model.set_equation(equation)
    equation_model.prepare()
    session.add_model(equation_model)
    return f"Model {equation_model.name} added successfully."


@mcp.tool()
async def list_profiles() -> list[str]:
    """List all profiles in the refinement session."""
    return [str(profile_id) for profile_id in session.profiles.keys()]


@mcp.tool()
async def list_models() -> list[str]:
    """List all models in the refinement session."""
    return [str(model_id) for model_id in session.models.keys()]


@mcp.tool()
async def set_model_equation(
    model_name: Annotated[str, "Name of the parametric model"],
    equation: Annotated[str, "Equation to set for the parametric model"],
) -> str:
    """Set or change the equation for a specific parametric model."""
    if model_name not in session.models:
        raise ValueError(f"Model with ID {model_name} does not exist.")

    model = session.models[model_name]
    model.set_equation(equation)
    model.prepare()  # Re-prepare the model after changing the equation

    return f"Equation for model {model_name} set successfully."


@mcp.tool()
async def combine_models(
    parent_model_name: Annotated[str, "Name of the parent parametric model"],
    child_model_name: Annotated[str, "Name of the child parametric model"],
    symbol: Annotated[
        str, "Symbol to use for child model in the parent model's equation"
    ],
) -> str:
    """
    Combine two parametric models by registering the child to the parent model.
    """
    if parent_model_name not in session.models:
        raise ValueError(
            f"Parent model with ID {parent_model_name} does not exist."
        )

    if child_model_name not in session.models:
        raise ValueError(
            f"Child model with ID {child_model_name} does not exist."
        )

    parent_model = session.models[parent_model_name]
    child_model = session.models[child_model_name]

    parent_model.register_submodel(symbol, child_model)
    parent_model.prepare()

    return (
        f"Models {parent_model_name} and "
        f"{child_model_name} combined successfully."
    )


@mcp.tool()
async def set_model_param_value(
    param_name: Annotated[str, "Name of the parameter to set"],
    value: Annotated[float, "Value to set for the parameter"],
) -> str:
    """
    Set the value of a specific parameter in a parametric model.
    """
    from diffpy.apps.refinebase.util import get_variable

    variable = get_variable(session.models, param_name)
    variable.setValue(value)

    return f"Parameter '{param_name}' is set to {value}."


@mcp.tool()
async def list_model_parameters(
    model_name: Annotated[str, "Name of the parametric model"],
) -> str:
    """
    List all parameters of a specific parametric model.
    """
    if model_name not in session.models:
        raise ValueError(f"Model with ID {model_name} does not exist.")

    model = session.models[model_name]
    parameters = {
        node_id: par.value for node_id, par in model.parameters.items()
    }
    return f"Parameters for model '{model_name}': {parameters}"


@mcp.tool()
async def get_model_value(
    model_name: Annotated[str, "Name of the parametric model"],
) -> str:
    """
    Get the value of a specific parametric model.
    """
    if model_name not in session.models:
        raise ValueError(f"Model with ID {model_name} does not exist.")

    model = session.models[model_name]
    value = model.evaluate()

    return f"Value for model '{model_name}': {value}"


@mcp.tool()
async def refine(
    profile_names: Annotated[
        list[str], "List of profile IDs to use in the refinement"
    ],
    model_names: Annotated[
        list[str], "List of model IDs to use in the refinement"
    ],
    variable_names: Annotated[list[str], "List of variable names to refine"],
    weights: Annotated[list[float], "List of weights for each profile"] = None,
    initial_values: Annotated[
        list[float], "List of initial values for each variable"
    ] = None,
) -> str:
    """
    Perform a refinement using the specified profiles, models, and variables.
    """
    # Retrieve profiles and models from session using provided IDs
    from diffpy.apps.refinebase.util import get_variable

    profile_objs = [session.profiles[pid] for pid in profile_names]
    model_objs = [session.models[mid] for mid in model_names]
    variable_objs = [
        get_variable(session.models, var_name) for var_name in variable_names
    ]

    # Perform refinement
    session.solve(
        profile_objs,
        model_objs,
        variable_objs,
        weights=weights,
        initial_values=initial_values,
    )

    # Collect refined variable values
    refined_values = {var.name: var.value for var in variable_objs}

    return (
        f"Refinement completed successfully. Refined values: {refined_values}"
    )


if __name__ == "__main__":
    mcp.run()
