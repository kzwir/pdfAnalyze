# Główny Orchestrator PDF → Word

## Cel modułu

Moduł `glowny.py` pełni rolę głównego punktu wejścia aplikacji odpowiedzialnej za przetwarzanie pojedynczego dokumentu PDF do dokumentu Microsoft Word.

Jego zadaniem jest:

- analiza dokumentu PDF,
- wybór trybu przetwarzania,
- uruchomienie głównego pipeline ekstrakcji danych,
- przekazanie parametrów użytkownika do pipeline,
- rejestrowanie przebiegu procesu,
- prezentacja podsumowania wykonania.

Moduł nie realizuje samodzielnie analizy PDF, ekstrakcji tabel ani generowania dokumentów DOCX. Funkcjonalności te są delegowane do wyspecjalizowanych modułów projektu.

---

# Miejsce modułu w architekturze systemu

```text
PDF
 ↓
glowny.py
 ↓
checkpdf_module.py
 ↓
tableimport.py
 ↓
Engine
 ↓
pdf2word_module.py
 ↓
DOCX
```

Moduł stanowi warstwę orkiestracyjną odpowiedzialną za zarządzanie przepływem danych pomiędzy komponentami systemu.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł `glowny.py` odpowiada za:

- obsługę argumentów CLI,
- inicjalizację logowania,
- analizę dokumentu PDF,
- wybór trybu pracy sekwencyjnej lub równoległej,
- uruchomienie procesu ekstrakcji danych,
- agregację podstawowych wyników przetwarzania,
- prezentację podsumowania użytkownikowi.

Nie odpowiada za:

- analizę zawartości PDF,
- wykrywanie tabel,
- realizację OCR,
- wybór algorytmu ekstrakcji,
- generowanie dokumentu DOCX.

---

## Publiczne API modułu

Moduł udostępnia jedną funkcję wykonywalną:

```python
main()
```

Jest ona uruchamiana przez:

```python
if __name__ == "__main__":
    main()
```

---

## Funkcje wewnętrzne

W kodzie źródłowym znajduje się jedna aktywna funkcja:

```python
main()
```

W kodzie występuje również zakomentowana funkcja:

```python
setup_logging()
```

Nie jest ona jednak wykorzystywana, ponieważ logowanie pochodzi z modułu `logging_config`.

---

# Diagram przepływu danych

```text
CLI
 ↓
main()
 ↓
analyze_file()
 ↓
valid_pdf ?
 ├─ NIE → komunikat błędu
 │
 └─ TAK
      ↓
      wybór trybu pracy
      ↓
run_pipeline_with_metrics()
      ↓
pipeline_result
      ↓
summary
      ↓
terminal + logi
```

---

# Opis działania modułu

Po uruchomieniu moduł:

1. Odczytuje argumenty z linii poleceń.
2. Konfiguruje logowanie.
3. Analizuje dokument PDF przy użyciu `analyze_file()`.
4. Sprawdza poprawność dokumentu.
5. Ustala tryb pracy sekwencyjnej lub równoległej.
6. Uruchamia główny pipeline za pomocą `run_pipeline_with_metrics()`.
7. Oblicza czas wykonania.
8. Tworzy podsumowanie.
9. Wyświetla wyniki w terminalu.
10. Zapisuje informacje diagnostyczne do logów.

---

# Struktura katalogów

Na podstawie kodu można odtworzyć następującą strukturę:

```text
project/
│
├── glowny.py
├── checkpdf_module.py
├── tableimport.py
├── logging_config.py
│
├── logs/
│   └── main.log
│
├── input.pdf
├── szablon.docx
└── wynik.docx
```

---

# Wejście i wyjście

## Dane wejściowe

### Dokument PDF

```text
0.pdf
```

### Szablon Word

```text
szablon.docx
```

---

## Dane wyjściowe

### Dokument DOCX

```text
wynik.docx
```

---

## Dodatkowe artefakty

### Log

```text
logs/main.log
```

---

# Tabela funkcji modułu

| Funkcja | Przeznaczenie |
|----------|----------|
| `main()` | Główny orchestrator procesu PDF → DOCX |

---

# Funkcje modułu

# main()

## Przeznaczenie

Funkcja stanowi główny punkt wejścia programu.

Odpowiada za:

- odczyt parametrów CLI,
- analizę dokumentu PDF,
- wybór trybu wykonywania,
- uruchomienie pipeline,
- prezentację wyników.

---

## Sygnatura

```python
def main():
```

---

## Parametry

Funkcja nie przyjmuje parametrów bezpośrednio.

Dane wejściowe pobierane są z linii poleceń.

### --input

Typ:

```python
str
```

Ścieżka do dokumentu PDF.

---

### --template

Typ:

```python
str
```

Ścieżka do szablonu Word.

---

### --output

Typ:

```python
str
```

Ścieżka do pliku wynikowego DOCX.

---

### --engine

Typ:

```python
str
```

Domyślna wartość:

```python
"auto"
```

Parametr przekazywany do pipeline jako:

```python
forced_engine
```

---

### --parallel

Typ:

```python
bool
```

Flaga aktywująca tryb równoległy.

---

## Wartości zwracane

Brak jawnie zwracanej wartości.

W przypadku błędnego dokumentu PDF wykonywane jest:

```python
return
```

---

## Zależności wejścia/wyjścia

### Wejście

```python
args.input
args.template
args.output
args.engine
args.parallel
```

### Dane pośrednie

```python
result = analyze_file(...)
```

```python
pipeline_result = run_pipeline_with_metrics(...)
```

### Wyjście

```text
wynik.docx
```

oraz

```text
logs/main.log
```

---

## Przepływ działania

```text
CLI
 ↓
parse_args()
 ↓
setup_logging()
 ↓
analyze_file()
 ↓
valid_pdf ?
 ↓
wybór trybu pracy
 ↓
run_pipeline_with_metrics()
 ↓
summary
 ↓
print()
```

---

## Obsługa błędów

Funkcja nie zawiera bloku:

```python
try / except
```

Obsługuje natomiast niepoprawny dokument PDF:

```python
if not result.get("valid_pdf"):
```

W takim przypadku:

```python
logger.error(...)
```

oraz:

```python
return
```

Przykładowy komunikat:

```text
Błąd: plik PDF nie jest poprawny
```

---

## Przykład użycia

### Automatyczny wybór silnika

```bash
python3 glowny.py \
    --input a.pdf \
    --template t.docx \
    --output out.docx
```

### Wymuszenie OCR

```bash
python3 glowny.py \
    --input scan.pdf \
    --template t.docx \
    --output out.docx \
    --engine ocr
```

### Wymuszenie trybu równoległego

```bash
python3 glowny.py \
    --input duzy.pdf \
    --template t.docx \
    --output out.docx \
    --parallel
```

---

## Przykładowy wynik

```text
=== PODSUMOWANIE ===

Plik: a.pdf
Typ PDF: tekstowy
Strony: 12
Silnik: pdfplumber
Tabele: 6
Poprawne: 6
Czas: 3.24 s
```

### Co robi przykład

Program analizuje dokument PDF, uruchamia pipeline ekstrakcji danych oraz generuje dokument DOCX.

### Kiedy jest przydatny

Jest podstawowym sposobem uruchamiania procesu konwersji pojedynczego dokumentu PDF do Word.

---

## Kiedy używać

Funkcja powinna być wykorzystywana jako standardowy punkt wejścia dla użytkownika końcowego.

Jest odpowiednia dla przetwarzania pojedynczych dokumentów PDF oraz testowania konfiguracji silników ekstrakcji. Umożliwia łatwe sterowanie procesem z poziomu linii poleceń.

---

# Tryby pracy

## Sekwencyjny

Uruchamiany gdy:

```python
use_parallel == False
```

Log:

```text
Tryb: sekwencyjny
```

---

## Równoległy

Uruchamiany gdy:

```python
args.parallel == True
```

lub:

```python
pages > 10
```

Log:

```text
Tryb: rownolegoy
```

---

# Multiprocessing

Moduł nie tworzy procesów równoległych samodzielnie.

Przekazuje jednak parametr:

```python
parallel=use_parallel
```

do:

```python
run_pipeline_with_metrics()
```

Na podstawie kodu nie można określić sposobu implementacji przetwarzania równoległego w module docelowym.

---

# Dashboard

Moduł nie generuje dashboardu.

Prezentuje jedynie podsumowanie procesu:

```text
=== PODSUMOWANIE ===
```

wyświetlane na standardowym wyjściu.

---

# Raporty

Moduł nie zapisuje raportów JSON ani innych raportów plikowych.

Tworzy wyłącznie:

- logi,
- podsumowanie w terminalu.

---

# Logowanie

## Konfiguracja

Logowanie inicjalizowane jest poprzez:

```python
setup_logging(
    log_dir="logs",
    log_file="main.log",
    log_level="INFO"
)
```

---

## Lokalizacja logów

```text
logs/main.log
```

---

## Co jest logowane

### Start programu

```text
Start programu
```

### Start przetwarzania

```text
START przetwarzania
```

### Plik wejściowy

```text
Plik wejsciowy: a.pdf
```

### Typ PDF

```text
Typ PDF: tekstowy
```

### Tryb pracy

```text
Tryb: rownolegoy
```

lub

```text
Tryb: sekwencyjny
```

### Podsumowanie

```text
Podsumowanie: {...}
```

### Zakończenie

```text
KONIEC przetwarzania
```

### Błąd PDF

```text
Niepoprawny PDF - przerywam
```

---

# Interfejs CLI

## Parametry

| Parametr | Wymagany | Opis |
|-----------|-----------|-----------|
| `--input` | Tak | Plik PDF |
| `--template` | Tak | Szablon Word |
| `--output` | Tak | Plik DOCX |
| `--engine` | Nie | Wymuszenie silnika |
| `--parallel` | Nie | Włączenie trybu równoległego |

---

## Przykłady użycia

### Klasyczny tryb

```bash
python3 glowny.py \
    --input 0.pdf \
    --template szablon.docx \
    --output wynik.docx
```

### OCR

```bash
python3 glowny.py \
    --input scan.pdf \
    --template t.docx \
    --output out.docx \
    --engine ocr
```

### Parallel

```bash
python3 glowny.py \
    --input duzy.pdf \
    --template t.docx \
    --output out.docx \
    --parallel
```

---

# Przykłady integracji

## checkpdf_module.py

### Przekazywane dane

```python
args.input
```

### Odbierane dane

```python
{
    "valid_pdf": True,
    "type": "...",
    "pages": 12
}
```

### Rola

Analiza dokumentu PDF.

---

## tableimport.py

### Przekazywane dane

```python
pdf_path
template_path
output_path
pdf_type
pages
forced_engine
parallel
```

### Odbierane dane

```python
{
    "engine": "...",
    "tables_total": ...,
    "tables_valid": ...
}
```

### Rola

Realizacja głównego pipeline ekstrakcji danych.

---

## logging_config.py

### Przekazywane dane

```python
log_dir
log_file
log_level
```

### Odbierane dane

```python
logger
```

### Rola

Konfiguracja logowania.

---

# Przykłady produkcyjne

## Standardowe przetwarzanie

```bash
python3 /opt/project/glowny.py \
    --input /data/invoices/invoice_001.pdf \
    --template /templates/template.docx \
    --output /output/invoice_001.docx
```

---

## Wymuszenie OCR

```bash
python3 /opt/project/glowny.py \
    --input /data/scans/scan_001.pdf \
    --template /templates/template.docx \
    --output /output/scan_001.docx \
    --engine ocr
```

---

## Duży dokument

```bash
python3 /opt/project/glowny.py \
    --input /data/reports/report.pdf \
    --template /templates/template.docx \
    --output /output/report.docx \
    --parallel
```

---

# Wydajność

## Multiprocessing

Moduł nie implementuje multiprocessing bezpośrednio.

Przekazuje jedynie parametr:

```python
parallel=True
```

do pipeline.

---

## Wpływ liczby workers

W kodzie źródłowym brak parametru:

```python
workers
```

Nie można określić wpływu liczby procesów roboczych.

---

## Potencjalne wąskie gardła

Na podstawie kodu można wskazać:

- analizę dokumentu PDF,
- wykonanie pipeline ekstrakcji,
- zapis dokumentu DOCX.

---

## Najbardziej obciążające CPU/I/O

Moduł sam wykonuje jedynie operacje sterujące.

Największe obciążenie występuje w modułach:

- `checkpdf_module.py`,
- `tableimport.py`.

---

# Zależności

## argparse

### Przeznaczenie

Obsługa interfejsu CLI.

### Miejsce użycia

```python
argparse.ArgumentParser(...)
```

### Dokumentacja

https://docs.python.org/3/library/argparse.html

---

## logging

### Przeznaczenie

Logowanie zdarzeń.

### Miejsce użycia

```python
logging
```

### Dokumentacja

https://docs.python.org/3/library/logging.html

---

## time

### Przeznaczenie

Pomiar czasu wykonania.

### Miejsce użycia

```python
time.time()
```

### Dokumentacja

https://docs.python.org/3/library/time.html

---

## checkpdf_module

### Przeznaczenie

Analiza dokumentów PDF.

### Miejsce użycia

```python
analyze_file()
```

---

## tableimport

### Przeznaczenie

Uruchomienie pipeline ekstrakcji.

### Miejsce użycia

```python
run_pipeline_with_metrics()
```

---

## logging_config

### Przeznaczenie

Konfiguracja loggera.

### Miejsce użycia

```python
setup_logging(...)
```

---

# Powiązane moduły projektu

- checkpdf_module
- batch_pipeline.md
- [tableimport](tableimport.md)
- pdf2word_module.md
- [Metrics](metrics.md)
- parallel_pipeline.md

## checkpdf_module.py

Odpowiada za analizę i walidację dokumentów PDF przed rozpoczęciem przetwarzania.

### Integracja

```python
analyze_file(args.input)
```

---

## tableimport.py

Realizuje główny pipeline ekstrakcji danych.

### Integracja

```python
run_pipeline_with_metrics(...)
```

---

## pdf2word_module.py

Pośrednio wykorzystywany przez pipeline do generowania dokumentów DOCX.

---

## metrics.py

Moduł nie komunikuje się bezpośrednio z `metrics.py`.

Może być wykorzystywany pośrednio w pipeline.

---

## parallel_pipeline.py

Może być wykorzystywany przez pipeline po aktywacji trybu:

```python
parallel=True
```

Na podstawie dostarczonego kodu nie można potwierdzić szczegółów integracji.

---

# Podsumowanie

Moduł `glowny.py` jest głównym orchestratorem procesu konwersji PDF → Word dla pojedynczego dokumentu.

Odpowiada za analizę wejścia, wybór trybu pracy, przekazanie parametrów do pipeline, logowanie oraz prezentację wyników. Nie realizuje bezpośrednio ekstrakcji danych ani generowania dokumentów DOCX, lecz koordynuje współpracę wyspecjalizowanych modułów systemu.

Najczęstszym sposobem użycia jest uruchomienie programu z poziomu CLI przy użyciu parametrów `--input`, `--template` i `--output`, co prowadzi do wygenerowania pojedynczego dokumentu DOCX na podstawie wskazanego pliku PDF.
