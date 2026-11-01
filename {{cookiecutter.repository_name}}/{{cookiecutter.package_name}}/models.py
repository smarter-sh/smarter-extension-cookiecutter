"""The arguments and result of the {{ cookiecutter.tool_name }} tool."""

from pydantic import BaseModel, Field, JsonValue


class {{ cookiecutter.tool_class }}Arguments(BaseModel):
    """The arguments of {{ cookiecutter.tool_name }}."""

    query: str = Field(..., min_length=1, description="What to search for, e.g. 'solar eclipses in 2027'.")


class {{ cookiecutter.tool_class }}Result(BaseModel):
    """What {{ cookiecutter.tool_name }} returns to the LLM."""

    query: str = Field(..., description="The query that was searched for.")
    results: list[JsonValue] = Field(..., description="The service's results, as it returned them.")
