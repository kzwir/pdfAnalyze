# -*- coding: utf-8 -*-

# zbiera metryki przetwarzania
# liczy jakość tabel
# liczy skuteczność przetwarzania
# śledzi wykorzystanie silników
# generuje podsumowanie dla dashboardu

# ===================================
#            DASHBOARD
# ===================================

# PDF total      : 2
# OK             : 1
# Errors         : 1
# Success rate   : 50.0 %

# Tabele         : 5
# Poprawne       : 4
# Quality        : 80.0 %

# Total time     : 12.4 s
# Average time   : 0.88 s
# Min time       : 0.5 s
# Max time       : 1.25 s

# Fallback count : 0
# Fallback rate  : 0.0 %

# Engine usage:
#   pdfplumber: 1

# PDF types:
#   tekstowy tabelaryczny: 1

import time
from collections import defaultdict


class Metrics:
    """
    Zbiera metryki z przetwarzania PDF.
    """

    def __init__(self):
        self.start_time = time.time()

        # PDF
        self.total = 0
        self.ok = 0
        self.error = 0

        # Tabele
        self.tables_total = 0
        self.tables_valid = 0

        # Czasy
        self.times = []

        # Silniki
        self.engine_usage = defaultdict(int)

        # Fallback
        self.fallback_count = 0

        # Typy PDF
        self.pdf_types = defaultdict(int)

    def add_result(self, result):
        """
        Dodaje wynik pojedynczego pliku.
        """

        self.total += 1

        if result.get("status") == "ok":
            self.ok += 1
        else:
            self.error += 1

        self.tables_total += result.get("tables_total", 0)
        self.tables_valid += result.get("tables_valid", 0)

        if "time" in result:
            self.times.append(result["time"])

        engine = result.get("engine")
        if engine:
            self.engine_usage[engine] += 1

        pdf_type = result.get("pdf_type")
        if pdf_type:
            self.pdf_types[pdf_type] += 1

        if result.get("fallback_used", False):
            self.fallback_count += 1

    def get_total_time(self):
        return time.time() - self.start_time

    def get_average_time(self):
        if not self.times:
            return 0

        return sum(self.times) / len(self.times)

    def get_min_time(self):
        if not self.times:
            return 0

        return min(self.times)

    def get_max_time(self):
        if not self.times:
            return 0

        return max(self.times)

    def get_success_rate(self):
        if self.total == 0:
            return 0

        return (self.ok / self.total) * 100

    def get_table_quality(self):
        if self.tables_total == 0:
            return 0

        return (self.tables_valid / self.tables_total) * 100

    def get_fallback_rate(self):
        if self.total == 0:
            return 0

        return (self.fallback_count / self.total) * 100

    def summary(self):
        """
        Zwraca pełne podsumowanie dashboardu.
        """

        return {
            "total": self.total,
            "ok": self.ok,
            "error": self.error,
            "success_rate": round(
                self.get_success_rate(), 2
            ),

            "tables_total": self.tables_total,
            "tables_valid": self.tables_valid,
            "quality": round(
                self.get_table_quality(), 2
            ),

            "total_time": round(
                self.get_total_time(), 2
            ),

            "avg_time": round(
                self.get_average_time(), 2
            ),

            "min_time": round(
                self.get_min_time(), 2
            ),

            "max_time": round(
                self.get_max_time(), 2
            ),

            "fallback_count": self.fallback_count,

            "fallback_rate": round(
                self.get_fallback_rate(), 2
            ),

            "engine_usage": dict(
                self.engine_usage
            ),

            "pdf_types": dict(
                self.pdf_types
            )
        }

    def print_dashboard(self):
        """
        Dashboard tekstowy.
        """

        summary = self.summary()

        print()
        print("===================================")
        print("           DASHBOARD")
        print("===================================")
        print()

        print(f"PDF total      : {summary['total']}")
        print(f"OK             : {summary['ok']}")
        print(f"Errors         : {summary['error']}")
        print(f"Success rate   : {summary['success_rate']} %")
        print()

        print(f"Tabele         : {summary['tables_total']}")
        print(f"Poprawne       : {summary['tables_valid']}")
        print(f"Quality        : {summary['quality']} %")
        print()

        print(f"Total time     : {summary['total_time']} s")
        print(f"Average time   : {summary['avg_time']} s")
        print(f"Min time       : {summary['min_time']} s")
        print(f"Max time       : {summary['max_time']} s")
        print()

        print(f"Fallback count : {summary['fallback_count']}")
        print(f"Fallback rate  : {summary['fallback_rate']} %")
        print()

        print("Engine usage:")
        for engine, count in summary["engine_usage"].items():
            print(f"  {engine}: {count}")

        print()

        print("PDF types:")
        for pdf_type, count in summary["pdf_types"].items():
            print(f"  {pdf_type}: {count}")

        print()
        print("===================================")
        print()