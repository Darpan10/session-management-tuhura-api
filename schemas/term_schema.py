from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class TermBase(BaseModel):
    name: str
    start_date: date = Field(alias='startDate')
    end_date: date = Field(alias='endDate')
    year: Optional[int] = None  # Auto-calculated from start_date

    class Config:
        populate_by_name = True


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = Field(None, alias='startDate')
    end_date: Optional[date] = Field(None, alias='endDate')
    year: Optional[int] = None

    class Config:
        populate_by_name = True


class TermResponse(TermBase):
    id: int
    startDate: date = Field(alias='start_date')
    endDate: date = Field(alias='end_date')

    class Config:
        from_attributes = True
        populate_by_name = True
