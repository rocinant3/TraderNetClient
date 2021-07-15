from typing import Literal
from pydantic import BaseModel, Field, validator, ValidationError


class Ticker(BaseModel):
    market: Literal["MCX", "NASDAQ", "FIX"] = Field(..., alias="ltr")
    currency: str = Field('RUR', alias='x_curr')
    code_name: str = Field(..., alias="c")
    name_1: str = Field(..., alias="name")
    name_2: str = Field(..., alias='name2')
    last_price: float = Field(..., alias="ltp")
    name: str

    @validator("name", always=True, check_fields=True)
    def validate_name(cls, value, values):
        try:
            values.get("market")
        except KeyError:
            raise ValidationError
        return values["name_1"]
