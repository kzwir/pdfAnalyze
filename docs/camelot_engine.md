# camelot_engine.py

## Cel modułu

Moduł `camelot_engine.py` implementuje silnik ekstrakcji tabel oparty o bibliotekę Camelot.

Silnik odpowiada za:

- ekstrakcję tabel z dokumentów PDF,
- ekstrakcję tabel z pojedynczych stron PDF,
- automatyczny wybór trybu analizy tabel,
- fallback pomiędzy trybami Camelot,
- konwersję wyników Camelot do wspólnego formatu wykorzystywanego w systemie,
- dostarczanie informacji diagnostycznych o dokumencie.

Implementacja jest zgodna z architekturą opartą o klasę bazową `BaseEngine`.

---

# Miejsce modułu w architekturze systemu

```text
BaseEngine
    │
    ▼
CamelotEngine
    │
    ├── extract()
    ├── extract_page()
    ├── count_tables()
    └── get_document_info()
            │
            ▼
tableimport.py
            │
            ▼
parallel_pipeline.py
            │
            ▼
pdf2word_module.py
```

Moduł stanowi jedną z implementacji silników ekstrakcji danych.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- obsługę biblioteki Camelot,
- ekstrakcję tabel z PDF,
- obsługę trybu `lattice`,
- obsługę trybu `stream`,
- automatyczny fallback `lattice → stream`,
- konwersję wyników do formatu projektowego,
- logowanie błędów ekstrakcji,
- generowanie informacji diagnostycznych.

---

## Dziedziczenie

```python
class CamelotEngine(BaseEngine)
```

Silnik dziedziczy po:

```python
BaseEngine
```

---

## Architektura logiczna

```text
CamelotEngine
│
├── supports()
├── extract()
├── extract_page()
├── _try_lattice()
├── _try_stream()
├── count_tables()
└── get_document_info()
```

---

# Diagram przepływu danych

## Ekstrakcja całego dokumentu

```text
PDF
 │
 ▼
_try_lattice()
 │
 ├── znaleziono tabele
 │        │
 │        ▼
 │   konwersja wyniku
 │
 └── brak tabel
          │
          ▼
     _try_stream()
          │
          ▼
    konwersja wyniku
          │
          ▼
        wynik
```

---

## Ekstrakcja pojedynczej strony

```text
PDF
 │
 ▼
extract_page()
 │
 ▼
_try_lattice()
 │
 ├── wynik
 │
 └── brak wyniku
       │
       ▼
  _try_stream()
       │
       ▼
      wynik
```

---

# Opis działania modułu

Silnik wykorzystuje bibliotekę Camelot do identyfikacji tabel w dokumentach PDF.

Podczas ekstrakcji wykonywana jest próba użycia trybu:

```text
lattice
```

Jeżeli tryb ten nie zwróci tabel, wykonywana jest automatyczna próba:

```text
stream
```

Dzięki temu pojedyncze wywołanie silnika realizuje wewnętrzny mechanizm fallback pomiędzy metodami detekcji tabel.

---

# Model danych

## Struktura wyniku extract()

Zwracane rekordy mają postać:

```python
{
    "page": 1,
    "data": [...]
}
```

---

## Struktura listy wyników

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

---

## Struktura wyniku get_document_info()

```python
{
    "pages_with_tables": 5,
    "tables_found": 12,
    "engine": "camelot"
}
```

---

# Klasa CamelotEngine

## Przeznaczenie

Implementacja silnika ekstrakcji tabel bazującego na bibliotece Camelot.

Najlepiej sprawdza się dla dokumentów PDF zawierających tabele z dobrze zdefiniowaną strukturą.

---

## Dziedziczenie

```python
CamelotEngine(BaseEngine)
```

---

## Atrybuty klasy

### name

Typ:

```python
str
```

Wartość:

```python
"camelot"
```

Przeznaczenie:

Identyfikacja silnika w systemie.

---

# Funkcje modułu

Moduł nie zawiera funkcji globalnych.

Cała funkcjonalność została zaimplementowana w klasie `CamelotEngine`.

---

# Metody klasy CamelotEngine

## supports()

### Przeznaczenie

Określa, czy silnik obsługuje wskazany typ dokumentu PDF.

---

### Sygnatura

```python
def supports(self, pdf_type):
```

### Parametry

#### pdf_type

Typ:

```python
str
```

---

### Wartości zwracane

Typ:

```python
bool
```

---

### Obsługiwane typy PDF

```python
[
    "tekstowy tabelaryczny",
    "tekstowy",
    "tabelaryczny (slaba jakosc)"
]
```

---

### Przepływ działania

```text
pdf_type
 │
 ▼
sprawdzenie listy
 │
 ▼
True / False
```

---

### Obsługa błędów

Brak dedykowanej obsługi błędów.

---

### Przykład użycia

```python
engine.supports(
    "tekstowy tabelaryczny"
)
```

### Przykładowy wynik

```python
True
```

### Co robi przykład

Sprawdza możliwość użycia silnika dla wskazanego typu dokumentu.

### Kiedy używać

Przed rozpoczęciem ekstrakcji danych.

Pozwala wybrać odpowiedni silnik dla danego dokumentu.

---

## extract()

### Przeznaczenie

Ekstrakcja tabel z całego dokumentu PDF.

---

### Sygnatura

```python
def extract(self, pdf_path):
```

### Parametry

#### pdf_path

Typ:

```python
str
```

Ścieżka dokumentu PDF.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Przepływ działania

```text
_try_lattice()
 │
 ├── znaleziono tabele
 │
 ▼
konwersja wyniku
 │
 ▼
return
 │
 └── brak tabel
     │
     ▼
_try_stream()
     │
     ▼
konwersja wyniku
     │
     ▼
return
```

---

### Obsługa błędów

Obsługiwane są:

- błędy trybu lattice,
- błędy trybu stream,
- błędy konwersji tabel,
- błędy ekstrakcji dokumentu.

W przypadku błędów metoda zwraca pustą listę wyników.

---

### Przykład użycia

```python
tables = engine.extract(
    "raport.pdf"
)
```

### Przykładowy wynik

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

### Co robi przykład

Przetwarza cały dokument PDF.

### Kiedy używać

Gdy wymagane jest pobranie wszystkich tabel z dokumentu.

Jest to podstawowa metoda używana przez `tableimport.py`.

---

## extract_page()

### Przeznaczenie

Ekstrakcja tabel z pojedynczej strony PDF.

---

### Sygnatura

```python
def extract_page(
    self,
    pdf_path,
    page_num
):
```

### Parametry

#### pdf_path

Typ:

```python
str
```

#### page_num

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

### Przepływ działania

```text
_try_lattice()
 │
 ├── znaleziono tabelę
 │
 ▼
return
 │
 └── brak wyniku
     ▼
_try_stream()
     ▼
return
```

---

### Obsługa błędów

Błędy są logowane.

W przypadku wyjątku zwracana jest:

```python
[]
```

---

### Przykład użycia

```python
tables = engine.extract_page(
    "raport.pdf",
    5
)
```

### Przykładowy wynik

```python
[
    [...]
]
```

### Co robi przykład

Przetwarza pojedynczą stronę dokumentu.

### Kiedy używać

Podczas przetwarzania równoległego.

Metoda jest wykorzystywana przez `parallel_pipeline.py`.

---

## _try_lattice()

### Przeznaczenie

Wykonuje analizę dokumentu przy użyciu trybu:

```text
lattice
```

Tryb przeznaczony dla tabel posiadających linie pionowe i poziome.

---

### Sygnatura

```python
def _try_lattice(
    self,
    pdf_path,
    pages="all"
):
```

### Parametry

#### pdf_path

Typ:

```python
str
```

#### pages

Typ:

```python
str
```

Domyślnie:

```python
"all"
```

---

### Wartości zwracane

Typ:

Nie jest określony bezpośrednio w kodzie.

Metoda zwraca wynik `camelot.read_pdf()` lub pustą listę.

---

### Obsługa błędów

Błędy są logowane jako:

```python
logging.warning(...)
```

---

### Kiedy używać

Metoda wykorzystywana wewnętrznie przez silnik.

Nie jest wywoływana przez pozostałe moduły projektu.

---

## _try_stream()

### Przeznaczenie

Wykonuje analizę dokumentu w trybie:

```text
stream
```

Tryb przeznaczony dla tabel rozpoznawanych na podstawie układu tekstu.

---

### Sygnatura

```python
def _try_stream(
    self,
    pdf_path,
    pages="all"
):
```

### Parametry

Takie same jak `_try_lattice()`.

---

### Wartości zwracane

Takie same jak `_try_lattice()`.

---

### Obsługa błędów

Obsługiwane przez:

```python
logging.warning(...)
```

---

### Kiedy używać

Metoda wewnętrzna używana podczas fallback.

---

## count_tables()

### Przeznaczenie

Zwraca liczbę tabel wykrytych w dokumencie.

---

### Sygnatura

```python
def count_tables(
    self,
    pdf_path
):
```

### Parametry

#### pdf_path

Typ:

```python
str
```

---

### Wartości zwracane

Typ:

```python
int
```

---

### Przepływ działania

```text
extract()
 │
 ▼
len(...)
 │
 ▼
return
```

---

### Obsługa błędów

W przypadku błędu zwracane jest:

```python
0
```

---

### Przykład użycia

```python
count = engine.count_tables(
    "raport.pdf"
)
```

### Przykładowy wynik

```python
12
```

### Co robi przykład

Zlicza wszystkie wykryte tabele.

### Kiedy używać

Podczas generowania statystyk lub diagnostyki dokumentu.

---

## get_document_info()

### Przeznaczenie

Zwraca informacje diagnostyczne dotyczące dokumentu.

---

### Sygnatura

```python
def get_document_info(
    self,
    pdf_path
):
```

### Parametry

#### pdf_path

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

### Struktura wyniku

```python
{
    "pages_with_tables": X,
    "tables_found": Y,
    "engine": "camelot"
}
```

---

### Przepływ działania

```text
extract()
 │
 ▼
zliczanie stron
 │
 ▼
zliczanie tabel
 │
 ▼
budowa słownika
```

---

### Obsługa błędów

W przypadku błędu zwracane są wartości:

```python
{
    "pages_with_tables": 0,
    "tables_found": 0,
    "engine": "camelot"
}
```

---

### Przykład użycia

```python
info = engine.get_document_info(
    "raport.pdf"
)
```

### Przykładowy wynik

```python
{
    "pages_with_tables": 8,
    "tables_found": 15,
    "engine": "camelot"
}
```

### Co robi przykład

Generuje podsumowanie diagnostyczne dokumentu.

### Kiedy używać

Przy analizie skuteczności ekstrakcji oraz raportowaniu.

---

# Tryby pracy

## Lattice

Tryb:

```text
lattice
```

Przeznaczony dla tabel posiadających linie.

---

## Stream

Tryb:

```text
stream
```

Przeznaczony dla tabel identyfikowanych na podstawie układu tekstu.

---

## Fallback

Kolejność:

```text
lattice
↓
stream
```

---

# Multiprocessing

Silnik nie wykorzystuje multiprocessing.

Metoda:

```python
extract_page()
```

została przygotowana do współpracy z:

```text
parallel_pipeline.py
```

---

# Dashboard

Moduł nie generuje dashboardu.

---

# Raporty

Moduł nie generuje raportów.

---

# Logowanie

## Co jest logowane

### Błędy ekstrakcji

```text
camelot: błąd ekstrakcji 'plik.pdf': ...
```

### Błędy pojedynczej strony

```text
camelot: extract_page(5) błąd: ...
```

### Błędy konwersji tabel

```text
camelot: błąd konwersji tabeli: ...
```

### Ostrzeżenia lattice

```text
camelot lattice: ...
```

### Ostrzeżenia stream

```text
camelot stream: ...
```

### Fallback

```text
camelot: lattice nie znalazł tabel, próba stream
```

---

## Gdzie są zapisywane logi

Moduł nie definiuje konfiguracji logowania.

Wykorzystuje mechanizm:

```python
logging
```

a miejsce zapisu zależy od konfiguracji aplikacji nadrzędnej.

---

# Interfejs CLI

Moduł nie zawiera:

```python
if __name__ == "__main__":
```

Nie udostępnia interfejsu CLI.

---

# Przykłady integracji

## tableimport.py

Przekazywane dane:

```python
pdf_path
pdf_type
```

Odbierane dane:

```python
tables
engine_name
```

Rola:

Podstawowy silnik ekstrakcji.

---

## parallel_pipeline.py

Przekazywane dane:

```python
pdf_path
page_num
```

Odbierane dane:

```python
tables
```

Rola:

Ekstrakcja danych dla pojedynczych stron.

---

## pdf2word_module.py

Odbiera dane utworzone przez:

```python
extract()
```

w celu wygenerowania dokumentów Word.

---

# Przykłady produkcyjne

## Ekstrakcja całego dokumentu

```python
engine = CamelotEngine()

tables = engine.extract(
    "/data/reports/report.pdf"
)
```

---

## Ekstrakcja pojedynczej strony

```python
engine = CamelotEngine()

tables = engine.extract_page(
    "/data/reports/report.pdf",
    3
)
```

---

## Informacje diagnostyczne

```python
engine = CamelotEngine()

info = engine.get_document_info(
    "/data/reports/report.pdf"
)
```

---

# Wydajność

## Multiprocessing

Brak bezpośredniej implementacji.

## Potencjalne wąskie gardła

- odczyt PDF,
- analiza dokumentu przez Camelot,
- konwersja danych do list Python.

## Najbardziej obciążające CPU

- analiza tabel Camelot,
- przetwarzanie dużych dokumentów.

## Najbardziej obciążające I/O

- odczyt plików PDF.

---

# Zależności

## logging

### Przeznaczenie

Logowanie błędów i ostrzeżeń.

### Miejsce użycia

```python
logging.info()
logging.warning()
logging.error()
```

### Dokumentacja

https://docs.python.org/3/library/logging.html

---

## BaseEngine

### Przeznaczenie

Bazowy interfejs wszystkich silników.

### Miejsce użycia

```python
class CamelotEngine(BaseEngine)
```

---

## camelot

### Przeznaczenie

Ekstrakcja tabel z PDF.

### Miejsce użycia

```python
camelot.read_pdf()
```

### Dokumentacja

https://camelot-py.readthedocs.io/

### Repozytorium

https://github.com/camelot-dev/camelot

---

# Powiązane moduły projektu

- base_engine.md
- tableimport.md
- pdf2word_module.md
- parallel_pipeline.md
- [metrics.md](metrics.md)

## base_engine.py

Definiuje kontrakt implementowany przez CamelotEngine.

## tableimport.py

Wykorzystuje CamelotEngine jako jeden z silników ekstrakcyjnych.

## parallel_pipeline.py

Wykorzystuje metodę `extract_page()` do przetwarzania równoległego.

## pdf2word_module.py

Przetwarza dane zwrócone przez CamelotEngine do postaci DOCX.

## metrics.py

Może analizować wyniki zwracane przez silnik.

---

# Podsumowanie

Moduł `camelot_engine.py` implementuje silnik ekstrakcji tabel oparty na bibliotece Camelot. Obsługuje ekstrakcję całych dokumentów PDF oraz pojedynczych stron, wykorzystując dwa tryby rozpoznawania tabel: `lattice` i `stream`.

Najważniejszymi metodami są `extract()` oraz `extract_page()`. Moduł pełni rolę jednego z silników pluginowych wykorzystywanych przez architekturę opartą o `BaseEngine`, współpracując z `tableimport.py`, `parallel_pipeline.py` oraz `pdf2word_module.py`.
