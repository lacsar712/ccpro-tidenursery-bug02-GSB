from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

PondStatus = Literal["stocked", "dry", "quarantine"]


class PondCreate(BaseModel):
    hatchery_id: int = Field(..., alias="hatcheryId")
    pond_code: str = Field(..., min_length=1, max_length=64, alias="pondCode")
    species: str = Field(..., min_length=1, max_length=64)
    volume_m3: float = Field(..., gt=0, alias="volumeM3")
    status: PondStatus = "stocked"

    model_config = ConfigDict(populate_by_name=True)


class PondUpdate(BaseModel):
    hatchery_id: Optional[int] = Field(None, alias="hatcheryId")
    pond_code: Optional[str] = Field(None, min_length=1, max_length=64, alias="pondCode")
    species: Optional[str] = Field(None, min_length=1, max_length=64)
    volume_m3: Optional[float] = Field(None, gt=0, alias="volumeM3")
    status: Optional[PondStatus] = None

    model_config = ConfigDict(populate_by_name=True)


class PondOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    hatchery_id: int = Field(serialization_alias="hatcheryId")
    pond_code: str = Field(serialization_alias="pondCode")
    species: str
    volume_m3: float = Field(serialization_alias="volumeM3")
    status: PondStatus
