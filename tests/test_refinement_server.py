import numpy
import pytest
from mcp import Client

from diffpy.apps.refinebase.refinement_server import mcp
from diffpy.apps.refinebase.util import get_variable


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_refine_sine():
    # C1: Set up the MCP client and do a sine refinement
    #   Expect all objs are created and refined successfully
    from diffpy.apps.refinebase.refinement_server import session

    async with Client(mcp, raise_exceptions=True) as mcp_client:
        await mcp_client.call_tool(
            "add_dat_profile",
            {
                "profile_name": "sine_profile",
                "profile_path": "tests/data/sine.dat",
            },
        )
        assert "sine_profile" in session.profiles
        await mcp_client.call_tool(
            "add_equation_model",
            {
                "model_name": "sine_model",
                "equation": "A*sin(x)",
            },
        )
        assert "sine_model" in session.models
        await mcp_client.call_tool(
            "set_model_param_value",
            {
                "param_name": "sine_model.A",
                "value": 0.8,
            },
        )
        variable_A = get_variable(session.models, "sine_model.A")
        expected_value = 0.8
        actual_value = variable_A.value
        assert actual_value == expected_value
        await mcp_client.call_tool(
            "refine",
            {
                "profile_names": ["sine_profile"],
                "model_names": ["sine_model"],
                "variable_names": ["sine_model.A"],
            },
        )
        expected_value = 1.0  # The expected value of A after refinement
        actual_value = variable_A.value
        assert numpy.isclose(actual_value, expected_value, rtol=0.2)
