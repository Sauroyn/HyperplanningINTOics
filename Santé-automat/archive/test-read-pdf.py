import pdfplumber
import os

pdf_path = "pdfs/prisedesang.pdf"  # <-- remplace par le nom réel du fichier

if not os.path.exists(pdf_path):
    print(f"❌ Le fichier {pdf_path} n'existe pas.")
    exit()

with pdfplumber.open(pdf_path) as pdf:
    print(f"✅ PDF ouvert : {pdf_path}")
    print(f"Nombre de pages : {len(pdf.pages)}")
    print("─────────────────────────────")

    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        print(f"\n=== Page {i} ===")
        print(text)
        print("─────────────────────────────")
