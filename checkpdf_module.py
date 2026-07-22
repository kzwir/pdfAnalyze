# -*- coding: utf-8 -*-

# 1. Sprawdza plik PDF
#       czy plik jest PDF
#       ile ma stron
#       czy jest zaszyfrowany
# 2. analizuje zawartosc
#       dlugosc tekstu
#       liczba obrazow
#       liczba tabel
# 3. Klasyfikuje PDF
#   typ             znaczenie
#   tekstowy        normalny PDF
#   tabelaryczny    ma tabele
#   skan            OCR potrzebny
#   mieszany        hybryda
#   uszkodzony      blad
# 4. Zwraca wynik (API)
#
# PRZYKŁADOWY OUTPUT
# {
#  "file": "0.pdf",
#   "valid_pdf": true,
#   "pages": 1,
#   "type": "tekstowy tabelaryczny",
#   "recommended_tool": "pdfplumber / camelot"
# }


import os
import logging

import pdfplumber
import pypdf as PyPDF2

logger = logging.getLogger(__name__)


# 1. WALIDACJA PDF
def check_pdf_validity(path):
    """
    Sprawdza czy plik jest poprawnym PDF i zwraca:
    (True/False, liczba stron / błąd, czy zaszyfrowany)
    """
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)

            pages = len(reader.pages)
            encrypted = reader.is_encrypted

            return True, pages, encrypted

    except Exception as e:
        logger.error(f"Blad walidacji PDF: {e}")
        return False, str(e), False


# 2. ANALIZA ZAWARTOSCI
def analyze_pdf(path, max_pages=3):
    """
    Analizuje pierwsze strony PDF:
    - ilosc tekstu
    - ilosc obrazow
    - ilosc tabel
    """

    text_len = 0
    images = 0
    tables = 0

    try:
        with pdfplumber.open(path) as pdf:

            pages = min(len(pdf.pages), max_pages)

            for i in range(pages):
                page = pdf.pages[i]

                # tekst
                text = page.extract_text()
                if text:
                    text_len += len(text.strip())

                # obrazy (heurystyka OCR)
                images += len(page.images)

                # tabele
                try:
                    extracted_tables = page.extract_tables()
                    if extracted_tables:
                        tables += len(extracted_tables)
                except Exception:
                    pass

        return {
            "text_len": text_len,
            "images": images,
            "tables": tables
        }

    except Exception as e:
        logger.error(f"Blad analizy PDF: {e}")
        return None


# 3. KLASYFIKACJA PDF
def classify(info, encrypted):
    """
    Określa typ PDF i sugerowany silnik
    """

    if info is None:
        return "uszkodzony", "brak przetwarzania"

    text = info["text_len"]
    images = info["images"]
    tables = info["tables"]

    # priorytet: zabezpieczenie
    if encrypted:
        return "zabezpieczony", "pypdf / qpdf"

    # skan (brak tekstu, sa obrazy)
    if text == 0 and images > 0:
        return "skan (OCR)", "ocr"

    # tekstowy + tabela
    if text > 100 and images == 0:
        if tables > 0:
            return "tekstowy tabelaryczny", "pdfplumber / camelot"
        return "tekstowy", "pdfplumber"

    # mieszany
    if text > 100 and images > 0:
        return "mieszany", "pdfplumber + OCR"

    # tylko tabele
    if tables > 0:
        return "tabelaryczny (slaba jakosc)", "camelot"

    return "niejednoznaczny", "manualna analiza"


# 4. GLOWNA FUNKCJA (API)
def analyze_file(path):
    """
    Glowne API do analizy pliku PDF
    Zwraca slownik uzywany w calym pipeline
    """

    result = {
        "file": path,
        "exists": os.path.exists(path),
        "valid_pdf": False,
        "encrypted": False,
        "pages": 0,
        "analysis": {},
        "type": None,
        "recommended_tool": None
    }

    # brak pliku
    if not result["exists"]:
        result["type"] = "brak_pliku"
        logger.error(f"Plik nie istnieje: {path}")
        return result

    # walidacja PDF
    valid, pages_or_error, encrypted = check_pdf_validity(path)

    if not valid:
        result["type"] = "uszkodzony"
        logger.error(f"Bledny PDF: {pages_or_error}")
        return result

    result["valid_pdf"] = True
    result["pages"] = pages_or_error
    result["encrypted"] = encrypted

    # analiza zawartości
    info = analyze_pdf(path)
    result["analysis"] = info

    # klasyfikacja
    pdf_type, tool = classify(info, encrypted)

    result["type"] = pdf_type
    result["recommended_tool"] = tool

    logger.info(f"Analiza PDF: {result}")

    return result


# 5. CLI (opcjonalne uruchomienie standalone)
def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Analiza PDF")
    parser.add_argument("--input", required=True)

    args = parser.parse_args()

    logger.basicConfig(level=logger.INFO)

    result = analyze_file(args.input)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()