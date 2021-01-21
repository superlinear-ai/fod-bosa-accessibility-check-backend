"""The FastAPI models."""

from typing import List

from pydantic import BaseModel, Field

from .wcag.type_aliases import Infraction


class CheckURLData(BaseModel):
    """Data object containing the resources from the client page."""

    url: str = Field(
        ...,
        example="https://rdx201.kumulus.11ways.be/index.html",
        title="The URL to be checked",
    )
    window_width: int = Field(default=1920, example=1920, title="The width of the user's window")
    window_height: int = Field(default=1080, example=1080, title="The height of the user's window")


class ReturnedInfraction(BaseModel):
    """An infraction to return."""

    wcag_criterion: str = Field(..., example="WCAG_1_4_3", title="The WCAG criterion")
    xpath: str = Field(..., example="/html/body/textarea[1]", title="The xpath of the infraction")
    contrast: float = Field(..., example=1.683, title="The contrast ratio found in the infraction")
    contrast_threshold: float = Field(..., example=4.5, title="The expected minimal contrast ratio")


class ReturnedInfractions(BaseModel):
    """A list of infractions that is returned to the user."""

    errors: List[ReturnedInfraction] = Field(default=[], title="The detected infractions")

    @classmethod
    def create(cls, infractions: List[Infraction]) -> "ReturnedInfractions":
        """Create a Pydantic model of returned infractions, given a list of dict infractions."""
        returned_infractions = [ReturnedInfraction.parse_obj(infr) for infr in infractions]
        return ReturnedInfractions(errors=returned_infractions)
