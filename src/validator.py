
from decimal import Decimal
from src.schemas import InvoiceData


# Allow small rounding differences
TOLERANCE = Decimal("0.02")


def close_enough(first, second):
    return abs(first - second) <= TOLERANCE


def validate_invoice(invoice: InvoiceData):

    errors = []
    warnings = []

    # 1. Check required invoice fields
    if not invoice.invoice_number:
        warnings.append("Invoice number is missing.")

    if not invoice.invoice_date:
        warnings.append("Invoice date is missing.")

    if not invoice.supplier_name:
        warnings.append("Supplier name is missing.")

    if invoice.total_amount is None:
        errors.append("Grand total is missing.")

    # 2. Validate individual invoice items
    calculated_subtotal = Decimal("0")
    complete_item_count = 0

    for index, item in enumerate(invoice.items, start=1):

        if item.quantity is None:
            warnings.append(
                f"Item {index}: Quantity is missing."
            )
            continue

        if item.unit_price is None:
            warnings.append(
                f"Item {index}: Unit price is missing."
            )
            continue

        if item.total_amount is None:
            warnings.append(
                f"Item {index}: Total amount is missing."
            )
            continue

        complete_item_count += 1
        expected_total = item.quantity * item.unit_price

        if not close_enough(
            expected_total,
            item.total_amount
        ):
            errors.append(
                f"Item {index}: Expected {expected_total}, "
                f"but extracted {item.total_amount}."
            )

        calculated_subtotal += item.total_amount

    # 3. Validate subtotal
    if invoice.subtotal is not None:

        if invoice.items and complete_item_count == len(invoice.items):

            if not close_enough(
                calculated_subtotal,
                invoice.subtotal
            ):
                errors.append(
                    f"Subtotal mismatch: calculated "
                    f"{calculated_subtotal}, "
                    f"extracted {invoice.subtotal}."
                )
        elif invoice.items:
            warnings.append(
                "Subtotal could not be fully checked because one or more "
                "items are incomplete."
            )

    else:
        warnings.append("Subtotal is missing.")

    # 4. Validate VAT
    if (
        invoice.subtotal is not None
        and invoice.vat_percentage is not None
        and invoice.vat_amount is not None
    ):

        expected_vat = (
            invoice.subtotal
            * invoice.vat_percentage
            / Decimal("100")
        )

        if not close_enough(
            expected_vat,
            invoice.vat_amount
        ):
            warnings.append(
                f"VAT discrepancy: expected approximately "
                f"{expected_vat}, extracted "
                f"{invoice.vat_amount}."
            )

    # 5. Validate grand total
    if (
        invoice.subtotal is not None
        and invoice.vat_amount is not None
        and invoice.total_amount is not None
    ):

        expected_grand_total = (
            invoice.subtotal + invoice.vat_amount
        )

        if not close_enough(
            expected_grand_total,
            invoice.total_amount
        ):
            errors.append(
                f"Grand total mismatch: calculated "
                f"{expected_grand_total}, extracted "
                f"{invoice.total_amount}."
            )

    # Final validation result
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }
