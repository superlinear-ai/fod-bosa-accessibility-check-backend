"""The FastAPI models."""

from typing import List, Union

from pydantic import BaseModel, Field


class CheckURLData(BaseModel):
    """Data object containing the resources from the client page."""

    url: str = Field(
        ...,
        example="https://eid.belgium.be/fr",
        title="The URL to be checked",
    )
    window_width: int = Field(default=1920, example=1920, title="The width of the user's window")
    window_height: int = Field(default=1080, example=1080, title="The height of the user's window")


class BaseInfraction(BaseModel):
    """An infraction."""

    wcag_criterion: str = Field(..., example="WCAG_1_4_3", title="The WCAG criterion")
    xpath: str = Field(..., example="/html/body/textarea[1]", title="The xpath of the infraction")


class ContrastInfraction(BaseInfraction):
    """An infraction against WCAG 1.4.3 or 1.4.11."""

    contrast: float = Field(..., example=1.6839, title="The contrast ratio found in the infraction")
    contrast_threshold: float = Field(..., example=4.5, title="The expected minimal contrast ratio")


class LanguageInfraction(BaseInfraction):
    """An infraction against WCAG 3.1.1 or 3.1.2."""

    html_language: str = Field(
        ..., example="en", title="The language of the web page or element as defined by the HTML"
    )
    predicted_language: str = Field(
        ..., example="nl", title="The language that we predict the web page or element is in"
    )
    text: str = Field(
        ..., example="this is an example text", title="The text found to be in the wrong language"
    )


class AltTextInfraction(BaseInfraction):
    """An infraction against WCAG 1.1.1."""

    text: str = Field(..., title="The alt text of the image")
    type: int = Field(..., title="Error (1) or warning (2)")


Infraction = Union[ContrastInfraction, LanguageInfraction, AltTextInfraction]


class ReturnedInfractions(BaseModel):
    """A list of infractions that is returned to the user."""

    errors: List[Infraction] = Field(default=[], title="The detected infractions")
