# parallel_pipeline.py

## Cel modułu

Moduł `parallel_pipeline.py` odpowiada za równoległe przetwarzanie stron dokumentu PDF.

Jego zadaniem jest:

- równoległe uruchamianie ekstrakcji danych dla wielu stron PDF,
- wybór odpowiedniego silnika ekstrakcji,
- realizacja mechanizmu fallback pomiędzy silnikami,
- agregacja wyników poszczególnych stron,
- optymalizacja wykorzystania wielu rdzeni procesora,
- ograniczanie zużycia pamięci dla dużych dokumentów poprzez przetwarzanie paczkami,
- udostępnienie trybu strumieniowego dla stopniowego odbioru wyników.

Moduł realizuje przetwarzanie na poziomie pojedynczych stron dokumentu.

---

# Miejsce modułu w architekturze systemu

```text
PDF
 │
 ▼
checkpdf_module.py
 │
 ▼
parallel_pipeline.py
 │
 ├── PdfPlumberEngine
 ├── CamelotEngine
 └── OCREngine
         │
         ▼
   wyniki stron
         │
         ▼
tableimport.py
         │
         ▼
metrics.py
```

Moduł stanowi warstwę wykonawczą odpowiedzialną za równoległą ekstrakcję danych ze stron dokumentu PDF.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- zarządzanie procesami roboczymi (`Pool`),
- uruchamianie ekstrakcji dla pojedynczych stron,
- wybór obsługiwanych silników,
- obsługę fallback pomiędzy silnikami,
- agregację wyników,
- przetwarzanie dokumentów wielostronicowych,
- przetwarzanie strumieniowe wyników.

---

## Zakres odpowiedzialności

```text
parallel_pipeline.py
│
├── planowanie pracy
├── multiprocessing
├── fallback silników
├── przetwarzanie stron
├── chunking
└── streaming
```

---

## Poza zakresem modułu

Moduł nie odpowiada za:

- analizę dokumentu PDF,
- klasyfikację typu PDF,
- generowanie DOCX,
- zapis raportów,
- obliczanie metryk jakości,
- zapis dashboardów.

---

# Diagram przepływu danych

```text
PDF
 │
 ▼
lista stron
 │
 ▼
process_page()
 │
 ├── PdfPlumberEngine
 ├── CamelotEngine
 └── OCREngine
        │
        ▼
    wynik strony
        │
        ▼
 run_parallel()
 chunked_parallel()
 run_streaming()
        │
        ▼
 lista wyników
 lub
 generator wyników
```

---

# Opis działania modułu

Moduł przetwarza dokument PDF na poziomie pojedynczych stron.

Każda strona:

1. Trafia do procesu roboczego.
2. Przechodzi przez listę dostępnych silników.
3. Sprawdzana jest zgodność silnika z typem PDF.
4. Uruchamiana jest ekstrakcja.
5. Pierwszy poprawny wynik kończy dalsze próby fallback.
6. Wynik zostaje zwrócony do procesu nadrzędnego.

---

# Model danych

## Struktura wejściowa process_page()

```python
(
    pdf_path,
    page_num,
    pdf_type
)
```

Przykład:

```python
(
    "dokument.pdf",
    3,
    "tekstowy"
)
```

---

## Struktura wyniku

```python
{
    "page": 3,
    "engine": "pdfplumber",
    "tables": [...]
}
```

Jeżeli żaden silnik nie zwróci wyniku:

```python
{
    "page": 3,
    "engine": None,
    "tables": []
}
```

---

# Konfiguracja silników

## Lista silników

Kolejność wykonywania:

```python
ENGINES = [
    PdfPlumberEngine(),
    CamelotEngine(),
    OCREngine()
]
```

Kolejność jest jednocześnie kolejnością fallback.

---

# Mechanizm fallback

Dla każdej strony wykonywana jest następująca sekwencja:

```text
PdfPlumberEngine
        │
        ▼
CamelotEngine
        │
        ▼
OCREngine
```

Przejście do kolejnego silnika następuje gdy:

- silnik nie obsługuje danego typu PDF,
- wystąpi wyjątek,
- ekstrakcja nie zwróci tabel.

---

# Funkcje modułu

## process_page()

### Przeznaczenie

Przetwarza pojedynczą stronę dokumentu PDF.

Dla wskazanej strony próbuje kolejne silniki ekstrakcyjne aż do uzyskania poprawnego wyniku.

---

### Sygnatura

```python
def process_page(args):
```

---

### Parametry

#### args

Typ:

```python
tuple
```

Struktura:

```python
(
    pdf_path,
    page_num,
    pdf_type
)
```

##### pdf_path

Typ:

```python
str
```

Ścieżka dokumentu PDF.

##### page_num

Typ:

```python
int
```

Numer strony.

##### pdf_type

Typ:

```python
str
```

Typ dokumentu PDF.

---

### Wartości zwracane

Typ:

```python
dict
```

Przykład:

```python
{
    "page": 3,
    "engine": "pdfplumber",
    "tables": [...]
}
```

---

### Przepływ działania

```text
process_page()
 │
 ▼
iteracja po silnikach
 │
 ▼
supports()
 │
 ▼
extract_page()
 │
 ▼
wynik ?
 ├── TAK
 │     ▼
 │   return
 │
 └── NIE
       ▼
 kolejny silnik
```

---

### Obsługa błędów

Każde wywołanie:

```python
engine.extract_page(...)
```

znajduje się w bloku:

```python
try:
except Exception
```

W przypadku wyjątku:

```python
logging.error(...)
```

i wykonywana jest próba kolejnym silnikiem.

---

### Przykład użycia

```python
result = process_page(
    (
        "raport.pdf",
        5,
        "tekstowy"
    )
)
```

---

### Przykładowy wynik

```python
{
    "page": 5,
    "engine": "pdfplumber",
    "tables": [...]
}
```

---

### Kiedy używać

Funkcja jest przeznaczona do obsługi pojedynczej strony PDF.

Najczęściej wykorzystywana jest pośrednio przez funkcje równoległego przetwarzania.

---

## run_parallel()

### Przeznaczenie

Główna funkcja równoległego przetwarzania dokumentu PDF.

Każda strona dokumentu przekazywana jest do puli procesów roboczych.

---

### Sygnatura

```python
def run_parallel(
    pdf_path,
    pdf_type,
    pages,
    workers=None
):
```

---

### Parametry

#### pdf_path

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

Liczba stron.

#### workers

Typ:

```python
int | None
```

Domyślnie:

```python
min(cpu_count(), 4)
```

---

### Wartości zwracane

Typ:

```python
list
```

Lista wyników stron.

---

### Przepływ działania

```text
run_parallel()
 │
 ▼
utworzenie listy stron
 │
 ▼
Pool()
 │
 ▼
imap_unordered()
 │
 ▼
process_page()
 │
 ▼
results[]
```

---

### Obsługa błędów

Funkcja nie implementuje własnych bloków `try/except`.

Obsługa błędów przetwarzania stron realizowana jest przez `process_page()`.

---

### Przykład użycia

```python
results = run_parallel(
    pdf_path="raport.pdf",
    pdf_type="tekstowy",
    pages=20
)
```

---

### Przykładowy wynik

```python
[
    {
        "page": 1,
        "engine": "pdfplumber",
        "tables": [...]
    }
]
```

---

### Kiedy używać

Jest podstawowym trybem przetwarzania większości dokumentów PDF.

Najlepiej sprawdza się dla dokumentów średniej i dużej wielkości.

---

## chunked_parallel()

### Przeznaczenie

Przetwarza dokument PDF partiami stron.

Zmniejsza ilość danych obsługiwanych jednocześnie.

---

### Sygnatura

```python
def chunked_parallel(
    pdf_path,
    pdf_type,
    pages,
    chunk_size=5,
    workers=None
):
```

---

### Parametry

#### chunk_size

Typ:

```python
int
```

Domyślna wartość:

```python
5
```

Liczba stron w pojedynczej partii.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Przepływ działania

```text
chunk
 │
 ▼
Pool()
 │
 ▼
process_page()
 │
 ▼
wyniki chunka
 │
 ▼
kolejny chunk
```

---

### Obsługa błędów

Obsługa błędów wykonywana jest przez `process_page()`.

---

### Przykład użycia

```python
results = chunked_parallel(
    pdf_path="duzy.pdf",
    pdf_type="tekstowy",
    pages=300,
    chunk_size=10
)
```

---

### Przykładowy wynik

```python
[
    {"page": 1, "engine": "pdfplumber", "tables": [...]}
]
```

---

### Kiedy używać

Przeznaczone dla bardzo dużych dokumentów PDF.

Kod źródłowy wskazuje, że celem jest zmniejszenie zużycia pamięci RAM.

---

## run_streaming()

### Przeznaczenie

Przetwarza dokument PDF w trybie strumieniowym.

Wyniki są zwracane stopniowo podczas przetwarzania.

---

### Sygnatura

```python
def run_streaming(
    pdf_path,
    pdf_type,
    pages,
    workers=None
):
```

---

### Parametry

Takie same jak w `run_parallel()`.

---

### Wartości zwracane

Typ:

```python
generator
```

Realizowany przez:

```python
yield result
```

---

### Przepływ działania

```text
Pool()
 │
 ▼
process_page()
 │
 ▼
yield
 │
 ▼
kolejny wynik
```

---

### Obsługa błędów

Obsługa błędów wykonywana jest przez `process_page()`.

---

### Przykład użycia

```python
for result in run_streaming(
    pdf_path="raport.pdf",
    pdf_type="tekstowy",
    pages=20
):
    print(result)
```

---

### Przykładowy wynik

```python
{
    "page": 1,
    "engine": "pdfplumber",
    "tables": [...]
}
```

---

### Kiedy używać

Przeznaczone do scenariuszy, w których wyniki powinny być dostępne natychmiast po zakończeniu przetwarzania strony.

---

# Tryby pracy

## Standard

Funkcja:

```python
run_parallel()
```

Przeznaczenie:

```text
większość dokumentów PDF
```

---

## Chunking

Funkcja:

```python
chunked_parallel()
```

Przeznaczenie:

```text
bardzo duże dokumenty PDF
```

---

## Streaming

Funkcja:

```python
run_streaming()
```

Przeznaczenie:

```text
przetwarzanie w czasie rzeczywistym
```

---

# Multiprocessing

## Mechanizm

Moduł wykorzystuje:

```python
multiprocessing.Pool
```

oraz:

```python
cpu_count()
```

---

## Domyślna liczba procesów

```python
min(cpu_count(), 4)
```

---

## Jednostka równoległości

Jedna strona PDF stanowi jedno zadanie.

```text
1 strona PDF
    =
1 zadanie
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

### Start pipeline

```text
=== START PARALLEL PIPELINE ===
```

### Parametry

```text
Plik: ...
Strony: ...
Workers: ...
```

### Postęp przetwarzania

```text
Strona X: próba pdfplumber
```

### Wyniki ekstrakcji

```text
Strona X: pdfplumber znalazł Y tabel
```

### Błędy

```text
Strona X, silnik pdfplumber: ...
```

### Koniec przetwarzania

```text
=== KONIEC PARALLEL PIPELINE ===
```

---

# Interfejs CLI

Moduł nie zawiera:

```python
if __name__ == "__main__":
```

Nie udostępnia interfejsu CLI.

---

# Przykłady integracji

## checkpdf_module.py → parallel_pipeline.py

Przekazywane dane:

```python
pdf_type
```

Rola:

Informacja o typie dokumentu wykorzystywana przez:

```python
engine.supports(pdf_type)
```

---

## engines → parallel_pipeline.py

Przekazywane dane:

```python
extract_page(...)
```

Odbierane dane:

```python
tables
```

Rola:

Właściwa ekstrakcja danych.

---

## parallel_pipeline.py → metrics.py

Przekazywane dane:

```python
page
engine
tables
```

Rola:

Budowanie statystyk procesu.

---

# Przykłady produkcyjne

## Standardowe przetwarzanie

```python
results = run_parallel(
    pdf_path="/data/reports/report.pdf",
    pdf_type="tekstowy",
    pages=120
)
```

---

## Duży dokument

```python
results = chunked_parallel(
    pdf_path="/data/archive/archive.pdf",
    pdf_type="tekstowy",
    pages=1000,
    chunk_size=20
)
```

---

## Streaming

```python
for page_result in run_streaming(
    pdf_path="/data/live/live.pdf",
    pdf_type="tekstowy",
    pages=50
):
    print(page_result)
```

---

# Wydajność

## Wykorzystanie multiprocessing

Tak.

Mechanizm:

```python
Pool()
```

---

## Wpływ liczby workers

Większa liczba procesów umożliwia równoległe przetwarzanie większej liczby stron.

Kod ogranicza domyślną wartość do:

```python
4
```

---

## Potencjalne wąskie gardła

- ekstrakcja danych przez silniki,
- OCR,
- tworzenie i zamykanie puli procesów,
- transfer wyników pomiędzy procesami.

---

## Najbardziej obciążające CPU

- `extract_page()`,
- OCR,
- analiza tabel.

---

## Najbardziej obciążające I/O

- odczyt dokumentu PDF,
- komunikacja pomiędzy procesami.

---

# Zależności

## logging

Przeznaczenie:

- logowanie przebiegu działania.

Miejsce użycia:

```python
logging.debug(...)
logging.info(...)
logging.error(...)
```

Dokumentacja:

https://docs.python.org/3/library/logging.html

---

## multiprocessing.Pool

Przeznaczenie:

- realizacja przetwarzania równoległego.

Miejsce użycia:

```python
Pool(...)
```

Dokumentacja:

https://docs.python.org/3/library/multiprocessing.html

---

## multiprocessing.cpu_count

Przeznaczenie:

- określenie liczby rdzeni procesora.

Miejsce użycia:

```python
cpu_count()
```

Dokumentacja:

https://docs.python.org/3/library/multiprocessing.html

---

## PdfPlumberEngine

Przeznaczenie:

- pierwszy silnik ekstrakcji.

---

## CamelotEngine

Przeznaczenie:

- drugi silnik ekstrakcji.

---

## OCREngine

Przeznaczenie:

- trzeci silnik ekstrakcji.

---

# Powiązane moduły projektu

- checkpdf_module.md
- batch_pipeline.md
- tableimport.md
- pdf2word_module.md
- [Metrics](metrics.md)
- parallel_pipeline.md

## checkpdf_module.py

Dostarcza typ dokumentu PDF.

## tableimport.py

Może wykorzystywać wyniki przetwarzania stron.

## metrics.py

Może agregować wyniki generowane przez moduł.

## pdf2word_module.py

Może wykorzystywać dane wyekstrahowane przez silniki.

## engines

Dostarczają implementację ekstrakcji danych wykorzystywaną przez moduł.

---

# Podsumowanie

Moduł `parallel_pipeline.py` realizuje równoległe przetwarzanie stron dokumentów PDF z wykorzystaniem `multiprocessing.Pool`. Zapewnia mechanizm fallback pomiędzy trzema silnikami ekstrakcji oraz udostępnia trzy tryby pracy: standardowy, chunking i streaming.

Najczęściej wykorzystywaną funkcją jest `run_parallel()`, natomiast `chunked_parallel()` przeznaczone jest dla bardzo dużych dokumentów, a `run_streaming()` dla scenariuszy wymagających odbioru wyników w trakcie trwania przetwarzania.
