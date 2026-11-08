from decimal import Decimal

from src.schemas import InvoiceData, InvoiceItem
from src.validator import validate_invoice


def make_invoice(**overrides):
    values = {
        "invoice_number": "RT-2024-1052",
        "invoice_date": "14 October 2024",
        "supplier_name": "Rivertech Supplies Ltd.",
        "currency": "NPR",
        "items": [
            InvoiceItem(
                description="HDPE Pipe 110mm",
                quantity=Decimal("50"),
                unit_price=Decimal("1250"),
                total_amount=Decimal("62500"),
            ),
            InvoiceItem(
                description="Other invoice items",
                quantity=Decimal("1"),
                unit_price=Decimal("38000"),
                total_amount=Decimal("38000"),
            ),
        ],
        "subtotal": Decimal("100500"),
        "vat_amount": Decimal("13065"),
        "vat_percentage": Decimal("13"),
        "total_amount": Decimal("113565"),
    }
    values.update(overrides)
    return InvoiceData(**values)


def test_valid_invoice_passes():
    result = validate_invoice(make_invoice())
    assert result == {"is_valid": True, "errors": [], "warnings": []}


def test_incorrect_item_calculation_is_an_error():
    invoice = make_invoice(
        items=[
            InvoiceItem(
                description="Incorrect item",
                quantity=Decimal("2"),
                unit_price=Decimal("10"),
                total_amount=Decimal("15"),
            )
        ],
        subtotal=Decimal("15"),
        vat_amount=Decimal("0"),
        vat_percentage=Decimal("0"),
        total_amount=Decimal("15"),
    )

    result = validate_invoice(invoice)

    assert result["is_valid"] is False
    assert any("Item 1" in error for error in result["errors"])


def test_missing_data_is_reported_without_false_subtotal_error():
    invoice = make_invoice(
        items=[
            InvoiceItem(
                description="Incomplete item",
                quantity=None,
                unit_price=Decimal("10"),
                total_amount=None,
            )
        ]
    )

    result = validate_invoice(invoice)

    assert result["is_valid"] is True
    assert any("incomplete" in warning for warning in result["warnings"])
