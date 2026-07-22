# metrics.py

## Cel modułu

Moduł `metrics.py` odpowiada za centralne gromadzenie, agregowanie oraz prezentowanie statystyk procesu przetwarzania dokumentów PDF.

Jego głównym zadaniem jest dostarczanie jednolitego mechanizmu monitorowania jakości procesu ekstrakcji danych oraz skuteczności przetwarzania dokumentów.

Moduł:

- agreguje wyniki wielu operacji przetwarzania,
- oblicza wskaźniki jakości,
- mierzy skuteczność przetwarzania,
- monitoruje wykorzystanie silników ekstrakcji,
- monitoruje wykorzystanie mechanizmów fallback,
- gromadzi statystyki czasowe,
- prezentuje dashboard tekstowy,
- udostępnia podsumowanie w postaci słownika.

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
 ▼
pdf2word_module.py
 │
 ▼
metrics.py
 │
 ├── agregacja wyników
 ├── statystyki jakości
 ├── statystyki czasu
 ├── statystyki PDF
 ├── statystyki silników
 ├── statystyki fallback
 │
 ▼
dashboard
```

Moduł nie wykonuje przetwarzania dokumentów.

Jego rolą jest wyłącznie analiza i agregacja rezultatów uzyskanych przez inne komponenty systemu.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- agregację wyników przetwarzania,
- zliczanie sukcesów i błędów,
- zliczanie tabel,
- wyliczanie jakości ekstrakcji,
- wyliczanie skuteczności procesu,
- analizę wykorzystania silników,
- analizę typów dokumentów,
- analizę fallback,
- wyliczanie statystyk czasowych,
- tworzenie dashboardu.

## Zakres odpowiedzialności

```text
Metrics
│
├── PDF statistics
├── Table statistics
├── Timing statistics
├── Engine statistics
├── Fallback statistics
└── PDF type statistics
```

## Poza zakresem modułu

Moduł nie wykonuje:

- analizy PDF,
- OCR,
- ekstrakcji tabel,
- zapisu DOCX,
- modyfikacji danych źródłowych,
- zapisu raportów do plików.

---

# Diagram przepływu danych

```text
result
 │
 ▼
add_result()
 │
 ├── total
 ├── ok/error
 ├── tables
 ├── engine
 ├── pdf_type
 ├── fallback
 └── time
         │
         ▼
      summary()
         │
         ▼
   print_dashboard()
```

---

# Opis działania modułu

Przetwarzanie przebiega w następującej kolejności:

1. Tworzony jest obiekt klasy `Metrics`.
2. Kolejne wyniki przekazywane są do `add_result()`.
3. Aktualizowane są liczniki i statystyki.
4. Obliczane są wskaźniki jakości.
5. Tworzone jest podsumowanie.
6. Dashboard jest prezentowany użytkownikowi.

---

# Model danych modułu

## Rekord wejściowy `result`

Moduł oczekuje słownika.

Obsługiwane pola:

```python
{
    "status": "ok",
    "tables_total": 5,
    "tables_valid": 4,
    "time": 1.25,
    "engine": "pdfplumber",
    "pdf_type": "tekstowy",
    "fallback_used": False
}
```

Żadne z pól poza `status` nie jest wymagane przez implementację.

W przypadku braku pól wykorzystywane są wartości domyślne.

---

# Atrybuty klasy Metrics

## Statystyki PDF

```python
total
ok
error
```

## Statystyki tabel

```python
tables_total
tables_valid
```

## Statystyki czasowe

```python
times
start_time
```

## Statystyki silników

```python
engine_usage
```

Typ:

```python
defaultdict(int)
```

## Statystyki fallback

```python
fallback_count
```

## Statystyki typów PDF

```python
pdf_types
```

Typ:

```python
defaultdict(int)
```

---

# Przepływ życia obiektu

```text
Metrics()
   │
   ▼
add_result()
   │
   ▼
add_result()
   │
   ▼
add_result()
   │
   ▼
summary()
   │
   ▼
print_dashboard()
```

---

# Funkcje modułu

## Klasa Metrics

### Przeznaczenie

Przechowuje zagregowane dane statystyczne dotyczące procesu przetwarzania dokumentów PDF.

Obiekt klasy jest tworzony raz dla całej sesji przetwarzania.

---

## `__init__()`

### Przeznaczenie

Inicjalizacja wszystkich struktur danych oraz rejestracja czasu rozpoczęcia działania modułu.

### Sygnatura

```python
def __init__(self):
```

### Parametry

Brak.

### Wartości zwracane

Brak.

### Kiedy używać

Przed rozpoczęciem agregacji wyników.

---

## `add_result()`

### Przeznaczenie

Dodaje wynik pojedynczego dokumentu do zbiorczych statystyk.

### Sygnatura

```python
def add_result(self, result):
```

### Parametry

#### result

Typ:

```python
dict
```

### Wartości zwracane

Brak.

### Przepływ działania

```text
result
 │
 ▼
aktualizacja PDF
 │
 ▼
aktualizacja tabel
 │
 ▼
aktualizacja silnika
 │
 ▼
aktualizacja czasu
 │
 ▼
aktualizacja fallback
```

### Obsługa błędów

Wszystkie odczyty wykonywane są przez:

```python
result.get(...)
```

Brakujące klucze nie powodują wyjątku.

### Przykład

```python
metrics.add_result({
    "status": "ok",
    "tables_total": 5,
    "tables_valid": 4,
    "time": 1.3,
    "engine": "pdfplumber"
})
```

### Przykładowy wynik

```python
metrics.total == 1
metrics.ok == 1
```

### Kiedy używać

Po zakończeniu przetwarzania pojedynczego dokumentu.

---

## `get_total_time()`

### Przeznaczenie

Zwraca czas działania obiektu od momentu utworzenia.

### Wartość zwracana

```python
float
```

---

## `get_average_time()`

### Przeznaczenie

Oblicza średni czas przetwarzania.

### Wartość zwracana

```python
float
```

Jeżeli lista czasów jest pusta:

```python
0
```

---

## `get_min_time()`

### Przeznaczenie

Zwraca minimalny czas przetwarzania.

### Wartość zwracana

```python
float
```

---

## `get_max_time()`

### Przeznaczenie

Zwraca maksymalny czas przetwarzania.

### Wartość zwracana

```python
float
```

---

## `get_success_rate()`

### Przeznaczenie

Wylicza procent poprawnie przetworzonych dokumentów.

### Wzór

```text
(ok / total) * 100
```

---

## `get_table_quality()`

### Przeznaczenie

Wylicza jakość ekstrakcji tabel.

### Wzór

```text
(tables_valid / tables_total) * 100
```

---

## `get_fallback_rate()`

### Przeznaczenie

Wylicza stopień wykorzystania mechanizmu fallback.

### Wzór

```text
(fallback_count / total) * 100
```

---

## `summary()`

### Przeznaczenie

Buduje pełne podsumowanie procesu.

### Sygnatura

```python
def summary(self):
```

### Wartość zwracana

```python
dict
```

### Klucze wyniku

```python
total
ok
error
success_rate
tables_total
tables_valid
quality
total_time
avg_time
min_time
max_time
fallback_count
fallback_rate
engine_usage
pdf_types
```

### Kiedy używać

Przy budowaniu raportów, dashboardów lub statystyk.

---

## `print_dashboard()`

### Przeznaczenie

Wyświetla dashboard tekstowy.

### Sygnatura

```python
def print_dashboard(self):
```

### Wartości zwracane

Brak.

### Przykładowy wynik

```text
===================================
           DASHBOARD
===================================

PDF total      : 2
OK             : 1
Errors         : 1
Success rate   : 50.0 %

Tabele         : 5
Poprawne       : 4
Quality        : 80.0 %

Total time     : 12.4 s
Average time   : 0.88 s

Engine usage:
  pdfplumber: 1
```

### Kiedy używać

Po zakończeniu przetwarzania wsadowego.

---

# KPI wyliczane przez moduł

## Success Rate

```text
(ok / total) * 100
```

Określa skuteczność procesu.

## Table Quality

```text
(tables_valid / tables_total) * 100
```

Określa jakość ekstrakcji tabel.

## Fallback Rate

```text
(fallback_count / total) * 100
```

Określa poziom wykorzystania mechanizmów awaryjnych.

---

# Dashboard

Dashboard prezentuje:

- liczbę dokumentów,
- liczbę sukcesów,
- liczbę błędów,
- skuteczność procesu,
- jakość ekstrakcji,
- czasy wykonania,
- wykorzystanie silników,
- wykorzystanie fallback,
- typy PDF.

---

# Kontrakty integracyjne

## Wejście

```python
dict result
```

## Wyjście

```python
summary()
```

oraz

```python
print_dashboard()
```

---

# Scenariusze użycia

## Analiza pojedynczego wsadu

```python
metrics = Metrics()

for result in results:
    metrics.add_result(result)

metrics.print_dashboard()
```

## Generowanie raportu

```python
summary = metrics.summary()
```

---

# Ograniczenia implementacji

Aktualna implementacja:

- nie zapisuje wyników do pliku,
- nie eksportuje danych do JSON,
- nie zapisuje dashboardu,
- nie wykorzystuje multiprocessing,
- nie zapisuje historii pomiarów,
- nie posiada trwałego magazynu danych.

---

# Multiprocessing

Moduł nie wykorzystuje multiprocessing.

---

# Logowanie

Moduł nie wykorzystuje biblioteki `logging`.

---

# Interfejs CLI

Moduł nie zawiera:

```python
if __name__ == "__main__":
```

Nie posiada interfejsu CLI.

---

# Wydajność

## Złożoność

Dodanie pojedynczego wyniku:

```text
O(1)
```

Obliczenie większości metryk:

```text
O(1)
```

Wyliczenie średniej:

```text
O(n)
```

gdzie:

```text
n = liczba zapisanych czasów
```

## Obciążenie CPU

Największe koszty:

- sumowanie czasów,
- obliczenia procentowe.

## Obciążenie I/O

Jedyną operacją I/O jest:

```python
print()
```

---

# Zależności

## time

Przeznaczenie:

- pomiar czasu działania modułu.

Użycie:

```python
time.time()
```

Dokumentacja:

https://docs.python.org/3/library/time.html

---

## collections.defaultdict

Przeznaczenie:

- automatyczne zliczanie wartości.

Użycie:

```python
defaultdict(int)
```

Dokumentacja:

https://docs.python.org/3/library/collections.html#collections.defaultdict

---

# Powiązane moduły projektu

- checkpdf_module.md
- batch_pipeline.md
- tableimport.md
- pdf2word_module.md
- [Metrics](metrics.md)
- parallel_pipeline.md

## checkpdf_module.py

Dostarcza informacje o typach dokumentów PDF.

## tableimport.py

Generuje większość danych agregowanych przez Metrics.

## batch_pipeline.py

Przekazuje wyniki do:

```python
metrics.add_result()
```

oraz wykorzystuje:

```python
summary()
```

## pdf2word_module.py

Pośrednio uczestniczy w procesie, którego wyniki są mierzone przez Metrics.

## parallel_pipeline.py

Może dostarczać wyniki do agregacji.

---

# Podsumowanie

Moduł `metrics.py` stanowi centralny komponent monitorowania jakości procesu przetwarzania dokumentów PDF. Odpowiada za agregację wyników, obliczanie KPI, analizę jakości ekstrakcji, analizę skuteczności przetwarzania oraz prezentację dashboardu tekstowego.

Najważniejszym elementem modułu jest klasa `Metrics`, która pełni funkcję repozytorium metryk dla całego procesu przetwarzania i dostarcza zunifikowany interfejs raportowania wykorzystywany przez pozostałe komponenty systemu.
