from pydantic import BaseModel, AwareDatetime, Field

class Echo(BaseModel):
    echo: str = Field(pattern=r"^[a-zA-Z]+$")
    time: AwareDatetime
