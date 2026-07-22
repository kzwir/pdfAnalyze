# -*- coding: utf-8 -*-

# 1. Plugin system
#   Obsluguje silniki:
#   pdfplumber
#   camelot
#   ocr (Tesseract)
# 2. Fallback
#   pdfplumber -> camelot -> ocr
# 3. Tryb rownolegly dla duzych PDF:
#       run_parallel()
# 4. Metryki
#    {
#     "tables_total": X,
#     "tables_valid": Y,
#     "engine": "pdfplumber"
#   }
# 5. Obsługiwane tryby
# tryb              działanie
# auto              wybor silnika
# forced_engine     wymuszenie
# parallel          multiprocessing

# normalnie
#   python3 tableimport.py --input 0.pdf --template szablon.docx --output wynik.docx
# wymuszenie OCR
#   --engine ocr
# parallel
#   --parallel --pages 20

import logging

from engines.pdfplumber_engine import PdfPlumberEngine
from engines.camelot_engine import CamelotEngine
from engines.ocr_engine import OCREngine

from pdf2word_module import (create_document,process_tables_to_word,save_document)


from parallel_pipeline import run_parallel

logger = logging.getLogger(__name__)


# =========================
# ENGINE MANAGER (PLUGIN SYSTEM)
# =========================
class EngineManager:

    def __init__(self):
        self.engines = [
            PdfPlumberEngine(),
            CamelotEngine(),
            OCREngine()
        ]

    def get_supported_engines(self, pdf_type):
        return [e for e in self.engines if e.supports(pdf_type)]

    def get_engine_by_name(self, name):
        for e in self.engines:
            if e.name == name:
                return e
        return None

    def run_with_fallback(self, pdf_path, pdf_type):
        """
        fallback: pdfplumber → camelot → ocr
        """

        for engine in self.get_supported_engines(pdf_type):

            logger.info(f"Próba silnika: {engine.name}")

            try:
                tables = engine.extract(pdf_path)

                if tables:
                    logger.info(
                        f"Silnik {engine.name} znalazł {len(tables)} tabel"
                    )
                    return tables, engine.name

            except Exception as e:
                logger.error(f"Silnik {engine.name} błąd: {e}")

        logger.warning("Fallback nie znalazł tabel")
        return [], None


# =========================
# WALIDACJA TABEL
# =========================
def is_valid_table(table):
    try:
        rows = len(table["data"])
        cols = max(len(r) for r in table["data"] if r)
        return rows > 1 and cols > 1
    except Exception:
        return False


# =========================
# GŁÓWNY PIPELINE Z METRYKAMI
# =========================
def run_pipeline_with_metrics(
    pdf_path,
    template_path,
    output_path,
    pdf_type,
    pages=1,
    forced_engine="auto",
    parallel=False,
    document=None
):
    """
    Główna funkcja przetwarzania PDF
    """

    manager = EngineManager()

    logger.info("tableimport.py: run_pipeline_with_metrics")
    logger.info("=== START PIPELINE ===")
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Typ PDF: {pdf_type}")
    logger.info(f"Tryb równoległy: {parallel}")

    # WYBÓR SILNIKA
    if forced_engine != "auto":
        engine = manager.get_engine_by_name(forced_engine)

        if not engine:
            logger.error(f"Nieznany silnik: {forced_engine}")
            return {"tables_total": 0, "tables_valid": 0, "engine": None}

        logger.info(f"Wymuszony silnik: {engine.name}")

        tables = engine.extract(pdf_path)
        engine_name = engine.name

    else:
        # PARALLEL vs SEQUENTIAL
        if parallel and pages > 1:
            logger.info("Tryb: parallel pipeline")

            results = run_parallel(pdf_path, pdf_type, pages)

            tables = []
            engine_usage = {}

            for r in results:
                tables.extend([{"page": r["page"], "data": t} for t in r["tables"]])

                if r["engine"]:
                    engine_usage[r["engine"]] = engine_usage.get(r["engine"], 0) + 1

            # wybór dominującego engine
            engine_name = max(engine_usage, key=engine_usage.get) if engine_usage else None

        else:
            logger.info("Tryb: fallback sequential")

            tables, engine_name = manager.run_with_fallback(pdf_path, pdf_type)

    # ZAPIS DO WORD
    # utworzenie dokumentu, dodanie zawartości PDF, zapis dokumentu
    
    own_document = False

    if document is None:

        document = create_document(template_path)
        own_document = True

    process_result = process_tables_to_word(
        tables=tables,
        document=document,
        source_name=pdf_path
    )

    # METRYKI
    tables_total = process_result.get("tables", len(tables))
    tables_valid = process_result.get("tables_valid",0)

    logger.info(f"Tabele: {tables_total}, poprawne: {tables_valid}")

    if own_document:
        save_document(document,output_path)


    logger.info("=== KONIEC PIPELINE ===")

    return {
        "tables_total": tables_total,
        "tables_valid": tables_valid,
        "engine": engine_name
    }


# =========================
# PROSTY PIPELINE (bez metryk)
# =========================
def run_pipeline(pdf_path, template_path, output_path, pdf_type):
    return run_pipeline_with_metrics(
        pdf_path,
        template_path,
        output_path,
        pdf_type
    )


# =========================
# CLI
# =========================
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Pipeline PDF → Word (plugin engines)"
    )

    parser.add_argument("--input", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--output", required=True)

    parser.add_argument("--engine", default="auto")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--pages", type=int, default=1)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    run_pipeline_with_metrics(
        pdf_path=args.input,
        template_path=args.template,
        output_path=args.output,
        pdf_type="auto",
        pages=args.pages,
        forced_engine=args.engine,
        parallel=args.parallel
    )


if __name__ == "__main__":
    main()