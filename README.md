# Ekstrakcja tabel z PDF i generowanie dokumentów Word

Automatyczny pipeline do przetwarzania dokumentów PDF, ekstrakcji tabel oraz generowania raportów Microsoft Word (.docx).

Projekt obsługuje przetwarzanie pojedynczych plików oraz całych katalogów PDF przy użyciu wielu silników ekstrakcji, przetwarzania równoległego, mechanizmów fallback oraz systemu metryk jakości.

---

## Badges

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

---

# Spis treści

- Funkcjonalności
- Architektura
- Struktura projektu
- Instalacja
- Użycie
- Python API
- REST API (Roadmap)
- Dokumentacja
- Roadmap
- Autor
- Licencja

---

# Funkcjonalności

## PDF → Word

- ekstrakcja tabel z dokumentów PDF
- generowanie dokumentów DOCX
- obsługa szablonów Word
- raport walidacji danych
- automatyczna normalizacja tabel

---

## Obsługiwane silniki

- pdfplumber
- Camelot
- OCR (Tesseract)

Mechanizm fallback:

```text
pdfplumber
    ↓
camelot
    ↓
ocr
```

---

## Tryby pracy

### Single

Jeden PDF → Jeden DOCX

```text
a.pdf → a.docx
b.pdf → b.docx
c.pdf → c.docx
```

---

### Merged

Wiele PDF → Jeden DOCX

```text
a.pdf
b.pdf
c.pdf
    ↓
wynik_zbiorczy.docx
```

---

### Grouped

Wiele PDF → Kilka DOCX

Przykład:

```text
group_size = 10
```

```text
part_001.docx
part_002.docx
part_003.docx
```

---

## Multiprocessing

Przetwarzanie równoległe:

```python
workers = min(cpu_count(), 4)
```

---

## Dashboard

Generowane statystyki:

- liczba PDF
- liczba błędów
- skuteczność
- liczba tabel
- jakość tabel
- czas wykonania
- wykorzystanie silników

Przykład:

```text
=== DASHBOARD ===

PDF total: 120
OK: 118
Errors: 2

Success rate: 98.33%

Tables total: 456
Valid tables: 441

Engine usage:
   pdfplumber: 107
   camelot: 10
   ocr: 3
```

---

# Architektura

```text
PDF
 ↓
checkpdf_module
 ↓
EngineManager
 ↓
pdfplumber
 ↓
camelot
 ↓
ocr
 ↓
tableimport
 ↓
pdf2word_module
 ↓
DOCX
```

---

# Struktura projektu

```text
project/
│
├── input/
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
└── templates
    └── szablon.docx
```

---

# Instalacja

## Klonowanie repozytorium

```bash
git clone https://github.com/TWOJ_LOGIN/pdf-table-word-generator.git

cd pdf-table-word-generator
```

## Instalacja zależności

```bash
pip install -r requirements.txt
```

---

# Użycie

## Single

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --workers 4 \
    --merge-mode single
```

---

## Merged

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --workers 4 \
    --merge-mode merged
```

---

## Grouped

```bash
python3 batch_pipeline.py \
    --input-dir input \
    --template szablon.docx \
    --output-dir output \
    --merge-mode grouped \
    --group-size 10
```

---

# Python API

## Analiza PDF

```python
from checkpdf_module import analyze_file

result = analyze_file(
    "example.pdf"
)

print(result)
```

---

## Pipeline

```python
from tableimport import run_pipeline_with_metrics

result = run_pipeline_with_metrics(
    pdf_path="example.pdf",
    template_path="szablon.docx",
    output_path="wynik.docx",
    pdf_type="tekstowy tabelaryczny"
)

print(result)
```

---

## Batch Processing

```python
from batch_pipeline import run_batch

summary = run_batch(
    input_dir="input",
    template_path="szablon.docx",
    output_dir="output",
    workers=4,
    merge_mode="merged"
)

print(summary)
```

---

## Generowanie Word

```python
from pdf2word_module import (
    create_document,
    process_tables_to_word,
    save_document
)

document = create_document(
    "szablon.docx"
)

process_tables_to_word(
    tables=my_tables,
    document=document,
    source_name="example.pdf"
)

save_document(
    document,
    "wynik.docx"
)
```

---

# Dokumentacja

## Dokumentacja modułów

| Moduł | Opis | Dokumentacja |
|--------|--------|--------|
| `batch_pipeline.py` | Batch processing | [batch_pipeline.md](docs/batch_pipeline.md) |
| `checkpdf_module.py` | Analiza PDF | [checkpdf_module.md](docs/checkpdf_module.md) |
| `pdf2word_module.py` | Generowanie DOCX | [pdf2word_module.md](docs/pdf2word_module.md) |
| `tableimport.py` | Pipeline i EngineManager | [tableimport.md](docs/tableimport.md) |
| `metrics.py` | Dashboard i statystyki | [metrics.md](docs/metrics.md) |
| `parallel_pipeline.py` | Multiprocessing | [parallel_pipeline.md](docs/parallel_pipeline.md) |
| `engines/base_engine.py` | Bazowy interfejs silników | [base_engine.md](docs/base_engine.md) |
| `engines/pdfplumber_engine.py` | Silnik ekstrakcji PDFPlumber | [pdfplumber_engine.md](docs/pdfplumber_engine.md) |
| `engines/camelot_engine.py` | Silnik ekstrakcji Camelot | [camelot_engine.md](docs/camelot_engine.md) |
| `engines/ocr_engine.py` | Silnik OCR | [ocr_engine.md](docs/ocr_engine.md) |

---

## Dokumentacja bibliotek

### pdfplumber

https://github.com/jsvine/pdfplumber

### Camelot

https://camelot-py.readthedocs.io

### Tesseract

https://tesseract-ocr.github.io

### python-docx

https://python-docx.readthedocs.io

### pandas

https://pandas.pydata.org

### multiprocessing

https://docs.python.org/3/library/multiprocessing.html

---

# Autor

**Krzysztof Żwirek**

Project Manager | Software Engineering | Data Processing Automation

Warszawa, Polska

GitHub:

```text
https://github.com/kzwir
```

LinkedIn:

```text
https://pl.linkedin.com/in/krzysztof-zwirek
```

---

# Licencja

Projekt udostępniony na licencji MIT.

Szczegóły znajdują się w pliku LICENSE.
