# tableimport.py

## Cel modułu

Moduł `tableimport.py` odpowiada za koordynację procesu ekstrakcji tabel z dokumentów PDF oraz generowania dokumentów Word.

Stanowi centralny komponent integracyjny pomiędzy:

- silnikami ekstrakcji tabel,
- mechanizmem fallback,
- przetwarzaniem równoległym,
- modułem generowania Word,
- warstwą raportowania metryk,
- interfejsem CLI.

Moduł realizuje kompletny pipeline:

```text
PDF → Ekstrakcja tabel → Walidacja → Word → Metryki
```

---

# Miejsce modułu w architekturze systemu

```text
PDF
 │
 ▼
checkpdf_module.py
 │
 ▼
tableimport.py
 │
 ├── EngineManager
 │   ├── PdfPlumberEngine
 │   ├── CamelotEngine
 │   └── OCREngine
 │
 ├── fallback
 │
 ├── parallel_pipeline.py
 │
 ├── pdf2word_module.py
 │
 ▼
DOCX
 │
 ▼
metrics.py
```

Moduł pełni rolę głównego koordynatora procesu przetwarzania PDF.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- zarządzanie silnikami ekstrakcji,
- wybór silnika ekstrakcji,
- realizację fallback pomiędzy silnikami,
- uruchamianie przetwarzania równoległego,
- uruchamianie przetwarzania sekwencyjnego,
- tworzenie dokumentów Word,
- zapis dokumentów Word,
- agregację podstawowych metryk przetwarzania,
- udostępnianie interfejsu CLI.

---

## Poza zakresem modułu

Moduł nie odpowiada za:

- implementację silników ekstrakcji,
- generowanie dashboardów,
- przechowywanie metryk,
- konfigurację logowania,
- analizę typu PDF.

---

# Model danych

## Wynik procesu

Moduł zwraca słownik:

```python
{
    "tables_total": 10,
    "tables_valid": 8,
    "engine": "pdfplumber"
}
```

### Pola

#### tables_total

Typ:

```python
int
```

Liczba wszystkich przetworzonych tabel.

#### tables_valid

Typ:

```python
int
```

Liczba poprawnych tabel.

#### engine

Typ:

```python
str
```

lub

```python
None
```

Nazwa wykorzystanego silnika.

---

## Struktura tabel wykorzystywana przez pipeline

```python
{
    "page": 3,
    "data": [...]
}
```

---

# Miejsce modułu w przepływie danych

```text
PDF
 │
 ▼
wybór silnika
 │
 ▼
ekstrakcja
 │
 ▼
fallback
 │
 ▼
normalizacja danych
 │
 ▼
Word
 │
 ▼
metryki
```

---

# Diagram przepływu danych

## Tryb automatyczny

```text
PDF
 │
 ▼
EngineManager
 │
 ▼
run_with_fallback()
 │
 ▼
pdfplumber
 │
 ▼
camelot
 │
 ▼
ocr
 │
 ▼
tables
 │
 ▼
process_tables_to_word()
 │
 ▼
DOCX
```

---

## Tryb równoległy

```text
PDF
 │
 ▼
run_parallel()
 │
 ▼
wyniki stron
 │
 ▼
agregacja tabel
 │
 ▼
process_tables_to_word()
 │
 ▼
DOCX
```

---

# Opis działania modułu

Przetwarzanie przebiega następująco:

1. Odbierane są parametry wejściowe.
2. Tworzony jest obiekt `EngineManager`.
3. Wybierany jest tryb pracy.
4. Następuje ekstrakcja danych.
5. W trybie automatycznym wykorzystywany jest mechanizm fallback.
6. W trybie równoległym wykorzystywany jest moduł `parallel_pipeline`.
7. Dane przekazywane są do modułu `pdf2word_module`.
8. Tworzony jest dokument Word.
9. Wyliczane są podstawowe metryki.
10. Wynik jest zwracany użytkownikowi.

---

# Klasa EngineManager

## Przeznaczenie

Klasa zarządza wszystkimi dostępnymi silnikami ekstrakcji.

Zapewnia:

- rejestrację silników,
- filtrowanie obsługiwanych silników,
- wyszukiwanie silnika po nazwie,
- implementację mechanizmu fallback.

---

## Atrybuty klasy

### engines

Typ:

```python
list
```

Zawiera:

```python
PdfPlumberEngine()
CamelotEngine()
OCREngine()
```

---

## Metody klasy

### __init__()

#### Przeznaczenie

Inicjalizuje listę dostępnych silników.

#### Sygnatura

```python
def __init__(self):
```

#### Parametry

Brak.

#### Wartości zwracane

Brak.

#### Przykład użycia

```python
manager = EngineManager()
```

#### Kiedy używać

Podczas inicjalizacji procesu ekstrakcji.

---

### get_supported_engines()

#### Przeznaczenie

Zwraca silniki obsługujące wskazany typ PDF.

#### Sygnatura

```python
def get_supported_engines(self, pdf_type):
```

#### Parametry

##### pdf_type

Typ:

```python
str
```

#### Wartości zwracane

Typ:

```python
list
```

#### Przykład

```python
engines = manager.get_supported_engines(
    "tekstowy"
)
```

#### Kiedy używać

Przy wyborze silników obsługujących określony typ PDF.

---

### get_engine_by_name()

#### Przeznaczenie

Pobiera silnik na podstawie nazwy.

#### Sygnatura

```python
def get_engine_by_name(self, name):
```

#### Parametry

##### name

Typ:

```python
str
```

#### Wartości zwracane

Silnik lub:

```python
None
```

#### Przykład

```python
engine = manager.get_engine_by_name(
    "ocr"
)
```

#### Kiedy używać

Przy wymuszeniu konkretnego silnika.

---

### run_with_fallback()

#### Przeznaczenie

Realizuje sekwencyjny fallback pomiędzy silnikami.

Kolejność:

```text
pdfplumber
↓
camelot
↓
ocr
```

#### Sygnatura

```python
def run_with_fallback(
    self,
    pdf_path,
    pdf_type
):
```

#### Parametry

##### pdf_path

Typ:

```python
str
```

##### pdf_type

Typ:

```python
str
```

#### Wartości zwracane

```python
(
    tables,
    engine_name
)
```

#### Przepływ działania

```text
supports()
 │
 ▼
extract()
 │
 ▼
wynik ?
 ├── TAK
 │
 ▼
return
 │
 └── NIE
     ▼
kolejny silnik
```

#### Obsługa błędów

Błędy silników są logowane:

```python
logger.error(...)
```

Po błędzie wykonywana jest próba kolejnym silnikiem.

#### Przykład użycia

```python
tables, engine = (
    manager.run_with_fallback(
        pdf_path,
        pdf_type
    )
)
```

#### Przykładowy wynik

```python
(
    [...],
    "pdfplumber"
)
```

#### Kiedy używać

Jest podstawowym sposobem ekstrakcji danych.

Zapewnia odporność na błędy pojedynczych silników.

---

# Funkcje modułu

## is_valid_table()

### Przeznaczenie

Weryfikuje podstawową poprawność tabeli.

Tabela jest uznawana za poprawną, gdy posiada:

- więcej niż jeden wiersz,
- więcej niż jedną kolumnę.

---

### Sygnatura

```python
def is_valid_table(table):
```

### Parametry

#### table

Typ:

```python
dict
```

---

### Wartości zwracane

Typ:

```python
bool
```

---

### Przepływ działania

```text
odczyt liczby wierszy
 │
 ▼
odczyt liczby kolumn
 │
 ▼
sprawdzenie > 1
 │
 ▼
True/False
```

---

### Obsługa błędów

Wszystkie wyjątki są przechwytywane.

W przypadku błędu:

```python
False
```

---

### Przykład użycia

```python
is_valid_table(table)
```

### Przykładowy wynik

```python
True
```

### Kiedy używać

Przed zapisaniem danych do dokumentu Word.

Pozwala eliminować artefakty ekstrakcji.

---

## run_pipeline_with_metrics()

### Przeznaczenie

Główna funkcja modułu.

Koordynuje cały proces:

- wybór silnika,
- ekstrakcję danych,
- przetwarzanie równoległe,
- tworzenie dokumentu Word,
- obliczanie metryk.

---

### Sygnatura

```python
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
```

### Parametry

#### pdf_path

Typ:

```python
str
```

#### template_path

Typ:

```python
str
```

#### output_path

Typ:

```python
str
```

#### pdf_type

Typ:

```python
str
```

#### pages

Typ:

```python
int
```

Domyślnie:

```python
1
```

#### forced_engine

Typ:

```python
str
```

Domyślnie:

```python
"auto"
```

#### parallel

Typ:

```python
bool
```

Domyślnie:

```python
False
```

#### document

Typ:

```python
Document
```

lub

```python
None
```

---

### Wartości zwracane

Typ:

```python
dict
```

Struktura:

```python
{
    "tables_total": int,
    "tables_valid": int,
    "engine": str
}
```

---

### Przepływ działania

```text
START
 │
 ▼
EngineManager
 │
 ▼
wybór trybu
 │
 ├── auto
 ├── forced engine
 └── parallel
 │
 ▼
ekstrakcja
 │
 ▼
Word
 │
 ▼
metryki
 │
 ▼
wynik
```

---

### Obsługa błędów

Obsługiwane są:

- nieznane silniki,
- wyjątki silników ekstrakcyjnych,
- błędy fallback,
- błędy przetwarzania dokumentu.

#### Nieznany silnik

Zwracane jest:

```python
{
    "tables_total": 0,
    "tables_valid": 0,
    "engine": None
}
```

---

### Przykład użycia

```python
result = run_pipeline_with_metrics(
    pdf_path="input.pdf",
    template_path="template.docx",
    output_path="output.docx",
    pdf_type="auto"
)
```

### Przykładowy wynik

```python
{
    "tables_total": 5,
    "tables_valid": 4,
    "engine": "pdfplumber"
}
```

### Co robi przykład

Uruchamia pełny pipeline.

Tworzy dokument Word i zwraca metryki procesu.

### Kiedy jest przydatny

Jest podstawową funkcją produkcyjną modułu.

Powinna być wykorzystywana przez większość integracji.

---

## run_pipeline()

### Przeznaczenie

Uproszczony interfejs uruchomienia pipeline.

Deleguje wykonanie do:

```python
run_pipeline_with_metrics()
```

---

### Sygnatura

```python
def run_pipeline(
    pdf_path,
    template_path,
    output_path,
    pdf_type
):
```

---

### Parametry

Takie same jak pierwsze cztery parametry:

```python
run_pipeline_with_metrics()
```

---

### Wartości zwracane

Typ:

```python
dict
```

---

### Przykład użycia

```python
run_pipeline(
    "test.pdf",
    "template.docx",
    "result.docx",
    "auto"
)
```

### Kiedy używać

Gdy nie są potrzebne dodatkowe parametry konfiguracji.

---

## main()

### Przeznaczenie

Punkt wejścia interfejsu CLI.

---

### Sygnatura

```python
def main():
```

### Parametry

Brak.

### Wartości zwracane

Brak.

### Przepływ działania

```text
argparse
 │
 ▼
parse_args()
 │
 ▼
logging.basicConfig()
 │
 ▼
run_pipeline_with_metrics()
```

---

# Tryby pracy

## Auto

Automatyczny wybór silnika.

```python
forced_engine="auto"
```

---

## Forced Engine

Wymuszenie konkretnego silnika.

Przykład:

```python
forced_engine="ocr"
```

---

## Parallel

Uruchomienie:

```python
run_parallel()
```

jeżeli:

```python
parallel=True
```

oraz:

```python
pages > 1
```

---

# Multiprocessing

## Wykorzystanie

Moduł wykorzystuje multiprocessing pośrednio przez:

```python
run_parallel()
```

---

## Jednostka równoległości

Przetwarzanie stron PDF.

---

## Wpływ liczby stron

Tryb równoległy jest aktywowany wyłącznie dla:

```python
pages > 1
```

---

# Dashboard

Moduł nie generuje dashboardu.

---

# Raporty

Moduł nie generuje własnych raportów.

Wykorzystuje raport walidacji generowany przez:

```python
process_tables_to_word()
```

---

# Logowanie

## Co jest logowane

### Start pipeline

```text
=== START PIPELINE ===
```

### Parametry wejściowe

```text
PDF: ...
Typ PDF: ...
Tryb równoległy: ...
```

### Fallback

```text
Próba silnika: pdfplumber
```

### Wyniki

```text
Silnik pdfplumber znalazł 5 tabel
```

### Metryki

```text
Tabele: 5, poprawne: 4
```

### Błędy

```text
Nieznany silnik: ...
Silnik ... błąd: ...
```

### Koniec działania

```text
=== KONIEC PIPELINE ===
```

---

# Interfejs CLI

## Parametry

### --input

Ścieżka do pliku PDF.

### --template

Ścieżka do szablonu DOCX.

### --output

Ścieżka do pliku wynikowego DOCX.

### --engine

Nazwa silnika.

Domyślnie:

```text
auto
```

### --parallel

Włącza tryb równoległy.

### --pages

Liczba stron.

Domyślnie:

```text
1
```

---

## Przykłady użycia

### Standard

```bash
python3 tableimport.py \
  --input 0.pdf \
  --template szablon.docx \
  --output wynik.docx
```

### Wymuszenie OCR

```bash
python3 tableimport.py \
  --input 0.pdf \
  --template szablon.docx \
  --output wynik.docx \
  --engine ocr
```

### Tryb równoległy

```bash
python3 tableimport.py \
  --input 0.pdf \
  --template szablon.docx \
  --output wynik.docx \
  --parallel \
  --pages 20
```

---

# Przykłady integracji

## pdf2word_module.py

Przekazywane dane:

```python
tables
document
```

Odbierane dane:

```python
process_result
```

Rola:

Generowanie dokumentu DOCX.

---

## parallel_pipeline.py

Przekazywane dane:

```python
pdf_path
pdf_type
pages
```

Odbierane dane:

```python
results
```

Rola:

Równoległa ekstrakcja tabel.

---

## Engines

Przekazywane dane:

```python
pdf_path
```

Odbierane dane:

```python
tables
```

Rola:

Ekstrakcja danych.

---

# Przykłady produkcyjne

## Przetwarzanie standardowe

```python
result = run_pipeline_with_metrics(
    pdf_path="/data/input/report.pdf",
    template_path="/templates/report.docx",
    output_path="/output/report.docx",
    pdf_type="auto"
)
```

---

## OCR

```python
result = run_pipeline_with_metrics(
    pdf_path="/data/input/scan.pdf",
    template_path="/templates/report.docx",
    output_path="/output/scan.docx",
    pdf_type="auto",
    forced_engine="ocr"
)
```

---

## Parallel

```python
result = run_pipeline_with_metrics(
    pdf_path="/data/input/large.pdf",
    template_path="/templates/report.docx",
    output_path="/output/large.docx",
    pdf_type="auto",
    pages=100,
    parallel=True
)
```

---

# Wydajność

## Multiprocessing

Obsługiwany pośrednio przez:

```python
run_parallel()
```

## Potencjalne wąskie gardła

- ekstrakcja tabel,
- OCR,
- zapis dokumentów Word,
- agregacja wyników równoległych.

## Najbardziej obciążające CPU

- OCR,
- analiza tabel,
- przetwarzanie wielu stron.

## Najbardziej obciążające I/O

- odczyt PDF,
- zapis DOCX.

---

# Zależności

## logging

Przeznaczenie:

- logowanie procesu.

Dokumentacja:

https://docs.python.org/3/library/logging.html

---

## PdfPlumberEngine

Przeznaczenie:

- ekstrakcja tabel.

---

## CamelotEngine

Przeznaczenie:

- ekstrakcja tabel.

---

## OCREngine

Przeznaczenie:

- ekstrakcja tabel OCR.

---

## pdf2word_module

Przeznaczenie:

- generowanie dokumentów DOCX.

Wykorzystywane funkcje:

```python
create_document()
process_tables_to_word()
save_document()
```

---

## parallel_pipeline

Przeznaczenie:

- przetwarzanie równoległe.

Wykorzystywana funkcja:

```python
run_parallel()
```

---

# Powiązane moduły projektu

- checkpdf_module.md
- batch_pipeline.md
- pdf2word_module.md
- [metrics.md](metrics.md)
- parallel_pipeline.md

## checkpdf_module.py

Może dostarczać informację o typie dokumentu PDF.

## batch_pipeline.py

Może wielokrotnie uruchamiać pipeline dla wielu dokumentów.

## pdf2word_module.py

Odpowiada za generowanie dokumentów Word.

## metrics.py

Może wykorzystywać wynik zwrócony przez pipeline.

## parallel_pipeline.py

Realizuje równoległą ekstrakcję danych.

---

# Podsumowanie

Moduł `tableimport.py` jest centralnym komponentem integrującym proces ekstrakcji tabel z dokumentów PDF oraz generowania dokumentów Word. Zarządza silnikami ekstrakcyjnymi, realizuje fallback, obsługuje przetwarzanie równoległe i zwraca podstawowe metryki procesu.

Najważniejszym elementem modułu jest funkcja `run_pipeline_with_metrics()`, która realizuje kompletny przepływ danych od dokumentu PDF do dokumentu DOCX. Moduł pełni rolę warstwy orkiestracyjnej pomiędzy silnikami ekstrakcji, przetwarzaniem równoległym i eksportem do formatu Word.
