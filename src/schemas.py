
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class InvoiceItem(BaseModel):

    description: Optional[str] = Field(
        default=None,
        description="Description of the product or service"
    )

    quantity: Optional[Decimal] = Field(
        default=None,
        description="Quantity of the item"
    )

    unit_price: Optional[Decimal] = Field(
        default=None,
        description="Price per unit"
    )

    total_amount: Optional[Decimal] = Field(
        default=None,
        description="Total price of this item"
    )


class InvoiceData(BaseModel):

    invoice_number: Optional[str] = None

    invoice_date: Optional[str] = None

    supplier_name: Optional[str] = None

    currency: Optional[str] = None

    items: list[InvoiceItem] = Field(
        default_factory=list
    )

    subtotal: Optional[Decimal] = None

    vat_amount: Optional[Decimal] = None

    vat_percentage: Optional[Decimal] = None

    total_amount: Optional[Decimal] = None
