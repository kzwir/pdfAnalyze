# engines/pdfplumber_engine.py

# Ten silnik jest obecnie Twoim domyślnym i podstawowym silnikiem ekstrakcji, używanym dla:
# PDF tekstowych,
# PDF tabelarycznych,
# PDF mieszanych (przed fallback do OCR),
# równoległego przetwarzania stron.

# Jest zgodny z wcześniejszą architekturą:
# dziedziczy po BaseEngine
# obsługuje ekstrakcję całego dokumentu
# obsługuje ekstrakcję pojedynczej strony (parallel_pipeline.py)
# loguje błędy
# zwraca spójny format danych dla tableimport.py i pdf2word_module.py

import pdfplumber
from .base_engine import BaseEngine


class PdfPlumberEngine(BaseEngine):
    name = "pdfplumber"

    def supports(self, pdf_type):
        return pdf_type in ["tekstowy", "tekstowy tabelaryczny", "mieszany"]

    def extract(self, pdf_path):
        tables_out = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()

                if tables:
                    for t in tables:
                        tables_out.append({
                            "page": page_num,
                            "data": t
                        })

        return tables_out

    def extract_page(self, pdf_path, page_num):
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num - 1]
            tables = page.extract_tables()

        return tables if tables else []