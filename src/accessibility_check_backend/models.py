"""The FastAPI models."""

from typing import List, Optional

from pydantic import BaseModel, Field

from .wcag.type_aliases import Infraction


class CheckURLData(BaseModel):
    """Data object containing the resources from the client page."""

    url: str = Field(
        ...,
        example="https://eid.belgium.be/fr",
        title="The URL to be checked",
    )
    window_width: int = Field(default=1920, example=1920, title="The width of the user's window")
    window_height: int = Field(default=1080, example=1080, title="The height of the user's window")


class ReturnedInfraction(BaseModel):
    """An infraction to return."""

    wcag_criterion: str = Field(..., example="WCAG_1_4_3", title="The WCAG criterion")
    xpath: str = Field(..., example="/html/body/textarea[1]", title="The xpath of the infraction")

    # WCAG 1.4.3 and 1.4.11
    contrast: Optional[float] = Field(
        None, example=1.683, title="The contrast ratio found in the infraction"
    )
    contrast_threshold: Optional[float] = Field(
        None, example=4.5, title="The expected minimal contrast ratio"
    )

    # WCAG 3.1.1 and 3.1.2
    html_language: Optional[str] = Field(
        None, example="en-US", title="The language as defined by the web page"
    )
    predicted_language: Optional[str] = Field(
        None, example="nl", title="The language of the web page we predict"
    )


class ReturnedInfractions(BaseModel):
    """A list of infractions that is returned to the user."""

    errors: List[ReturnedInfraction] = Field(default=[], title="The detected infractions")

    @classmethod
    def create(cls, infractions: List[Infraction]) -> "ReturnedInfractions":
        """Create a Pydantic model of returned infractions, given a list of dict infractions."""
        returned_infractions = [ReturnedInfraction.parse_obj(infr) for infr in infractions]
        return ReturnedInfractions(errors=returned_infractions)
