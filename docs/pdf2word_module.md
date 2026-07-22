# pdf2word_module.py

## Cel modułu

Moduł `pdf2word_module.py` odpowiada za przetwarzanie danych tabelarycznych oraz dokumentów PDF do postaci dokumentu Microsoft Word (`.docx`).

Moduł realizuje następujące zadania:

- tworzenie dokumentów Word,
- wczytywanie szablonów DOCX,
- usuwanie tabel znajdujących się w szablonie,
- zapis dokumentów DOCX,
- normalizację struktur tabelarycznych,
- dodawanie dodatkowej kolumny do tabel,
- walidację artefaktów ekstrakcji,
- ocenę jakości tabel,
- generowanie raportu walidacyjnego,
- tworzenie tabel Word,
- konfigurację obramowań tabel,
- inicjalizację silników ekstrakcji,
- przetwarzanie wcześniej wyekstrahowanych tabel,
- bezpośrednie przetwarzanie dokumentów PDF.

Moduł stanowi warstwę transformacji danych pomiędzy silnikami ekstrakcji a końcowym dokumentem DOCX.

---

# Miejsce modułu w architekturze systemu

```text
PDF
 │
 ▼
Silnik ekstrakcji
 │
 ├── PdfPlumberEngine
 ├── CamelotEngine
 └── OCREngine
 │
 ▼
pdf2word_module.py
 │
 ├── Walidacja danych
 ├── Normalizacja danych
 ├── Analiza jakości
 ├── Raport walidacji
 └── Generowanie DOCX
 │
 ▼
Dokument Word
```

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- generowanie dokumentów DOCX,
- zapis dokumentów DOCX,
- obsługę szablonów DOCX,
- walidację tabel,
- standaryzację struktury tabel,
- analizę jakości danych,
- generowanie raportu walidacji,
- tworzenie tabel Word,
- wybór i inicjalizację silnika ekstrakcji PDF.

## Zakres funkcjonalny

```text
pdf2word_module.py
│
├── Dokument DOCX
│   ├── create_document()
│   └── save_document()
│
├── Walidacja
│   ├── is_valid_table()
│   ├── check_quality()
│   ├── calculate_quality()
│   └── validate_quality()
│
├── Transformacja
│   ├── normalize_table()
│   └── add_new_column()
│
├── Formatowanie DOCX
│   └── set_table_borders()
│
├── Factory silników
│   └── create_engine()
│
└── Eksport
    ├── process_tables_to_word()
    └── process_pdf_to_word()
```

---

# Diagram przepływu danych

## PDF → DOCX

```text
PDF
 │
 ▼
create_engine()
 │
 ▼
extract()
 │
 ▼
walidacja tabel
 │
 ▼
normalizacja
 │
 ▼
analiza jakości
 │
 ▼
tabele DOCX
 │
 ▼
raport walidacji
 │
 ▼
wynik
```

## Tables → DOCX

```text
tables
 │
 ▼
walidacja
 │
 ▼
normalizacja
 │
 ▼
analiza jakości
 │
 ▼
generowanie DOCX
 │
 ▼
raport walidacji
```

---

# Opis działania modułu

Moduł udostępnia dwa główne scenariusze użycia.

## Scenariusz 1

Przetwarzanie wcześniej wyekstrahowanych tabel.

W tym scenariuszu funkcja:

```python
process_tables_to_word()
```

otrzymuje gotowe dane wejściowe i generuje dokument Word bez wykonywania ekstrakcji PDF.

---

## Scenariusz 2

Przetwarzanie dokumentu PDF.

W tym scenariuszu funkcja:

```python
process_pdf_to_word()
```

samodzielnie inicjalizuje silnik ekstrakcyjny, pobiera dane z dokumentu PDF oraz generuje dokument Word.

---

# Struktura katalogów

Możliwa do odtworzenia na podstawie kodu:

```text
project/
│
├── pdf2word_module.py
│
├── engines/
│   ├── pdfplumber_engine.py
│   ├── camelot_engine.py
│   └── ocr_engine.py
│
├── templates/
│   └── *.docx
│
└── output/
    └── *.docx*```

---

# Model danych

## Struktura pojedynczego elementu tabeli

```python
{
    "page": 3,
    "data": [
        ["A", "B"],
        ["1", "2"]
    ]
}
```

---

## Struktura wyniku funkcji eksportujących

```python
{
    "tables": 10*
    "tables_valid": 8,
    "valid*tion_log": [
        "Tabela 1: pominięto artefakt"
    ]
}
```

---
# Funkcje modułu

## create_document()

### Przeznaczenie

Tworzy dokument Word na podstawie szablonu DOCX.

Jeżeli nie można załadować szablonu, tworzony jest pusty dokument.

Dodatkowo funkcja usuwa wszystkie tabele znajdujące się w załadowanym dokumencie.

---

###*Sygnatura

```python
def create_document(template_path):
```

### Parametry

#### template_path

Typ:

```python
str
```

Ścieżka do pliku szablonu DOCX.

---

### Wartości zwracane

Typ:

```python
Document
```
---

### Przepływ działania

```text
wczytanie szablonu
 │
 ▼
utworzenie Document
 │
 ▼
usunięcie tabel
 │
 ▼
return document
```

---

### Obsługa błędów

Obsługiwane są:

- błędy ładowania szablonu,
- błędy usuwania tabel.

Przy błędzie ładowania tworzony jest pusty dokument.
---

### Przykład użycia

```python
document = create_document(
    "templates/report.docx"
)
```

### Przykładowy wynik

```python
<Document>
```

### Kiedy używać

Należy używać przed rozpoczęciem generowanie dokumentu DOCX.

Funkcja zapewnia jednolity sposób inicjalizacji dokumentów w całym projekcie.

---

## save_document()

### Przeznaczenie
Zapisuje dokument Word do wskazanej lokalizacji.

---

### Sygnatura
```python
def save_document(docum*nt, output_path):
```

### Parametry

#### document

Typ:

```python
Document
```

#### output_path

Type

```python
str
```

---

### Wartości zwracane

Typ:

```python
bool
```

Możliwe wartości:

```python
True
False
```

---

### Przepływ działania

```text
utworzenie katalogu
 │
 ▼
document.save()
 │
 ▼
zapis logu
 │
 ▼
return
```

---

### Obsługa błędów

Obsługiwane są wyjątki zapisu dokumentu oraz tworzenia katalogów.

---

### Przykład użycia

```python
save_document(
    document,
    "output/report.docx"
)
```

### Przykładowy wynik

```python
True
```

### Kiedy używać

Po zakończeniu generowania dokumentu Word.

Jest końcowym etapem procesu eksportu.

---

## is_valid_table()

### Przeznaczenie

Weryfikuje, czy tabela posiada więcej niż jeden wiersz i więcej niż jedną kolumnę.

---

### Sygnatura

```python
def is_alid_table(df):
```

### Parametry
#### df

Typ:

```python
pandas.DataFrame
```

---

### Wartości zwracane

Type

```python
bool
```

---

### Przykład użycia

```Python
is_valid_table(df)
```

### Przykładowy wynik

```python
True
```

### Kiedy używać

Przed dalszym przetwarzaniem danych tabelaryczny*h.

Pozwala eliminować artefakty ekstrakcji.

---

## normalize_table*

### Przeznaczenie

Normalizuje długość wszystkich wierszy tabeli.
Brakujące wartości są uzupełniane pustymi ciągami znaków.

---

### Sygnatura

```python
def normalize_table(table):
```

### Parametry

### table

Typ:

```python
list
```
---

### Wartości zwracane

Typ:

```python
list
```

---

### Przykład użycia

```python
normalize_table([
    ["A", "B"],
    ["1"]
])
```

### Przykładowy wynik

```python*[
    ["A", "B"],
    ["1", ""]
]
```

### Kiedy używać

Przed utworzeniem obiektu DataFrame.

Zapewnia jednolitą strukturę wszystkich wierszy.

---

## add_new_column()

### Przeznaczenie

Dodaje nową kolumnę o nazwie:

```text
nowa kolumna
```

oraz wpisuje tę nazwę do pierwsz*go wiersza nowej kolumny.

---

### Sygnatura

```python
def add_new_column(df):
```

### Parametry

###* df

Typ:

```python
pandas.DataFrame
```

---

### Wartości zwracane
Typ:

```python
pandas.DataFrame
```

---

### Kiedy używać

Po normalizacji danych i przed eksportem tabeli do Word.

---

## check_quality()

### Przeznaczenie

Wylicza udział pustych komórek w tabeli.

---
### Sygnatura

```python
def chec_quality(df):
```

### Parametry

### df

Typ:

```python
pandas.DataFrame
```

---

### Wartości zwracane

Typ:

```python
float
```

---
### Wzór

```text
empty_cells / total_cells
```

---

### Przykład użycia

```python
ratio = check_quality(df)
```

### Przykładowy wynik
```python
0.25
```

---

## calculate_quality()

### Przeznaczenie

Oblicza zestaw metryk jakości tabeli

---

### Sygnatura

```python
def calculate_quality(df):
```

### Parametry

#### df

Typ:

```python
pandas.DataFrame
```

---

### Wartości zwracane

Typ:

```python
dict
```

lub

```python
None
```

---
### Przykładowy wynik

```python
{*    "rows": 10,
    "cols": 5,
   *"total_cells": 50,
    "empty_cell*": 2,
    "empty_ratio": 0.04
}
```

---

### Kiedy używać

W sytuacjach wymagających analizy jakości wyekstrahowanych danych.

---

## validate_quality()

### Przeznaczenie
Generuje komunikaty walidacyjne dotyczące jakości tabel.

---

### Sy*natura

```python
def validate_quality(df, table_counter):
```

### Parametry

#### df

Typ:

```python
pandas.DataFrame
```

#### table_counter

Typ:

```python
int
```

---
### Wartości zwracane

Typ:

```python
list
```

---

### Wykrywane sytuacje

- tylko jeden wiersz,
- tylko jedna kolumna,
- ponad 95% pustych komórek,
- ponad 80% pustych komórek.

---

### Przykładowy wynik
```python
[
    "Tabela 2: tylko jedna kolumna"
]
```

---

### Kiedy używać

Podczas walidacji jakości danych przed eksportem.

---

## set_table_borders()

### Przeznaczenie

Dodaje czarne obramowanie do tabeli Word.

---

### Sygnatura

```python
def set_table_borders(table)
```

### Parametry

#### table

Typ:

```python
Table
```

---

### Wartości zwracane

Brak.

---

### Kiedy używać

Po utworzeniu tabeli Word i przed zapisaniem dokumentu.
---

## create_engine()

### Przeznaczenie

Tworzy obiekt silnika ekstrakcji.

---

### Sygnatura

```python
def create_engine(engine_name)
```

### Parametry

#### engine_name

Typ:

```python
str
```

Obsługiwane wartości:

```text
pdfplumber
camelot
ocr
```

---

### Wartości zwracane

Instancja odpowiedniego silnika.

---

### Obsługa błędów
Błędy inicjalizacji są logowane i ponownie zgłaszane.

---

### Kiedy używać

Przed rozpoczęciem ekstrakcji danych z PDF.

---

## process_tables_to_word()

### Przeznaczenie
Generuje dokument Word z wcześnij wyekstrahowanych tabel.

Nie wykonuje ekstrakcji danych z PDF.

---
### Sygnatura

```python
def proces_tables_to_word(
    tables,
    document,
    source_name="?"
):
```

### Parametry

#### tables

Typ:
```python
list
```

#### document
Typ:

```python
Document
```

### source_name

Typ:

```python
str
```

---

### Wartości zwracane

Typ:

```python
dict
```

---

### Przepływ działania

```text
tabele
 │
 ▼
walidacja
 │
 ▼
normalizacja
 │
 ▼
analiza jakości
 │
 ▼
tworzenie tabel DOCX
 │
 ▼
raport walidacji
 │
 ▼
wynik
```

---

### Obsługa błędów

Obsługiwane są błędy:

- przetwarzania tabel,
- konwersji danych,
- generowania raportu,
- aktualizacji komórek dokumentu.

---

### Przykład użycia

```python
result = process_tables_to_word(
    tables
    document,
    "raport.pdf"
)
```

### Przykładowy wynik

```python
{
    "tables": 5,
    "tables_valid": 4,
    "validation_log": []
```

### Kiedy używać

Gdy dane zostały wcześniej wyekstrahowane przez inne moduły projektu.

Pozwala o*dzielić proces ekstrakcji od eksportu do Word.

---

## process_pdf_to_word()

### Przeznaczenie

Przetwarza dokument PDF i generuje jego zawartość w dokumencie Word.

---

### Sygnatura

```python
def process pdf_to_word(
    pdf_path,
    document,
    engine_name="pdfplumber"):
```

### Parametry

#### pdf_path

Typ:

```python
str
```

#### ducument

Typ:

```python
Document
```

#### engine_name

Typ:

```python
str
```

---

### Wartości zwracane

Typ:

```python
dict
```

---
### Przepływ działania

```text
create_engine()
 │
 ▼
extract()
 │
 ▼ walidacja
 │
 ▼
normalizacja
 │
 ▼ analiza jakości
 │
 ▼
tworzenie DOCX
 │
 ▼
raport walidacji
 │
 ▼
wynik
```

---

### Obsługa błędów

Obsługiwane są:

- błędy inicjalizacji silnika,
- błędy ekstrakcji,
- błędy tabel,
- błędy komórek,
- błędy raportowania.

---

### Przykład użycia

```python
result = process_pdf_to_word(
    "dokument.pdf",
   document,
    "pdfplumber"
)
```

### Przykładowy wynik

```python
{
   "tables": 12,
    "tables_valid: 10,
    "validation_log": []
}
```

### Kiedy używać

Gdy wymagane jest pełne przetworzenie PDF i wygenerowanie dokumentu DOCX w jednym kroku.

---

# Tryby pracy

## Table → Word

Funkcja:

```python
process_tables_to_word()
```

---

## PDF → Word

Funkcja:

```python
process_pdf_to_word()
```

---

# Multiprocessing

Moduł nie wykorzystuje multiprocessing.

---

# Dashboard

Moduł nie generuje dashboardu.

---
# Raporty

Moduł generuje sekcję:
```text
Raport walidacji
```

Sekcja zawiera komunikaty dotyczące jakości danych oraz błędów przetwarzania.

---

# Logowanie

## Co jest logowane

- ładowanie szablonów,
- zapis dokumentów,
- błędy walidacji
- błędy ekstrakcji,
- błędy tabel
- błędy komórek,
- błędy silników
- rozpoczęcie i zakończenie przetwarzania.

## Gdzie są zapisywane logi

Moduł nie definiuje własnej konfiguracji logowania.

Wykorzystuje

```python
logger = logging.getLogger(__name__)
```

Miejsce zapisu zależy od konfiguracji aplikacji nadrzędnej.

---

# Interfejs CLI

Moduł nie zawiera:

```python
if __name__ == "__main__":
```

Nie udostędnia interfejsu CLI.

---

# Przykłady integracji

## parallel_pipeline.py

Przekazuje:

```python
tables```

Odbiera:

```python
result
```

Rola: dostarczenie danych wyekstrahowanych równolegle.

---

## batch_pipeline.py

Przekazuje:

```python
pdf_path
```

Odbiera:

```python
result
```

Rola: masowe przetwarzanie dokumentów.

---

## logging*config.py

Zapewnia konfigurację loggera używanego przez moduł.

---
## Przykłady produkcyjne

## Utworzenie dokumentu

```python
document create_document(
    "/templates/template.docx"
)
```

## Przetwarzanie PDF

```python
result = process_pdf_to_word(
    "/pdf/raport.pdf"
    document,
    "pdfplumber"
)
```

## Zapis dokumentu

```python
save_document(
    document,
    "/utput/raport.docx"
)
```

---

# Wdajność

## Multiprocessing

Brak.
## Wpływ liczby workers

Nie dotyczy.

## Potencjalne wąskie gardła
- ekstrakcja danych przez silnik,
- iteracja po komórkach DataFrame,
- generowanie dużych tabel Word,
- zapis dokumentów DOCX.

## Najbardziej obciążające CPU

- tworzenie DataFrame,
- analiza jakości,
- przetwarzanie danych komórek.

## Najbar*ziej obciążające I/O

- odczyt PDF
- odczyt szablonu DOCX,
- zapis dokumentu DOCX.

---

# Zależności

## os

Przeznaczenie:

- obsługa ścieżek,
- tworzenie katalogów.

## logging

Przeznaczenie:

- logowanie zdarzeń.

## pandas

Przeznaczenie

- operacje na tabelach,
- analiza jakości.

Repozytorium:

https://github.com/pandas-dev/pandas

## python-docx

Przeznaczenie:

- tworzenie dokumentów Word.

Repozytorium:
https://github.com/python-openxml/python-docx

## OxmlElement

Przeznaczenie:

- konfiguracja XML tabel DOCX.

## qn

Przeznaczenie:

- konfiguracja atrybutów XML DOCX.

---
# Powiązane moduły projektu

- checkpdf_module.md
- batch_pipeline.md
- [tableimport.md](tableimport.md
- parallel_pipeline.md
- [metrics.md](metrics.md)
- logging_config.md

## checkpdf_module.py

Może dostarczać informacje potrzebne do wyboru mechanizmu przetwarzania PDF.

## batch_pipeline.py

Realizuje przetwarzanie wielu dokumentów wykorzystujących funkcje eksportowe modułu.
## tableimport.py

Może przekazywać gotowe dane tabelaryczne do eksportu.

## parallel_pipeline.py

Może dostarczać dane wyekstrahowane ze stron PDF.

## metrics.py

Może analizować wyniki zwracane przez funkcje eksportowe.

## logging_config.py

Dostarcza konfigurację logowania wykorzystywaną przez moduł.

---
## Podsumowanie

Moduł `pdf2word_module.py` odpowiada za generowanie dokumentów Word na podstawie danych tabelarycznych lub bezpośrednio z dokumentów PDF. Zawiera mechanizmy walidacji danych, normalizacji tabel i oceny jakości oraz generowania raportu walidacyjnego.

Najważniejszymi funkcjami modułu są `process_tables_to_word()` oraz `process_pdf_to_word()`. Moduł stanowi warstwę transformacji danych pomiędzy silnikami ekstrakcji a końcowym dokumentem DOCX i jest centralnym komponentem eksportu danych do formatu Word.
```
