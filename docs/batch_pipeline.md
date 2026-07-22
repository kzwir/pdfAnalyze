# Batch Pipeline

## Cel modułu

Moduł `batch_pipeline.py` odpowiada za wsadowe przetwarzanie dokumentów PDF oraz integrację całego procesu ekstrakcji danych i generowania dokumentów Microsoft Word.

Jest głównym punktem wejścia aplikacji. Zarządza analizą dokumentów PDF, uruchamianiem pipeline ekstrakcji, wyborem trybu pracy, obsługą przetwarzania równoległego, zapisem wyników oraz generowaniem raportów końcowych.

Moduł integruje następujące komponenty:

- `checkpdf_module.py`
- `tableimport.py`
- `pdf2word_module.py`
- `metrics.py`

---

# Miejsce modułu w architekturze systemu

```text
PDF
 ↓
checkpdf_module.py
 ↓
tableimport.py
 ↓
EngineManager
 ↓
PdfPlumberEngine / CamelotEngine / OCREngine
 ↓
pdf2word_module.py
 ↓
DOCX
```

Moduł pełni rolę koordynatora procesu i zarządza przepływem danych oraz wyników pomiędzy wszystkimi elementami systemu.

---

# Architektura modułu

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

# Diagram przepływu danych

## Tryb single

```text
PDF
 ↓
analyze_file()
 ↓
run_pipeline_with_metrics()
 ↓
DOCX
 ↓
Metrics
 ↓
Dashboard
```

## Tryb merged

```text
PDF1
PDF2
PDF3
 ...
PDFN
 ↓
run_pipeline_with_metrics()
 ↓
Document
 ↓
wynik_zbiorczy.docx
```

## Tryb grouped

```text
PDF
 ↓
Grouping
 ↓
Document
 ↓
part_001.docx

Document
 ↓
part_002.docx
```

---

# Opis działania modułu

Moduł skanuje katalog wejściowy i wyszukuje wszystkie pliki PDF.

Każdy dokument jest analizowany za pomocą funkcji `analyze_file()` z modułu `checkpdf_module.py`. Jeżeli dokument jest poprawny, zostaje przekazany do funkcji `run_pipeline_with_metrics()` odpowiedzialnej za ekstrakcję danych.

W zależności od wybranego trybu pracy moduł:

- tworzy osobny dokument DOCX dla każdego PDF,
- scala wszystkie PDF do jednego dokumentu DOCX,
- grupuje PDF do wielu dokumentów DOCX.

Po zakończeniu pracy generowany jest dashboard i raport JSON.

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
└── templates/
    └── szablon.docx
```

---

# Funkcje modułu

# setup_logging()

## Przeznaczenie

Konfiguruje system logowania wykorzystywany przez cały moduł.

Tworzy konfigurację pliku logów `batch.log` oraz ustawia poziom logowania `INFO`.

Funkcja jest uruchamiana przez interfejs CLI przed rozpoczęciem przetwarzania danych.

## Sygnatura

```python
setup_logging()
```

## Parametry

Brak.

## Wartości zwracane

Brak.

## Przepływ działania

```text
setup_logging()
 ↓
logging.basicConfig()
 ↓
batch.log
```

## Obsługa błędów

Funkcja nie implementuje własnej obsługi wyjątków.

## Przykład użycia

```python
setup_logging()
```

## Przykładowy wynik

```text
batch.log
```

## Kiedy używać

Funkcję należy wywołać przed rozpoczęciem przetwarzania dokumentów PDF. Zapewnia ona jednolity mechanizm diagnostyczny dla wszystkich funkcji modułu.

---

# process_single()

## Przeznaczenie

Przetwarza pojedynczy dokument PDF.

Jest podstawową jednostką pracy wykorzystywaną przez multiprocessing. Wykonuje analizę dokumentu, uruchamia pipeline ekstrakcji danych i zwraca statystyki wykonania.

## Sygnatura

```python
process_single(args)
```

## Parametry

### args

```python
(
    pdf_path,
    template_path,
    output_dir
)
```

### pdf_path

Typ:

```python
str
```

Ścieżka do dokumentu PDF.

### template_path

Typ:

```python
str
```

Ścieżka do szablonu DOCX.

### output_dir

Typ:

```python
str
```

Katalog wynikowy.

## Wartości zwracane

### Sukces

```python
{
    "file": "input/report.pdf",
    "status": "ok",
    "engine": "pdfplumber",
    "tables_total": 5,
    "tables_valid": 5,
    "time": 1.82
}
```

### Błąd

```python
{
    "file": "input/report.pdf",
    "status": "error",
    "reason": "invalid_pdf"
}
```

## Przepływ działania

```text
PDF
 ↓
analyze_file()
 ↓
run_pipeline_with_metrics()
 ↓
DOCX
 ↓
metrics
```

## Obsługa błędów

Przechwytywane są wszystkie wyjątki:

```python
except Exception as e
```

W przypadku błędu funkcja:

- zapisuje wpis do logów,
- zwraca status `error`.

## Przykład użycia

```python
result = process_single(
    (
        "input/report.pdf",
        "templates/template.docx",
        "output"
    )
)
```

## Przykładowy wynik

```python
{
    "file": "input/report.pdf",
    "status": "ok",
    "engine": "pdfplumber",
    "tables_total": 4,
    "tables_valid": 4,
    "time": 1.65
}
```

## Kiedy używać

Funkcja jest przydatna podczas debugowania pipeline lub testowania pojedynczych dokumentów. Pozwala uruchomić pełne przetwarzanie bez konieczności przetwarzania całych katalogów.

---

# process_with_retry()

## Przeznaczenie

Uruchamia przetwarzanie pojedynczego dokumentu PDF z mechanizmem ponownych prób.

Wykorzystuje funkcję `process_single()` i automatycznie ponawia operację w przypadku niepowodzenia.

## Sygnatura

```python
process_with_retry(
    args,
    retries=2
)
```

## Parametry

| Parametr | Typ | Opis |
|-----------|-----------|-----------|
| args | tuple | Parametry wejściowe dla process_single() |
| retries | int | Liczba ponownych prób |

## Przepływ działania

```text
process_single()
 ↓
error
 ↓
retry
 ↓
process_single()
 ↓
success lub error
```

## Przykład użycia

```python
result = process_with_retry(
    (
        "input/example.pdf",
        "templates/template.docx",
        "output"
    ),
    retries=3
)
```

## Przykładowy wynik

```python
{
    "status": "ok",
    "engine": "pdfplumber"
}
```

## Kiedy używać

Funkcja jest zalecana podczas pracy produkcyjnej, gdy ważna jest odporność procesu na chwilowe błędy lub problemy z plikami wejściowymi.

---

# Tryby pracy

## single

Dla każdego PDF tworzony jest osobny dokument DOCX.

```text
0.pdf → 0.docx
1.pdf → 1.docx
2.pdf → 2.docx
```

## merged

Wszystkie dokumenty PDF są łączone w jeden dokument Word.

```text
0.pdf
1.pdf
2.pdf
 ↓
wynik_zbiorczy.docx
```

## grouped

PDF są grupowane do wielu dokumentów DOCX.

```text
25 PDF
group_size = 10
```

Wynik:

```text
part_001.docx
part_002.docx
part_003.docx
```

---

# Multiprocessing

Moduł wykorzystuje:

```python
multiprocessing.Pool
```

Domyślna konfiguracja:

```python
workers = min(cpu_count(), 4)
```

Przetwarzanie równoległe wykorzystywane jest wyłącznie w trybie `single`.

---

# Dashboard

Po zakończeniu przetwarzania wyświetlane jest podsumowanie:

```text
=== DASHBOARD ===

PDF total: 120
OK: 118
Errors: 2

Tabele: 456
Poprawne: 441

Quality: 96.71%
```

---

# Raporty

## dashboard.json

Przykład:

```json
{
  "total": 120,
  "ok": 118,
  "error": 2,
  "success_rate": 98.33
}
```

---

# Interfejs CLI

## Parametry

```bash
--input-dir
--template
--output-dir
--workers
--merge-mode
--group-size
```

## Przykład

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template templates/szablon.docx \
    --output-dir output \
    --workers 4 \
    --merge-mode single
```

---

# Powiązane moduły projektu

- checkpdf_module.md
- [ableimport.md
- [PDF to Word Module](pdf2word](metrics.md)
- [Parallel Pipelinemd

## checkpdf_module.py

Odpowiada za analizę i klasyfikację dokumentów PDF.

## tableimport.py

Realizuje główny pipeline ekstrakcji danych.

## pdf2word_module.py

Odpowiada za generowanie dokumentów Microsoft Word.

## metrics.py

Agreguje statystyki oraz generuje dashboard.

## parallel_pipeline.py

Rozszerza możliwości przetwarzania równoległego.

---

# Podsumowanie

Moduł `batch_pipeline.py` jest centralnym elementem procesu wsadowego przetwarzania dokumentów PDF. Odpowiada za zarządzanie analizą dokumentów, uruchamianie pipeline ekstrakcji danych, generowanie dokumentów DOCX, zbieranie metryk oraz tworzenie raportów końcowych.

Najczęściej wykorzystywanym punktem wejścia jest funkcja `run_batch()`, która umożliwia przetwarzanie całych katalogów PDF w trybie pojedynczym, grupowanym lub scalonym.
