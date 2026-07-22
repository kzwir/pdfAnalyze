# Batch Pipeline

## Opis modułu

Moduł `batch_pipeline.py` odpowiada za wsadowe przetwarzanie dokumentów PDF oraz integrację całego procesu ekstrakcji danych i generowania dokumentów Microsoft Word.

Jest głównym punktem wejścia aplikacji i zarządza pełnym przepływem:

```text
PDF
 ↓
checkpdf_module
 ↓
tableimport
 ↓
EngineManager
 ↓
pdfplumber / camelot / OCR
 ↓
pdf2word_module
 ↓
DOCX
```

Moduł realizuje:

- wsadowe przetwarzanie dokumentów PDF
- multiprocessing
- automatyczny retry błędów
- generowanie dokumentów DOCX
- scalanie wielu PDF do jednego DOCX
- grupowanie PDF do wielu DOCX
- zbieranie metryk jakości
- generowanie dashboardu
- zapis raportu JSON
- generowanie logów procesu

---

# Architektura

```text
run_batch()
    │
    ├── process_single()
    │
    ├── process_with_retry()
    │
    ├── run_merged()
    │
    ├── run_grouped()
    │
    ├── print_dashboard()
    │
    └── dashboard.json
```

---

# Funkcje

## setup_logging()

Konfiguruje system logowania aplikacji.

### Parametry

Brak.

### Wynik

Tworzy plik:

```text
batch.log
```

### Format logów

```text
2026-07-21 14:10:53 INFO START: input/0.pdf
```

---

## process_single()

Przetwarza pojedynczy dokument PDF.

### Parametry

```python
(
    pdf_path,
    template_path,
    output_dir
)
```

### Proces

```text
PDF
 ↓
analyze_file()
 ↓
run_pipeline_with_metrics()
 ↓
wybór silnika
 ↓
generowanie DOCX
 ↓
metryki
```

### Przykładowy wynik

```python
{
    "file": "input/0.pdf",
    "status": "ok",
    "engine": "pdfplumber",
    "tables_total": 3,
    "tables_valid": 3,
    "time": 1.47
}
```

### Przykład błędu

```python
{
    "file": "input/0.pdf",
    "status": "error",
    "reason": "invalid_pdf"
}
```

---

## process_with_retry()

Uruchamia przetwarzanie pojedynczego PDF z obsługą ponownych prób.

### Sygnatura

```python
process_with_retry(
    args,
    retries=2
)
```

### Parametry

| Parametr | Opis |
|-----------|-----------|
| args | dane wejściowe dla process_single() |
| retries | liczba ponownych prób |

### Schemat działania

```text
PDF
 ↓
process_single()
 ↓
błąd
 ↓
Retry 1
 ↓
process_single()
 ↓
błąd
 ↓
Retry 2
 ↓
process_single()
 ↓
sukces lub error
```

### Maksymalna liczba uruchomień

```python
retries = 2
```

oznacza:

```text
3 próby wykonania
```

### Przykład logu

```text
START: input/0.pdf

ERROR:
input/0.pdf -> timeout

Retry 1 dla input/0.pdf

START: input/0.pdf

OK: input/0.pdf (1.32s)
```

### Przykład użycia

```python
from batch_pipeline import process_with_retry

result = process_with_retry(
    (
        "input/example.pdf",
        "szablon.docx",
        "output"
    ),
    retries=3
)

print(result)
```

### Przykładowy wynik

```python
{
    "file": "input/example.pdf",
    "status": "ok",
    "engine": "pdfplumber",
    "tables_total": 5,
    "tables_valid": 5,
    "time": 1.86
}
```

---

## run_merged()

Scala wiele dokumentów PDF do jednego pliku DOCX.

### Schemat działania

```text
PDF1
PDF2
PDF3
...
PDFN
 ↓
wynik_zbiorczy.docx
```

### Dokument wynikowy

```text
output/
└── wynik_zbiorczy.docx
```

### Zastosowania

- raporty okresowe
- dokumentacja projektowa
- archiwizacja dokumentów
- tworzenie raportów zbiorczych

---

## run_grouped()

Przetwarza wiele PDF do grup dokumentów DOCX.

### Parametry

```python
run_grouped(
    pdf_files,
    template_path,
    output_dir,
    group_size,
    metrics
)
```

### group_size

Określa liczbę PDF przypadających na jeden dokument.

### Przykład

```python
group_size = 10
```

Dla:

```text
25 PDF
```

zostaną utworzone:

```text
part_001.docx
part_002.docx
part_003.docx
```

---

## print_dashboard()

Wyświetla podsumowanie procesu.

### Przykład

```text
=== DASHBOARD ===

PDF total: 120

OK: 118

Errors: 2

Success rate: 98.33%

Tables total: 456

Valid tables: 441

Quality: 96.71%

Avg time: 1.84 s

Total time: 220.81 s

Engine usage:
    pdfplumber: 107
    camelot: 10
    ocr: 3
```

---

## run_batch()

Główna funkcja uruchamiająca przetwarzanie wsadowe.

### Sygnatura

```python
run_batch(
    input_dir,
    template_path,
    output_dir,
    workers=None,
    merge_mode="single",
    group_size=10
)
```

---

# Parametry

## input_dir

Katalog wejściowy zawierający pliki PDF.

Przykład:

```text
input/
```

---

## template_path

Szablon dokumentu Word.

Przykład:

```text
szablon.docx
```

---

## output_dir

Katalog wynikowy.

Przykład:

```text
output/
```

---

## workers

Liczba procesów wykorzystywanych do multiprocessing.

Przykład:

```python
workers=4
```

Domyślnie:

```python
min(cpu_count(), 4)
```

---

## merge_mode

Tryb przetwarzania.

Dostępne wartości:

```python
single
merged
grouped
```

---

## group_size

Liczba PDF przypadająca na jeden dokument w trybie grouped.

Przykład:

```python
group_size=10
```

---

# Tryby pracy

## single

Każdy PDF generuje własny plik DOCX.

### Przykład

```text
0.pdf → 0.docx
1.pdf → 1.docx
2.pdf → 2.docx
```

### Uruchomienie

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --workers 4 \
    --merge-mode single
```

---

## merged

Wszystkie PDF trafiają do jednego dokumentu DOCX.

### Przykład

```text
0.pdf
1.pdf
2.pdf
...
18.pdf
 ↓
wynik_zbiorczy.docx
```

### Uruchomienie

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --workers 4 \
    --merge-mode merged
```

---

## grouped

PDF są grupowane do wielu dokumentów DOCX.

### Przykład

```text
25 PDF
group_size=10
```

Wynik:

```text
part_001.docx
part_002.docx
part_003.docx
```

### Uruchomienie

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --merge-mode grouped \
    --group-size 10
```

---

# Multiprocessing

Moduł wykorzystuje:

```python
multiprocessing.Pool
```

### Domyślna konfiguracja

```python
workers = min(cpu_count(), 4)
```

### Korzyści

- wykorzystanie wielu rdzeni CPU
- szybsze przetwarzanie dużych zbiorów PDF
- lepsza skalowalność

---

# Dashboard

Po zakończeniu procesu generowane jest podsumowanie.

### Metryki

- liczba PDF
- liczba poprawnie przetworzonych plików
- liczba błędów
- współczynnik sukcesu
- liczba tabel
- liczba poprawnych tabel
- średni czas przetwarzania
- całkowity czas wykonania
- wykorzystanie silników

---

# Raport JSON

Automatycznie generowany plik:

```text
dashboard.json
```

### Przykład

```json
{
  "total": 120,
  "ok": 118,
  "error": 2,
  "success_rate": 98.33,
  "tables_total": 456,
  "tables_valid": 441,
  "avg_time": 1.84
}
```

---

# Logi

Wszystkie operacje są zapisywane do:

```text
batch.log
```

Rejestrowane są:

- rozpoczęcie procesu
- analiza PDF
- wybór silnika
- retry
- błędy
- zapis dokumentów
- dashboard
- zakończenie procesu

---

# Struktura katalogów

```text
project/
│
├── input/
│   ├── 0.pdf
│   ├── 1.pdf
│   └── ...
│
├── output/
│
├── batch_pipeline.py
├── checkpdf_module.py
├── tableimport.py
├── pdf2word_module.py
├── metrics.py
├── parallel_pipeline.py
│
├── engines/
│   ├── pdfplumber_engine.py
│   ├── camelot_engine.py
│   └── ocr_engine.py
│
├── dashboard.json
├── batch.log
│
├── templates/
    └── szablon.docx
```

---

# Powiązane moduły

## checkpdf_module.py

Analiza i klasyfikacja dokumentów PDF.

---

## tableimport.py

Główny pipeline ekstrakcji danych.

---

## pdf2word_module.py

Generowanie dokumentów DOCX.

---

## metrics.py

Zbieranie statystyk i generowanie dashboardu.

---

## parallel_pipeline.py

Przetwarzanie równoległe dużych dokumentów.

---

## engines/

Implementacje silników ekstrakcji:

- PdfPlumberEngine
- CamelotEngine
- OCREngine

---

# Wersja

Aktualna wersja modułu wspiera:

- multiprocessing
- retry
- dashboard
- JSON reporting
- single mode
- merged mode
- grouped mode
- EngineManager
- fallback extraction
- automatyczne zbieranie metryk
