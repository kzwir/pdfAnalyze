# -*- coding: utf-8 -*-

# Bazowy interfejs dla wszystkich silników (pdfplumber, camelot, ocr, przyszłe AI/ML).
# Jego zadaniem jest wymuszenie wspólnego API dla wszystkich pluginów.

from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """
    Bazowa klasa dla wszystkich silników ekstrakcji danych z PDF.

    Każdy silnik powinien:
    - mieć unikalną nazwę
    - określać jakie typy PDF obsługuje
    - implementować ekstrakcję całego dokumentu
    - implementować ekstrakcję pojedynczej strony
    """

    name = "base"

    @abstractmethod
    def supports(self, pdf_type):
        """
        Sprawdza czy silnik obsługuje dany typ PDF.

        Parametry:
            pdf_type (str)

        Zwraca:
            bool
        """
        pass

    @abstractmethod
    def extract(self, pdf_path):
        """
        Ekstrakcja danych z całego dokumentu.

        Parametry:
            pdf_path (str)

        Zwraca:
            list

        Przykład wyniku:

        [
            {
                "page": 1,
                "data": [...]
            }
        ]
        """
        pass

    @abstractmethod
    def extract_page(self, pdf_path, page_num):
        """
        Ekstrakcja danych z pojedynczej strony.
        Wykorzystywane przez parallel_pipeline.py

        Parametry:
            pdf_path (str)
            page_num (int)

        Zwraca:
            list
        """
        pass

    def validate_result(self, result):
        """
        Podstawowa walidacja wyniku.

        Parametry:
            result

        Zwraca:
            bool
        """

        return isinstance(result, list)

    def get_metadata(self):
        """
        Zwraca metadane silnika.

        Zwraca:
            dict
        """

        return {
            "name": self.name,
            "class": self.__class__.__name__
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"(name='{self.name}')"
        )