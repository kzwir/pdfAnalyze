# -*- coding: utf-8 -*-

# 1. przetwarzanie równoległe
# każda strona PDF:
#   osobny proces
#   osobny engine
#   osobny wynik
# fallback per strona: pdfplumber -> camelot -> ocr
# dla każdej strony osobno
# 3. trzy tryby
# tryb          funkcja             kiedy
# standard      run_parallel        większosc PDF
# chunking      chunked_parallel    bardzo duze PDF
# streaming     run_streaming       real-time
# STRUKTURA WYNIKU
# {
#  "page": 3,
#   "engine": "pdfplumber",
#   "tables": [...]
# }

import logging
from multiprocessing import Pool, cpu_count

from engines.pdfplumber_engine import PdfPlumberEngine
from engines.camelot_engine import CamelotEngine
from engines.ocr_engine import OCREngine


# LISTA SILNIKÓW (kolejność = fallback)
ENGINES = [
    PdfPlumberEngine(),
    CamelotEngine(),
    OCREngine()
]


# =========================
# PRZETWARZANIE POJEDYNCZEJ STRONY
# =========================
def process_page(args):
    """
    Przetwarza jedną stronę PDF:
    - próbuje różne silniki
    - zwraca pierwszy działający wynik
    """

    pdf_path, page_num, pdf_type = args

    for engine in ENGINES:

        if not engine.supports(pdf_type):
            continue

        try:
            logging.debug(f"Strona {page_num}: próba {engine.name}")

            tables = engine.extract_page(pdf_path, page_num)

            if tables:
                logging.info(
                    f"Strona {page_num}: {engine.name} znalazł {len(tables)} tabel"
                )

                return {
                    "page": page_num,
                    "engine": engine.name,
                    "tables": tables
                }

        except Exception as e:
            logging.error(f"Strona {page_num}, silnik {engine.name}: {e}")

    # brak wyników
    return {
        "page": page_num,
        "engine": None,
        "tables": []
    }


# =========================
# RÓWNOLEGŁY PIPELINE
# =========================
def run_parallel(pdf_path, pdf_type, pages, workers=None):
    """
    Główna funkcja równoległego przetwarzania PDF
    """

    workers = workers or min(cpu_count(), 4)

    logging.info("=== START PARALLEL PIPELINE ===")
    logging.info(f"Plik: {pdf_path}")
    logging.info(f"Strony: {pages}")
    logging.info(f"Workers: {workers}")

    args = [(pdf_path, page, pdf_type) for page in range(1, pages + 1)]

    results = []

    with Pool(workers) as pool:

        # imap_unordered = szybciej dla dużych plików
        for result in pool.imap_unordered(process_page, args):
            results.append(result)

    logging.info("=== KONIEC PARALLEL PIPELINE ===")

    return results


# =========================
# OPCJA CHUNKING (dla bardzo dużych PDF)
# =========================
def chunked_parallel(pdf_path, pdf_type, pages, chunk_size=5, workers=None):
    """
    Przetwarzanie w paczkach (chunking)
    zmniejsza zużycie RAM
    """

    workers = workers or min(cpu_count(), 4)

    logging.info("=== START CHUNKED PIPELINE ===")
    logging.info(f"Chunk size: {chunk_size}")

    results = []

    for start in range(1, pages + 1, chunk_size):

        end = min(start + chunk_size - 1, pages)

        logging.info(f"Chunk: strony {start}-{end}")

        args = [(pdf_path, page, pdf_type) for page in range(start, end + 1)]

        with Pool(workers) as pool:
            for result in pool.imap_unordered(process_page, args):
                results.append(result)

    logging.info("=== KONIEC CHUNKED PIPELINE ===")

    return results


# =========================
# WERSJA STREAMING (dla real-time)
# =========================
def run_streaming(pdf_path, pdf_type, pages, workers=None):
    """
    Streaming – zwraca wyniki na bieżąco
    """

    workers = workers or min(cpu_count(), 4)

    logging.info("=== START STREAMING PIPELINE ===")

    args = [(pdf_path, page, pdf_type) for page in range(1, pages + 1)]

    with Pool(workers) as pool:
        for result in pool.imap(process_page, args):
            yield result

    logging.info("=== KONIEC STREAMING PIPELINE ===")