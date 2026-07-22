# Dashboard

## Cel modułu

Plik `dashboard.json` przechowuje podsumowanie wyników przetwarzania wsadowego dokumentów PDF.

Jego zadaniem jest zapis kluczowych metryk generowanych podczas działania modułu `batch_pipeline.py`. Dane zapisane w pliku mogą być wykorzystywane do monitorowania jakości ekstrakcji, analizy wydajności procesu oraz raportowania skuteczności działania systemu.

Plik nie zawiera logiki biznesowej ani kodu wykonywalnego. Stanowi trwały zapis wyników procesu przetwarzania.

---

# Miejsce modułu w architekturze systemu

Plik jest końcowym produktem procesu raportowania.

```text
PDF
 ↓
checkpdf_module.py
 ↓
tableimport.py
 ↓
EngineManager
 ↓
pdf2word_module.py
 ↓
Metrics
 ↓
dashboard.json
```

Dane zapisywane w pliku pochodzą z obiektu `Metrics`, który agreguje wyniki przetwarzania wszystkich dokumentów PDF.

---

# Architektura modułu

Plik ma postać pojedynczego dokumentu JSON.

```text
dashboard.json
│
├── total
├── ok
├── error
├── success_rate
├── tables_total
├── tables_valid
├── quality
├── total_time
├── avg_time
├── min_time
├── max_time
├── fallback_count
├── fallback_rate
├── engine_usage
└── pdf_types
```

---

# Diagram przepływu danych

```text
process_single()
        ↓
Metrics.add_result()
        ↓
Metrics.summary()
        ↓
summary
        ↓
dashboard.json
```

---

# Opis działania modułu

Po zakończeniu przetwarzania wszystkich dokumentów PDF moduł `batch_pipeline.py` wywołuje metodę:

```python
metrics.summary()
```

Wynik działania tej metody jest zapisywany do pliku:

```text
dashboard.json
```

Zapisywany obiekt zawiera zbiorcze informacje o:

- liczbie przetworzonych dokumentów,
- liczbie błędów,
- jakości ekstrakcji,
- czasie wykonania,
- wykorzystaniu silników ekstrakcji.

Dane są przechowywane w formacie JSON i mogą być odczytywane przez inne narzędzia raportujące.

---

# Struktura katalogów

Na podstawie kodu źródłowego można odtworzyć następującą strukturę:

```text
project/
│
├── input/
│
├── output/
│
├── batch_pipeline.py
├── checkpdf_module.py
├── tableimport.py
├── pdf2word_module.py
├── metrics.py
│
├── dashboard.json
└── batch.log
```

---

# Struktura danych

## Przykładowa zawartość

```json
{
  "total": 18,
  "ok": 18,
  "error": 0,
  "success_rate": 100.0,
  "tables_total": 46,
  "tables_valid": 46,
  "quality": 100.0,
  "total_time": 43.7,
  "avg_time": 2.43,
  "min_time": 0.14,
  "max_time": 10.52,
  "fallback_count": 0,
  "fallback_rate": 0.0,
  "engine_usage": {
    "pdfplumber": 18
  },
  "pdf_types": {}
}
```

---

# Pola raportu

## total

### Typ

```python
int
```

### Opis

Całkowita liczba dokumentów PDF uwzględnionych w raporcie.

### Przykład

```json
"total": 18
```

Oznacza, że przetworzono osiemnaście dokumentów PDF.

---

## ok

### Typ

```python
int
```

### Opis

Liczba dokumentów zakończonych sukcesem.

### Przykład

```json
"ok": 18
```

Wartość oznacza, że wszystkie dokumenty zostały przetworzone poprawnie.

---

## error

### Typ

```python
int
```

### Opis

Liczba dokumentów zakończonych błędem.

### Przykład

```json
"error": 0
```

Brak błędów podczas przetwarzania.

---

## success_rate

### Typ

```python
float
```

### Opis

Procent poprawnie przetworzonych dokumentów.

### Przykład

```json
"success_rate": 100.0
```

Oznacza pełną skuteczność procesu.

---

## tables_total

### Typ

```python
int
```

### Opis

Łączna liczba tabel wykrytych podczas przetwarzania wszystkich dokumentów.

### Przykład

```json
"tables_total": 46
```

---

## tables_valid

### Typ

```python
int
```

### Opis

Liczba tabel uznanych za poprawnie wyekstrahowane.

### Przykład

```json
"tables_valid": 46
```

---

## quality

### Typ

```python
float
```

### Opis

Procent poprawnych tabel względem wszystkich wykrytych tabel.

### Przykład

```json
"quality": 100.0
```

Oznacza, że wszystkie wykryte tabele zostały uznane za poprawne.

---

## total_time

### Typ

```python
float
```

### Opis

Łączny czas przetwarzania wszystkich dokumentów.

### Jednostka

```text
sekundy
```

### Przykład

```json
"total_time": 43.7
```

---

## avg_time

### Typ

```python
float
```

### Opis

Średni czas przetwarzania pojedynczego dokumentu.

### Przykład

```json
"avg_time": 2.43
```

---

## min_time

### Typ

```python
float
```

### Opis

Najkrótszy zarejestrowany czas przetwarzania dokumentu.

### Przykład

```json
"min_time": 0.14
```

---

## max_time

### Typ

```python
float
```

### Opis

Najdłuższy zarejestrowany czas przetwarzania dokumentu.

### Przykład

```json
"max_time": 10.52
```

---

## fallback_count

### Typ

```python
int
```

### Opis

Liczba przypadków wykorzystania mechanizmu fallback.

### Przykład

```json
"fallback_count": 0
```

W przedstawionym raporcie nie było konieczności użycia fallback.

---

## fallback_rate

### Typ

```python
float
```

### Opis

Procent operacji wykorzystujących fallback.

### Przykład

```json
"fallback_rate": 0.0
```

---

## engine_usage

### Typ

```python
dict
```

### Opis

Informacje o wykorzystaniu silników ekstrakcji.

### Przykład

```json
"engine_usage": {
  "pdfplumber": 18
}
```

Oznacza, że wszystkie dokumenty zostały przetworzone przy użyciu silnika `pdfplumber`.

---

## pdf_types

### Typ

```python
dict
```

### Opis

Statystyki dotyczące typów dokumentów PDF.

### Przykład

```json
"pdf_types": {}
```

W dostarczonym raporcie słownik jest pusty.

---

# Dashboard

Raport może zostać wyświetlony przez funkcję:

```python
print_dashboard(summary)
```

Przykładowa prezentacja danych:

```text
=== DASHBOARD ===

PDF total: 18

OK: 18

Errors: 0

Success rate: 100.0%

Tabele: 46

Poprawne: 46

Quality: 100.0%

Avg time: 2.43 s

Total time: 43.7 s

Engine usage:
    pdfplumber: 18
```

Dashboard umożliwia szybkie sprawdzenie jakości oraz wydajności całego procesu.

---

# Raporty

## dashboard.json

Plik generowany automatycznie po zakończeniu działania:

```python
run_batch()
```

Raport zapisywany jest za pomocą:

```python
json.dump(
    summary,
    f,
    indent=2,
    ensure_ascii=False
)
```

Format JSON pozwala na łatwą integrację z narzędziami analitycznymi, dashboardami oraz systemami raportowania.

---

# Logowanie

Plik `dashboard.json` samodzielnie nie generuje logów.

Informacje prezentowane w dashboardzie pochodzą z danych zbieranych podczas działania modułu:

```text
batch_pipeline.py
```

Zapisy logów wykonywane są do pliku:

```text
batch.log
```

---

# Interfejs CLI

Plik `dashboard.json` nie posiada własnego interfejsu CLI.

Jest tworzony automatycznie przez:

```python
batch_pipeline.py
```

---

# Przykłady integracji

## batch_pipeline.py

Tworzenie raportu:

```python
summary = metrics.summary()

with open(
    "dashboard.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        summary,
        f,
        indent=2,
        ensure_ascii=False
    )
```

Przekazywane dane:

```python
summary
```

Odbierane dane:

```python
dashboard.json
```

---

## metrics.py

Źródłem wszystkich informacji zapisanych w dashboardzie jest:

```python
Metrics
```

Moduł agreguje wyniki przetwarzania i buduje obiekt:

```python
summary
```

który później trafia do pliku JSON.

---

# Przykłady produkcyjne

## Odczyt dashboardu w Python

```python
import json

with open(
    "dashboard.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

print(
    data["success_rate"]
)
```

### Wynik

```text
100.0
```

Przykład pozwala wykorzystać raport jako źródło danych dla własnych dashboardów lub systemów raportowania.

---

## Analiza czasu przetwarzania

```python
import json

with open(
    "dashboard.json",
    encoding="utf-8"
) as f:
    data = json.load(f)

print(
    f"Średni czas: {data['avg_time']} s"
)
```

### Wynik

```text
Średni czas: 2.43 s
```

---

# Wydajność

Plik `dashboard.json` sam nie realizuje operacji obliczeniowych.

Przechowuje jednak informacje o wydajności procesu:

- całkowity czas wykonania,
- średni czas wykonania,
- minimalny czas wykonania,
- maksymalny czas wykonania,
- wykorzystanie silników ekstrakcji.

Na podstawie tych danych można analizować wpływ:

- liczby procesów multiprocessing,
- wielkości dokumentów PDF,
- jakości dokumentów,
- zastosowanego silnika ekstrakcji.

---

# Zależności

## json

Plik zapisany jest w formacie JSON.

Dokumentacja:

https://docs.python.org/3/library/json.html

---

# Powiązane moduły projektu

- [Batch Pipeline](batch_pipeline.ule.md
- [Tablemport.md
- [PDF to Word Module](pdftrics](metrics.md)
- [Parallel Pipelinemd

## batch_pipeline.py

Odpowiada za utworzenie pliku dashboard.json.

## checkpdf_module.py

Dostarcza metadane o dokumentach PDF.

## tableimport.py

Odpowiada za ekstrakcję danych.

## pdf2word_module.py

Generuje dokumenty DOCX.

## metrics.py

Tworzy obiekt podsumowania wykorzystywany do budowy dashboardu.

## parallel_pipeline.py

Może wpływać na statystyki wydajnościowe zapisane w dashboardzie.

---

# Podsumowanie

Plik `dashboard.json` jest końcowym raportem procesu przetwarzania dokumentów PDF. Zawiera zbiorcze informacje o jakości ekstrakcji, skuteczności działania pipeline, wykorzystaniu silników oraz wydajności całego procesu.

Stanowi podstawowe źródło danych dla monitoringu, raportowania oraz analiz wydajnościowych wykonywanych po zakończeniu przetwarzania dokumentów.
