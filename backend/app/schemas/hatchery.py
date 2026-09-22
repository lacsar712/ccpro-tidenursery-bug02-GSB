from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class HatcheryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    seawater_source: str = Field(..., min_length=1, max_length=128, alias="seawaterSource")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class HatcheryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    seawater_source: Optional[str] = Field(None, min_length=1, max_length=128, alias="seawaterSource")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class HatcheryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    seawater_source: str = Field(serialization_alias="seawaterSource")
    notes: Optional[str] = None
