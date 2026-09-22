from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WaterSampleCreate(BaseModel):
    pond_id: int = Field(..., alias="pondId")
    sampled_at: datetime = Field(..., alias="sampledAt")
    temp_c: float = Field(..., alias="tempC")
    salinity_ppt: float = Field(..., alias="salinityPpt")
    do_mg_l: float = Field(..., alias="doMgL")
    ph: float
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("do_mg_l")
    @classmethod
    def validate_do(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("溶解氧 doMgL 必须大于 0")
        return v

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: float) -> float:
        if v < 6 or v > 9:
            raise ValueError("pH 必须在 6 到 9 之间")
        return v


class WaterSampleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    pond_id: int = Field(serialization_alias="pondId")
    sampled_at: datetime = Field(serialization_alias="sampledAt")
    temp_c: float = Field(serialization_alias="tempC")
    salinity_ppt: float = Field(serialization_alias="salinityPpt")
    do_mg_l: float = Field(serialization_alias="doMgL")
    ph: float
    notes: Optional[str] = None
