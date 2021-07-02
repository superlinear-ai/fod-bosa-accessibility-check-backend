"""The FastAPI backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .models import CheckURLData, ReturnedInfractions
from .version import __version__
from .wcag import detect_wcag_infractions

app = FastAPI(
    title="FOD BOSA's Accessibility Check: Backend API",
    description="This backend provides extra functionality to FOD BOSA's Accessibility Check tool.",
    version=__version__,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "POST", "PUT"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def redirect_to_docs() -> RedirectResponse:
    """Redirect the root url to the docs."""
    return RedirectResponse(url="/docs")


@app.post("/v1/check_url", response_model=ReturnedInfractions, response_model_exclude_unset=True)
async def check_url(data: CheckURLData) -> ReturnedInfractions:
    """Check the given URL.

    Parameters
    ----------
    data : CheckURLData
        The URL to be checked, and the user's window dimensions

    Returns
    -------
    Any
        The errors detected in the given URL
    """
    infractions = detect_wcag_infractions(data.url, data.window_width, data.window_height)
    return ReturnedInfractions(errors=infractions)
