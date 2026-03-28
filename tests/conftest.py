import importlib
import pytest


@pytest.fixture(autouse=True)
def reset_pvr_state():
    """Reload PlotVR before each test to reset global scene/state."""
    import PlotVR._plotvr
    import PlotVR
    importlib.reload(PlotVR._plotvr)
    importlib.reload(PlotVR)
    yield
