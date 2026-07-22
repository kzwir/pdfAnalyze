# -*- coding: utf-8 -*-

# Jest zgodny z architekturą:
# BaseEngine
# tableimport.py
# parallel_pipeline.py
# pdf2word_module.py

# Silnik wykorzystuje:

# Tesseract OCR
# pytesseract
# pdf2image

# Działa jako fallback dla:
# PDF typu skan (OCR)
# PDF typu mieszany
# PDF, w których pozostałe silniki nie znalazły tabel.

# Wymagane pakiety
# Python
# pip install pytesseract
# pip install pdf2image
# pip install pillow
# Ubuntu
#   Tesseract
#       sudo apt install tesseract-ocr
#   Pakiet języka polskiego:
#       sudo apt install tesseract-ocr-pol
#   Poppler (wymagany przez pdf2image):
#       sudo apt install poppler-utils

# Test OCR
# Sprawdzenie Tesseract:
#   tesseract --versionPokaż więcej wierszy
# Sprawdzenie języków:
#   tesseract --list-langsPokaż więcej wierszy
# Powinieneś zobaczyć m.in.:
#   eng
#   pol

# Jeżeli pdfplumber i camelot nie zwrócą tabel, system automatycznie przejdzie do OCR. Dzięki temu pipeline obsługuje zarówno PDF tekstowe, jak i skany.


import logging

from .base_engine import BaseEngine


class OCREngine(BaseEngine):
    """
    Silnik OCR oparty o:
    - pdf2image
    - pytesseract

    Stosowany głównie dla:
    - skanów PDF
    - dokumentów mieszanych
    - fallback po pdfplumber/camelot
    """

    name = "ocr"

    def supports(self, pdf_type):
        """
        Określa czy silnik obsługuje dany typ PDF.
        """

        return pdf_type in [
            "skan (OCR)",
            "mieszany",
            "niejednoznaczny"
        ]

    def extract(self, pdf_path):
        """
        Ekstrakcja całego dokumentu.

        Zwraca:
        [
            {
                "page": 1,
                "data": [[tekst]]
            }
        ]
        """

        results = []

        try:

            images = self._pdf_to_images(pdf_path)

            for page_num, image in enumerate(images, start=1):

                try:

                    text = self._run_ocr(image)

                    results.append(
                        {
                            "page": page_num,
                            "data": [[text]]
                        }
                    )

                except Exception as e:
                    logging.error(
                        f"OCR: błąd strony {page_num}: {e}"
                    )

        except Exception as e:
            logging.error(
                f"OCR: błąd dokumentu '{pdf_path}': {e}"
            )

        return results

    def extract_page(self, pdf_path, page_num):
        """
        OCR pojedynczej strony.
        Wykorzystywane przez parallel_pipeline.py
        """

        try:

            from pdf2image import convert_from_path

            images = convert_from_path(
                pdf_path,
                first_page=page_num,
                last_page=page_num
            )

            if not images:
                return []

            text = self._run_ocr(images[0])

            return [
                [[text]]
            ]

        except Exception as e:

            logging.error(
                f"OCR extract_page({page_num}) błąd: {e}"
            )

            return []

    def _pdf_to_images(self, pdf_path):
        """
        Konwersja PDF -> obrazy.
        """

        from pdf2image import convert_from_path

        return convert_from_path(pdf_path)

    def _run_ocr(self, image):
        """
        Uruchamia Tesseract OCR.
        """

        import pytesseract

        text = pytesseract.image_to_string(
            image,
            lang="pol+eng"
        )

        return text.strip()

    def count_pages(self, pdf_path):
        """
        Liczba stron dokumentu.
        """

        try:

            images = self._pdf_to_images(pdf_path)

            return len(images)

        except Exception:

            return 0

    def get_document_info(self, pdf_path):
        """
        Informacje diagnostyczne.
        """

        try:

            pages = self.count_pages(pdf_path)

            return {
                "pages": pages,
                "engine": self.name
            }

        except Exception as e:

            logging.error(
                f"OCR get_document_info błąd: {e}"
            )

            return {
                "pages": 0,
                "engine": self.name
            }