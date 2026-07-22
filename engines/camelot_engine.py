# -*- coding: utf-8 -*-

# Jest zgodny z architekturą:
# BaseEngine
# tableimport.py
# parallel_pipeline.py
# pdf2word_module.py

# Obsługuje:
# ekstrakcję całego PDF
# ekstrakcję pojedynczej strony
# tryb lattice (tabele z liniami)
# tryb stream (tabele bez linii)
# automatyczny fallback lattice → stream
# logowanie błędów

# Instalacja Camelot
# Ubuntu
#   pip install camelot-py
# Dodatkowo wymagany Ghostscript:
#   sudo apt install ghostscript
# Sprawdzenie:
#   gs --version

# Camelot będzie uruchamiany automatycznie, gdy:
# PDF jest klasyfikowany jako tekstowy tabelaryczny
# pdfplumber nie znalazł poprawnych tabel
# wymusisz: --engine camelot w glowny.py lub tableimport.py.

import logging

from .base_engine import BaseEngine


class CamelotEngine(BaseEngine):
    """
    Silnik ekstrakcji tabel oparty o Camelot.

    Najlepiej sprawdza się dla PDF tekstowych
    zawierających dobrze zdefiniowane tabele.
    """

    name = "camelot"

    def supports(self, pdf_type):
        """
        Określa czy silnik obsługuje dany typ PDF.
        """

        return pdf_type in [
            "tekstowy tabelaryczny",
            "tekstowy",
            "tabelaryczny (slaba jakosc)"
        ]

    def extract(self, pdf_path):
        """
        Ekstrakcja tabel z całego dokumentu.
        """

        results = []

        try:

            tables = self._try_lattice(pdf_path)

            if not tables:
                logging.info(
                    "camelot: lattice nie znalazł tabel, "
                    "próba stream"
                )

                tables = self._try_stream(pdf_path)

            for table in tables:

                try:
                    results.append(
                        {
                            "page": table.page,
                            "data": table.df.values.tolist()
                        }
                    )

                except Exception as e:
                    logging.error(
                        f"camelot: błąd konwersji tabeli: {e}"
                    )

        except Exception as e:
            logging.error(
                f"camelot: błąd ekstrakcji '{pdf_path}': {e}"
            )

        return results

    def extract_page(self, pdf_path, page_num):
        """
        Ekstrakcja pojedynczej strony.
        Wykorzystywana przez parallel_pipeline.py
        """

        try:

            tables = self._try_lattice(
                pdf_path,
                pages=str(page_num)
            )

            if not tables:
                tables = self._try_stream(
                    pdf_path,
                    pages=str(page_num)
                )

            return [
                t.df.values.tolist()
                for t in tables
            ]

        except Exception as e:
            logging.error(
                f"camelot: extract_page({page_num}) błąd: {e}"
            )

            return []

    def _try_lattice(self, pdf_path, pages="all"):
        """
        Tryb lattice:
        tabela posiada linie pionowe i poziome.
        """

        try:
            import camelot

            tables = camelot.read_pdf(
                pdf_path,
                pages=pages,
                flavor="lattice"
            )

            return tables

        except Exception as e:
            logging.warning(
                f"camelot lattice: {e}"
            )

            return []

    def _try_stream(self, pdf_path, pages="all"):
        """
        Tryb stream:
        tabela bez linii,
        rozpoznawanie na podstawie układu tekstu.
        """

        try:
            import camelot

            tables = camelot.read_pdf(
                pdf_path,
                pages=pages,
                flavor="stream"
            )

            return tables

        except Exception as e:
            logging.warning(
                f"camelot stream: {e}"
            )

            return []

    def count_tables(self, pdf_path):
        """
        Liczba wykrytych tabel.
        """

        try:
            return len(self.extract(pdf_path))
        except Exception:
            return 0

    def get_document_info(self, pdf_path):
        """
        Informacje diagnostyczne.
        """

        try:

            tables = self.extract(pdf_path)

            pages = set()

            for table in tables:
                pages.add(table["page"])

            return {
                "pages_with_tables": len(pages),
                "tables_found": len(tables),
                "engine": self.name
            }

        except Exception as e:

            logging.error(
                f"camelot: get_document_info błąd: {e}"
            )

            return {
                "pages_with_tables": 0,
                "tables_found": 0,
                "engine": self.name
            }