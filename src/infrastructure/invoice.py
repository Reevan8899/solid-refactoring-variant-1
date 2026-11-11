from io import BytesIO

from reportlab.pdfgen import canvas


class PdfInvoiceGenerator:
    def __init__(self, invoices: dict[int, bytes]):
        self.invoices = invoices

    def generate(self, order: dict) -> None:
        target = BytesIO()
        document = canvas.Canvas(target, invariant=1)
        document.drawString(72, 760, f"Order #{order['id']}")
        document.drawString(72, 738, f"Total: {order['total']:.2f}")
        document.save()
        self.invoices[order["id"]] = target.getvalue()
