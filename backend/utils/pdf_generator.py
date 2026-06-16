from __future__ import annotations

from datetime import datetime
from pathlib import Path


def generate_statement_pdf(customer_name: str, customer_id: str) -> str:
    output_dir = Path(__file__).resolve().parents[2] / "generated_documents"
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"{customer_id}_six_month_statement.pdf"
    text = (
        "%PDF-1.4\n"
        "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << >> >> endobj\n"
        f"4 0 obj << /Length 178 >> stream\nBT /F1 18 Tf 72 720 Td "
        f"(LifePulse Bank Statement) Tj 0 -32 Td ({customer_name} - {customer_id}) Tj "
        f"0 -32 Td (Digitally signed on {datetime.utcnow():%d %b %Y}) Tj ET\nendstream endobj\n"
        "xref\n0 5\n0000000000 65535 f \ntrailer << /Root 1 0 R /Size 5 >>\nstartxref\n420\n%%EOF\n"
    )
    path.write_text(text, encoding="latin-1")
    return str(path)
