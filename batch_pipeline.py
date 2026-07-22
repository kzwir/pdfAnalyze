# -*- coding: utf-8 -*-

# Przetwarza katalog PDF
# dziala rownolegle (multiprocessing)
# integruje caly pipeline (checkpdf -> tableimport -> engines -> Word)
# zbiera metryki i generuje dashboard
# obsluguje bledy + retry
# zapisuje raport JSON

# python3 batch_pipeline.py --input-dir pdfs --template szablon.docx --output-dir output --workers 4

# projekt/
# │
# ├── pdfs/
# │   ├── a.pdf
# │   ├── b.pdf
# │
# ├── output/
# │   ├── a.docx
# │   ├── b.docx
# │
# ├── batch_pipeline.py
# ├── glowny.py
# ├── tableimport.py
# ├── pdf2word_module.py
# ├── checkpdf_module.py
# ├── metrics.py
# └── engines/

import os
import logging
import time
import json
from multiprocessing import Pool, cpu_count

from checkpdf_module import analyze_file
from tableimport import run_pipeline_with_metrics
from metrics import Metrics
from pdf2word_module import (create_document,process_pdf_to_word,save_document)

# LOGGING
def setup_logging():
    logging.basicConfig(
        filename="batch.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )


# POJEDYNCZY PLIK
def process_single(args):
    pdf_path, template_path, output_dir = args

    start = time.time()

    try:
        logging.info("batch_pipeline.py: process_single")
        logging.info(f"START: {pdf_path}")

        # analiza pliku
        result = analyze_file(pdf_path)

        if not result.get("valid_pdf"):
            logging.error(f"Niepoprawny PDF: {pdf_path}")
            return {
                "file": pdf_path,
                "status": "error",
                "reason": "invalid_pdf"
            }

        pages = result.get("pages", 1)

        # sciezka wynikowa
        output_path = os.path.join(
            output_dir,
            os.path.basename(pdf_path).replace(".pdf", ".docx")
        )

        # pipeline
        pipeline_result = run_pipeline_with_metrics(
            pdf_path=pdf_path,
            template_path=template_path,
            output_path=output_path,
            pdf_type=result["type"],
            pages=pages,
            forced_engine="auto",
            parallel=(pages > 10)
        )

        elapsed = time.time() - start

        logging.info(f"OK: {pdf_path} ({elapsed:.2f}s)")

        return {
            "file": pdf_path,
            "status": "ok",
            "engine": pipeline_result.get("engine"),
            "tables_total": pipeline_result.get("tables_total", 0),
            "tables_valid": pipeline_result.get("tables_valid", 0),
            "time": elapsed
        }

    except Exception as e:
        logging.error(f"Błąd: {pdf_path} -> {e}")

        return {
            "file": pdf_path,
            "status": "error",
            "error": str(e)
        }


# RETRY WRAPPER
def process_with_retry(args, retries=2):
    logging.info("batch_pipeline.py: process_with_retry")
    for attempt in range(retries):
        result = process_single(args)

        if result["status"] == "ok":
            return result

        logging.warning(f"Retry {attempt+1} dla {args[0]}")

    return result

# scal pliki pdf do jednego pliku docx
def run_merged(pdf_files,template_path,output_dir,metrics):

    document = create_document(template_path)

    for pdf_path in pdf_files:
        start = time.time()

        try:
            result = analyze_file(
                pdf_path
            )

            if not result["valid_pdf"]:
                elapsed = time.time() - start
                metrics.add_result(
                {
                    "status": "error",
                    "time": elapsed
                })

                continue

            pipeline_result = run_pipeline_with_metrics(
                pdf_path=pdf_path,
                template_path=template_path,
                output_path=None,
                pdf_type=result["type"],
                pages=result.get("pages", 1),
                forced_engine="auto",
                parallel=(result.get("pages", 1) > 10),
                document=document
            )

            elapsed = time.time() - start

            metrics.add_result(
            {
                "status": "ok",
                "engine": pipeline_result.get("engine"),
                "tables_total": pipeline_result.get("tables_total", 0),
                "tables_valid": pipeline_result.get("tables_valid", 0),
                "time": elapsed
            })
        
        except Exception as e:

            logging.error(
                f"Błąd {pdf_path}: {e}"
            )

            metrics.add_result(
                {
                    "status": "error"
                }
            )

    save_document(
        document,
        os.path.join(
            output_dir,
            "wynik_zbiorczy.docx"
        )
    )

# grupuj pliki pdf w plikach docx
def run_grouped(pdf_files,template_path,output_dir,group_size,metrics):

    part = 1

    document = create_document(
        template_path
    )

    current_count = 0

    for pdf_path in pdf_files:
        start = time.time()

        try:
            result = analyze_file(pdf_path)

            if not result["valid_pdf"]:           
                elapsed = time.time() - start
                metrics.add_result(
                {
                    "status": "error",
                    "time": elapsed
                })
                continue

            pipeline_result = run_pipeline_with_metrics(
                pdf_path=pdf_path,
                template_path=template_path,
                output_path=None,
                pdf_type=result["type"],
                pages=result.get("pages", 1),
                forced_engine="auto",
                parallel=(result.get("pages", 1) > 10),
                document=document
            )

            elapsed = time.time() - start

            metrics.add_result(
            {
                "status": "ok",
                "engine": pipeline_result.get("engine"),
                "tables_total": pipeline_result.get("tables_total", 0),
                "tables_valid": pipeline_result.get("tables_valid", 0),
                "time": elapsed
            })

            current_count += 1

            if current_count >= group_size:

                save_document(
                    document,
                    os.path.join(
                        output_dir,
                        f"part_{part:03}.docx"
                    )
                )

                part += 1
                current_count = 0

                document = create_document(template_path)

        except Exception as e:
        
            logging.error(
                f"Błąd {pdf_path}: {e}"
            )

            metrics.add_result(
                {
                    "status": "error"
                }
            )

    if current_count > 0:

        save_document(
            document,
            os.path.join(
                output_dir,
                f"part_{part:03}.docx"
            )
        )

# DASHBOARD
def print_dashboard(summary):
    print("\n=== DASHBOARD ===\n")

    print(f"PDF total: {summary['total']}")
    print(f"OK: {summary['ok']}")
    print(f"Errors: {summary['error']}")
    print(f"Success rate: {summary['success_rate']}%\n")

    print(f"Tabele: {summary['tables_total']}")
    print(f"Poprawne: {summary['tables_valid']}")
    print(f"Quality: {summary['quality']}%\n")

    print(f"Avg time: {summary['avg_time']} s")
    print(f"Total time: {summary['total_time']} s\n")

    print("Engine usage:")
    for k, v in summary["engine_usage"].items():
        print(f"  {k}: {v}")


# GLOWNY BATCH
def run_batch(input_dir, template_path, output_dir, workers=None, merge_mode="single", group_size=10
):
    workers = workers or min(cpu_count(), 4)

    logging.info("batch_pipeline.py: run_batch")
    logging.info("========== START BATCH ==========")
    logging.info(f"Katalog wejściowy: {input_dir}")
    logging.info(f"Workers: {workers}")
    logging.info(f"Merge mode: {merge_mode}")

    os.makedirs(output_dir, exist_ok=True)

    # lista PDF
    pdf_files = [
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.lower().endswith(".pdf")
    ]

    pdf_files.sort()

    logging.info(f"Znaleziono {len(pdf_files)} plików PDF")

    
    if not pdf_files:
        logging.warning("Brak plików PDF")
        return

    metrics = Metrics()


    # ======================================================
    # SINGLE
    # ======================================================
    if merge_mode == "single":
        args = [(pdf, template_path, output_dir) for pdf in pdf_files]

        with Pool(workers) as pool:
            for result in pool.imap_unordered(process_with_retry, args):
                metrics.add_result(result)
                logging.info(f"Wynik: {result}")
    
    # ======================================================
    # MERGED
    # ======================================================
    elif merge_mode == "merged":
        run_merged(pdf_files,template_path,output_dir,metrics)
        
    # ======================================================
    # GROUPED
    # ======================================================
    elif merge_mode == "grouped":
        run_grouped(pdf_files,template_path,output_dir,group_size,metrics)
  
    # ======================================================
    # DASHBOARD
    # ======================================================

    summary = metrics.summary()

    print_dashboard(summary)

    # zapis JSON
    with open("dashboard.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    logging.info("========== KONIEC BATCH ==========")

    return summary


# CLI
def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch przetwarzanie katalogu PDF → Word"
    )

    parser.add_argument("--input-dir", required=True, help="katalog PDF")
    parser.add_argument("--template", required=True, help="szablon Word")
    parser.add_argument("--output-dir", required=True, help="katalog wynikowy")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--merge-mode", choices=["single", "merged", "grouped"], default="single")
    parser.add_argument("--group-size", type=int, default=10)

    args = parser.parse_args()

    setup_logging()

    logging.info("batch_pipeline.py")

    run_batch(
        input_dir=args.input_dir,
        template_path=args.template,
        output_dir=args.output_dir,
        workers=args.workers,
        merge_mode=args.merge_mode,
        group_size=args.group_size
    )


if __name__ == "__main__":
    main()