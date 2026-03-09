from pydantic import BaseModel
from typing import Optional


class ExtractionResult(BaseModel):
    id: str
    product_line: Optional[str] = None
    origin_port_code: Optional[str] = None
    origin_port_name: Optional[str] = None
    destination_port_code: Optional[str] = None
    destination_port_name: Optional[str] = None
    incoterm: Optional[str] = None
    cargo_weight_kg: Optional[float] = None
    cargo_cbm: Optional[float] = None
    is_dangerous: Optional[bool] = None