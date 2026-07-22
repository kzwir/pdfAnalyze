# -*- coding: utf-8 -*-

# "klasycznie"
# python3 glowny.py --input 0.pdf --template szablon.docx --output wynik.docx

# automatycznie
# python3 glowny.py --input a.pdf --template t.docx --output out.docx

# wymuszenie OCR
# python3 glowny.py --input scan.pdf --template t.docx --output out.docx --engine ocr

# wymuszenie rownoleglosci
# python3 glowny.py --input duzy.pdf --template t.docx --output out.docx --parallel

import argparse
import logging
import time

from checkpdf_module import analyze_file
from tableimport import run_pipeline_with_metrics
from logging_config import setup_logging

logger = setup_logging(
    log_dir="logs",
    log_file="main.log",
    log_level="INFO"
)

# def setup_logging():
#     logging.basicConfig(
#         filename="main.log",
#         level=logging.INFO,
#         format="%(asctime)s %(levelname)s %(message)s"
#     )

def main():
    parser = argparse.ArgumentParser(
        description="Glowny orchestrator przetwarzania PDF -> Word"
    )

    parser.add_argument("--input", required=True, help="plik PDF")
    parser.add_argument("--template", required=True, help="szablon Word")
    parser.add_argument("--output", required=True, help="plik wynikowy DOCX")
    parser.add_argument("--engine", default="auto", help="wymuszenie silnika")
    parser.add_argument("--parallel", action="store_true", help="tryb rownolegoy")

    args = parser.parse_args()

    setup_logging()

    start_time = time.time()

    logger.info("Start programu")
    logger.info("START przetwarzania")
    logger.info(f"Plik wejsciowy: {args.input}")

    # 1. ANALIZA PDF
    result = analyze_file(args.input)

    logger.info(f"Typ PDF: {result.get('type')}")

    if not result.get("valid_pdf"):
        logger.error("Niepoprawny PDF - przerywam")
        print("Błąd: plik PDF nie jest poprawny")
        return

    pages = result.get("pages", 1)

    # 2. WYBÓR TRYBU
    use_parallel = args.parallel or (pages > 10)

    if use_parallel:
        logger.info("Tryb: rownolegoy")
    else:
        logger.info("Tryb: sekwencyjny")

    # 3. URUCHOMIENIE PIPELINE
    pipeline_result = run_pipeline_with_metrics(
        pdf_path=args.input,
        template_path=args.template,
        output_path=args.output,
        pdf_type=result["type"],
        pages=pages,
        forced_engine=args.engine,
        parallel=use_parallel
    )

    elapsed = time.time() - start_time

    # 4. PODSUMOWANIE
    summary = {
        "file": args.input,
        "type": result["type"],
        "pages": pages,
        "engine_used": pipeline_result.get("engine"),
        "tables_total": pipeline_result.get("tables_total", 0),
        "tables_valid": pipeline_result.get("tables_valid", 0),
        "time_sec": round(elapsed, 2)
    }

    logger.info(f"Podsumowanie: {summary}")

    print("\n=== PODSUMOWANIE ===\n")
    print(f"Plik: {summary['file']}")
    print(f"Typ PDF: {summary['type']}")
    print(f"Strony: {summary['pages']}")
    print(f"Silnik: {summary['engine_used']}")
    print(f"Tabele: {summary['tables_total']}")
    print(f"Poprawne: {summary['tables_valid']}")
    print(f"Czas: {summary['time_sec']} s\n")

    logger.info("KONIEC przetwarzania")


if __name__ == "__main__":
    main()