# pdfplumber_engine.py

## Cel modułu

Moduł `pdfplumber_engine.py` implementuje silnik ekstrakcji danych oparty na bibliotece `pdfplumber`.

Jest to podstawowy silnik ekstrakcji wykorzystywany do przetwarzania dokumentów PDF zawierających tekst oraz tabele.

Moduł realizuje następujące zadania:

- ekstrakcję tabel z całego dokumentu PDF,
- ekstrakcję tabel z pojedynczej strony PDF,
- dostarczanie danych w formacie zgodnym z architekturą projektu,
- obsługę integracji z modułami `tableimport.py`, `parallel_pipeline.py` oraz `pdf2word_module.py`,
- obsługę typów dokumentów przypisanych do silnika pdfplumber.

Moduł implementuje interfejs zdefiniowany przez klasę `BaseEngine`.

---

# Miejsce modułu w architekturze systemu

```text
BaseEngine
    │
    ▼
PdfPlumberEngine
    │
    ├── supports()
    ├── extract()
    └── extract_page()
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

Moduł jest jednym z silników ekstrakcji danych i stanowi domyślny mechanizm przetwarzania dokumentów PDF.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- otwieranie dokumentów PDF,
- iterację po stronach PDF,
- ekstrakcję tabel ze stron,
- budowę wyników zgodnych z architekturą projektu,
- ekstrakcję pojedynczych stron dla przetwarzania równoległego.

---

## Dziedziczenie

```python
class PdfPlumberEngine(BaseEngine)
```

---

## Architektura logiczna

```text
PdfPlumberEngine
│
├── supports()
├── extract()
└── extract_page()
```

---

## Zakres odpowiedzialności

Silnik odpowiada wyłącznie za ekstrakcję danych.

Nie odpowiada za:

- walidację tabel,
- analizę jakości danych,
- generowanie dokumentów DOCX,
- raportowanie,
- zarządzanie fallback pomiędzy silnikami,
- logikę multiprocessing.

---

# Diagram przepływu danych

## Ekstrakcja całego dokumentu

```text
PDF
 │
 ▼
pdfplumber.open()
 │
 ▼
iteracja stron
 │
 ▼
extract_tables()
 │
 ▼
budowa struktury wyniku
 │
 ▼
lista tabel
```

---

## Ekstrakcja pojedynczej strony

```text
PDF
 │
 ▼
pdfplumber.open()
 │
 ▼
wybór strony
 │
 ▼
extract_tables()
 │
 ▼
wynik
```

---

# Opis działania modułu

Silnik wykorzystuje bibliotekę `pdfplumber` do odczytu dokumentów PDF.

Podczas przetwarzania całego dokumentu wykonywana jest iteracja po wszystkich stronach.

Każda tabela zwrócona przez metodę:

```python
page.extract_tables()
```

zostaje umieszczona w strukturze:

```python
{
    "page": page_num,
    "data": tabela
}
```

Wyniki są agregowane i zwracane jako lista.

---

# Model danych

## Nazwa silnika

Atrybut:

```python
name = "pdfplumber"
```

---

## Wynik extract()

Każda tabela zwracana jest w postaci:

```python
{
    "page": 1,
    "data": [...]
}
```

---

## Wynik końcowy extract()

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

---

## Wynik extract_page()

```python
[
    [...]
]
```

lub

```python
[]
```

---

# Klasa PdfPlumberEngine

## Przeznaczenie

Implementuje ekstrakcję danych przy użyciu biblioteki `pdfplumber`.

Przeznaczony jest przede wszystkim dla dokumentów:

- tekstowych,
- tekstowych tabelarycznych,
- mieszanych.

---

## Dziedziczenie

```python
PdfPlumberEngine(BaseEngine)
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
"pdfplumber"
```

Przeznaczenie:

Identyfikacja silnika w całym systemie.

---

# Funkcje modułu

Moduł nie definiuje funkcji globalnych.

Całość funkcjonalności została zaimplementowana jako metody klasy `PdfPlumberEngine`.

---

# Metody klasy PdfPlumberEngine

## supports()

### Przeznaczenie

Określa, czy silnik obsługuje wskazany typ dokumentu PDF.

---

### Sygnatura

```python
def supports(self, pdf_type):
```

---

### Parametry

#### pdf_type

Typ:

```python
str
```

Opis:

Typ dokumentu PDF.

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
    "tekstowy",
    "tekstowy tabelaryczny",
    "mieszany"
]
```

---

### Przepływ działania

```text
pdf_type
 │
 ▼
porównanie z listą
 │
 ▼
True / False
```

---

### Obsługa błędów

Metoda nie zawiera dedykowanej obsługi wyjątków.

---

### Przykład użycia

```python
engine = PdfPlumberEngine()

engine.supports(
    "tekstowy"
)
```

### Przykładowy wynik

```python
True
```

### Co robi przykład

Sprawdza możliwość wykorzystania silnika dla określonego typu dokumentu.

### Kiedy używać

Przed wyborem silnika ekstrakcji.

Pozwala określić zgodność typu dokumentu z możliwościami silnika.

---

## extract()

### Przeznaczenie

Realizuje ekstrakcję tabel z całego dokumentu PDF.

Przegląda wszystkie strony dokumentu i agreguje wszystkie odnalezione tabele.

---

### Sygnatura

```python
def extract(self, pdf_path):
```

---

### Parametry

#### pdf_path

Typ:

```python
str
```

Opis:

Ścieżka do pliku PDF.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Struktura zwracanych danych

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

---

### Zależności wejścia/wyjścia

#### Wejście

```python
pdf_path
```

#### Wyjście

```python
[
    {
        "page": numer_strony,
        "data": tabela
    }
]
```

---

### Przepływ działania

```text
pdfplumber.open()
 │
 ▼
iteracja stron
 │
 ▼
extract_tables()
 │
 ▼
utworzenie słowników
 │
 ▼
zbudowanie listy wyników
 │
 ▼
return
```

---

### Obsługa błędów

Metoda nie zawiera jawnej obsługi wyjątków.

Wszelkie wyjątki pochodzące z:

```python
pdfplumber.open()
```

lub

```python
extract_tables()
```

nie są przechwytywane lokalnie.

---

### Przykład użycia

```python
engine = PdfPlumberEngine()

tables = engine.extract(
    "report.pdf"
)
```

### Przykładowy wynik

```python
[
    {
        "page": 1,
        "data": [
            ["A", "B"],
            ["1", "2"]
        ]
    }
]
```

### Co robi przykład

Przetwarza cały dokument PDF i zwraca wszystkie znalezione tabele.

### Kiedy używać

Jest to podstawowa metoda ekstrakcyjna wykorzystywana przez `tableimport.py`.

Powinna być używana, gdy wymagane jest przetworzenie wszystkich stron dokumentu.

---

## extract_page()

### Przeznaczenie

Ekstrahuje tabele z pojedynczej strony dokumentu PDF.

Metoda została przygotowana do współpracy z modułem `parallel_pipeline.py`.

---

### Sygnatura

```python
def extract_page(
    self,
    pdf_path,
    page_num
):
```

---

### Parametry

#### pdf_path

Typ:

```python
str
```

Opis:

Ścieżka do dokumentu PDF.

#### page_num

Typ:

```python
int
```

Opis:

Numer strony dokumentu.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Możliwe wyniki

Jeżeli znaleziono tabele:

```python
[
    [...]
]
```

Jeżeli nie znaleziono tabel:

```python
[]
```

---

### Zależności wejścia/wyjścia

#### Wejście

```python
pdf_path
page_num
```

#### Wyjście

Lista tabel dla wskazanej strony.

---

### Przepływ działania

```text
pdfplumber.open()
 │
 ▼
wybór strony
 │
 ▼
extract_tables()
 │
 ▼
wynik
```

---

### Obsługa błędów

Metoda nie implementuje lokalnej obsługi wyjątków.

Wyjątki generowane przez:

```python
pdfplumber.open()
```

lub odczyt strony nie są przechwytywane.

---

### Przykład użycia

```python
engine = PdfPlumberEngine()

tables = engine.extract_page(
    "report.pdf",
    3
)
```

### Przykładowy wynik

```python
[
    [
        ["A", "B"],
        ["1", "2"]
    ]
]
```

### Co robi przykład

Przetwarza wyłącznie wskazaną stronę dokumentu.

### Kiedy używać

Podczas przetwarzania równoległego.

Pozwala ograniczyć zakres analizy do pojedynczej strony.

---

# Tryby pracy

Moduł nie definiuje własnych trybów pracy.

Obsługiwany jest jeden model działania oparty na bibliotece `pdfplumber`.

---

# Multiprocessing

Moduł nie implementuje mechanizmów multiprocessing.

Metoda:

```python
extract_page()
```

jest przygotowana do współpracy z:

```text
parallel_pipeline.py
```

który może realizować przetwarzanie równoległe.

---

# Dashboard

Moduł nie generuje dashboardu.

---

# Raporty

Moduł nie generuje raportów.

---

# Logowanie

Moduł nie wykorzystuje biblioteki:

```python
logging
```

Nie zapisuje logów.

Nie generuje komunikatów diagnostycznych.

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

### Przekazywane dane

```python
pdf_path
pdf_type
```

### Odbierane dane

```python
tables
```

### Rola modułu

Domyślny silnik ekstrakcji tabel.

---

## parallel_pipeline.py

### Przekazywane dane

```python
pdf_path
page_num
```

### Odbierane dane

```python
tables
```

### Rola modułu

Ekstrakcja tabel dla pojedynczych stron.

---

## pdf2word_module.py

### Przekazywane dane

Tabele zwrócone przez:

```python
extract()
```

### Odbierane dane

Brak.

### Rola modułu

Źródło danych wykorzystywanych do budowy dokumentów Word.

---

# Przykłady produkcyjne

## Ekstrakcja całego dokumentu

```python
from engines.pdfplumber_engine import PdfPlumberEngine

engine = PdfPlumberEngine()

tables = engine.extract(
    "/data/reports/report.pdf"
)
```

---

## Ekstrakcja pojedynczej strony

```python
from engines.pdfplumber_engine import PdfPlumberEngine

engine = PdfPlumberEngine()

tables = engine.extract_page(
    "/data/reports/report.pdf",
    10
)
```

---

## Sprawdzenie typu PDF

```python
engine = PdfPlumberEngine()

supported = engine.supports(
    "tekstowy"
)
```

Wynik:

```python
True
```

---

# Wydajność

## Multiprocessing

Nie jest implementowany bezpośrednio.

---

## Wpływ liczby workers

Nie dotyczy.

Moduł nie zarządza workerami.

---

## Potencjalne wąskie gardła

- otwieranie dużych dokumentów PDF,
- analiza stron zawierających wiele tabel,
- iteracja po wszystkich stronach dokumentu.

---

## Najbardziej obciążające CPU

- analiza stron wykonywana przez bibliotekę pdfplumber,
- ekstrakcja tabel dla dużych dokumentów.

---

## Najbardziej obciążające I/O

- odczyt dokumentu PDF z dysku.

---

# Zależności

## pdfplumber

### Przeznaczenie

Odczyt dokumentów PDF i ekstrakcja tabel.

### Miejsce użycia

```python
pdfplumber.open()
page.extract_tables()
```

### Dokumentacja

https://github.com/jsvine/pdfplumber

### Repozytorium

https://github.com/jsvine/pdfplumber

---

## BaseEngine

### Przeznaczenie

Bazowy interfejs silników ekstrakcji.

### Miejsce użycia

```python
class PdfPlumberEngine(BaseEngine)
```

### Dokumentacja

Dokumentacja projektu:

```text
base_engine.md
```

---

# Powiązane moduły projektu

- base_engine.md
- [tableimport.md](tableimport.md)
- pdf2word_module.md
- parallel_pipeline.md
- [metrics.md](metrics.md)

## base_engine.py

Definiuje kontrakt implementowany przez `PdfPlumberEngine`.

## tableimport.py

Wykorzystuje silnik jako domyślny mechanizm ekstrakcji danych.

## pdf2word_module.py

Przetwarza dane tabelaryczne zwrócone przez silnik i generuje dokumenty Word.

## parallel_pipeline.py

Wykorzystuje metodę `extract_page()` podczas przetwarzania pojedynczych stron.

## metrics.py

Może wykorzystywać dane zwracane przez pipeline korzystający z silnika pdfplumber.

---

# Podsumowanie

Moduł `pdfplumber_engine.py` implementuje podstawowy silnik ekstrakcji tabel wykorzystywany w architekturze przetwarzania PDF. Odpowiada za odczyt dokumentów PDF, ekstrakcję tabel oraz dostarczanie wyników w jednolitym formacie wykorzystywanym przez pozostałe komponenty systemu.

Najważniejszymi metodami są `extract()` oraz `extract_page()`. Moduł znajduje się w warstwie silników ekstrakcyjnych i współpracuje bezpośrednio z `tableimport.py`, `parallel_pipeline.py` oraz `pdf2word_module.py`.
