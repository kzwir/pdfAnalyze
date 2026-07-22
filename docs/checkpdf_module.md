# Check PDF Module

## Cel modułu

Moduł `checkpdf_module.py` odpowiada za wstępną analizę dokumentów PDF przed uruchomieniem właściwego procesu przetwarzania danych.

Jego zadaniem jest sprawdzenie poprawności dokumentu, analiza zawartości, klasyfikacja typu PDF oraz wskazanie silnika, który powinien zostać wykorzystany podczas dalszej ekstrakcji danych. Dzięki temu pozostałe moduły systemu nie muszą samodzielnie analizować dokumentu i mogą skupić się wyłącznie na przetwarzaniu danych.

Moduł stanowi pierwszy etap całego pipeline PDF → DOCX.

---

# Miejsce modułu w architekturze systemu

`checkpdf_module.py` jest odpowiedzialny za analizę wejściowego dokumentu PDF i dostarczenie metadanych wykorzystywanych przez kolejne etapy przetwarzania.

```text
PDF
 ↓
checkpdf_module.py
 ↓
tableimport.py
 ↓
EngineManager
 ↓
PdfPlumberEngine
CamelotEngine
OCREngine
 ↓
pdf2word_module.py
 ↓
DOCX
```

Informacje zwracane przez moduł są wykorzystywane między innymi do:

- wyboru silnika ekstrakcji,
- określenia rodzaju dokumentu,
- wykrywania skanów wymagających OCR,
- wykrywania dokumentów uszkodzonych,
- obsługi dokumentów zabezpieczonych.

---

# Opis działania modułu

Proces działania modułu składa się z czterech etapów:

1. Walidacja dokumentu PDF.
2. Analiza zawartości dokumentu.
3. Klasyfikacja dokumentu.
4. Zwrócenie wyniku w postaci słownika Python.

Diagram procesu:

```text
PDF
 ↓
check_pdf_validity()
 ↓
analyze_pdf()
 ↓
classify()
 ↓
analyze_file()
 ↓
Wynik API
```

W większości przypadków pozostałe moduły systemu powinny korzystać wyłącznie z funkcji `analyze_file()`.

---

# Funkcje modułu

## check_pdf_validity()

### Przeznaczenie

Funkcja sprawdza, czy wskazany plik jest poprawnym dokumentem PDF.

W trakcie działania wykonywana jest próba otwarcia dokumentu, odczyt liczby stron oraz sprawdzenie informacji o szyfrowaniu. Funkcja jest wykorzystywana jako pierwszy etap walidacji dokumentu.

Jeżeli dokument jest uszkodzony lub nie może zostać odczytany, funkcja zwraca informację o błędzie.

---

### Sygnatura

```python
check_pdf_validity(path)
```

---

### Parametry

#### path

Typ:

```python
str
```

Ścieżka do analizowanego dokumentu PDF.

Przykład:

```python
path = "input/report.pdf"
```

---

### Wartość zwracana

Funkcja zwraca krotkę:

```python
(
    valid,
    pages,
    encrypted
)
```

#### valid

Typ:

```python
bool
```

Informacja, czy dokument jest poprawnym plikiem PDF.

---

#### pages

Typ:

```python
int
```

Liczba stron dokumentu.

W przypadku błędu może zawierać tekst błędu.

---

#### encrypted

Typ:

```python
bool
```

Informacja, czy dokument jest zaszyfrowany.

---

### Przykład użycia

```python
from checkpdf_module import (
    check_pdf_validity
)

valid, pages, encrypted = (
    check_pdf_validity(
        "input/report.pdf"
    )
)

print(valid)
print(pages)
print(encrypted)
```

Przykład pozwala szybko sprawdzić poprawność dokumentu bez wykonywania pełnej analizy zawartości. Funkcja jest szczególnie przydatna podczas testów lub budowy własnych narzędzi wykorzystujących dokumenty PDF.

---

## analyze_pdf()

### Przeznaczenie

Funkcja analizuje zawartość pierwszych stron dokumentu PDF.

Podczas działania zliczana jest długość tekstu, liczba obrazów oraz liczba wykrytych tabel. Informacje te są później wykorzystywane przez mechanizm klasyfikacji dokumentów.

Analizowane są jedynie pierwsze strony dokumentu, co pozwala znacząco ograniczyć czas działania dla dużych plików.

---

### Sygnatura

```python
analyze_pdf(
    path,
    max_pages=3
)
```

---

### Parametry

#### path

Typ:

```python
str
```

Ścieżka do dokumentu PDF.

---

#### max_pages

Typ:

```python
int
```

Maksymalna liczba stron analizowanych przez funkcję.

Domyślna wartość:

```python
3
```

Dla bardzo dużych dokumentów zwykle wystarcza analiza pierwszych stron w celu określenia charakteru dokumentu.

---

### Wartość zwracana

```python
{
    "text_len": 2450,
    "images": 1,
    "tables": 2
}
```

---

### Opis zwracanych pól

#### text_len

Łączna liczba znaków tekstu.

---

#### images

Liczba wykrytych obrazów.

---

#### tables

Liczba wykrytych tabel.

---

### Przykład użycia

```python
from checkpdf_module import (
    analyze_pdf
)

info = analyze_pdf(
    "input/report.pdf"
)

print(info)
```

Przykład umożliwia wykonanie samej analizy zawartości dokumentu bez jego klasyfikacji. Jest przydatny podczas testowania jakości ekstrakcji lub diagnozowania problematycznych plików PDF.

---

## classify()

### Przeznaczenie

Funkcja klasyfikuje dokument PDF na podstawie wyników wcześniej wykonanej analizy.

Na podstawie liczby znaków tekstu, liczby obrazów oraz liczby tabel określany jest typ dokumentu oraz rekomendowany silnik ekstrakcji danych.

Funkcja jest wykorzystywana przez główne API modułu.

---

### Sygnatura

```python
classify(
    info,
    encrypted
)
```

---

### Parametry

#### info

Typ:

```python
dict
```

Wynik zwrócony przez funkcję:

```python
analyze_pdf()
```

Przykład:

```python
{
    "text_len": 2800,
    "images": 0,
    "tables": 4
}
```

---

#### encrypted

Typ:

```python
bool
```

Informacja o szyfrowaniu dokumentu.

---

### Wartość zwracana

```python
(
    document_type,
    recommended_tool
)
```

Przykład:

```python
(
    "tekstowy tabelaryczny",
    "pdfplumber / camelot"
)
```

---

### Przykład użycia

```python
from checkpdf_module import (
    classify
)

info = {
    "text_len": 2500,
    "images": 0,
    "tables": 3
}

result = classify(
    info,
    False
)

print(result)
```

Przykład pokazuje wykorzystanie klasyfikatora niezależnie od analizy PDF. Może być używany podczas testów jednostkowych lub podczas rozwoju nowych reguł klasyfikacji.

---

## analyze_file()

### Przeznaczenie

Jest to główna funkcja publiczna modułu.

Łączy wszystkie wcześniejsze etapy w jedno wywołanie. Najpierw sprawdzana jest poprawność dokumentu, następnie wykonywana jest analiza zawartości, a na końcu klasyfikacja oraz wybór rekomendowanego silnika.

Jest to funkcja przeznaczona do wykorzystywania przez pozostałe moduły projektu.

---

### Sygnatura

```python
analyze_file(path)
```

---

### Parametry

#### path

Typ:

```python
str
```

Ścieżka do analizowanego dokumentu PDF.

Przykład:

```python
"input/report.pdf"
```

---

### Wartość zwracana

```python
{
    "file": "report.pdf",
    "exists": True,
    "valid_pdf": True,
    "encrypted": False,
    "pages": 5,
    "analysis": {
        "text_len": 2450,
        "images": 0,
        "tables": 4
    },
    "type": "tekstowy tabelaryczny",
    "recommended_tool": "pdfplumber / camelot"
}
```

---

### Opis zwracanych pól

#### file

Ścieżka lub nazwa pliku.

#### exists

Informacja, czy plik istnieje.

#### valid_pdf

Informacja, czy dokument jest poprawnym PDF.

#### encrypted

Informacja o szyfrowaniu dokumentu.

#### pages

Liczba stron dokumentu.

#### analysis

Wyniki analizy zawartości.

#### type

Typ dokumentu określony przez klasyfikator.

#### recommended_tool

Rekomendowany silnik przetwarzania.

---

### Przykład użycia

```python
from checkpdf_module import (
    analyze_file
)

result = analyze_file(
    "input/report.pdf"
)

print(result)
```

Jest to podstawowy i zalecany sposób korzystania z modułu. Jedno wywołanie zwraca wszystkie informacje potrzebne późniejszym etapom pipeline.

---

# Przykłady użycia

## Odczyt liczby stron

```python
result = analyze_file(
    "report.pdf"
)

print(
    result["pages"]
)
```

Przykład pokazuje jak pobrać liczbę stron analizowanego dokumentu. Informacja ta może zostać wykorzystana do szacowania czasu przetwarzania lub decyzji o użyciu multiprocessing.

---

## Odczyt typu dokumentu

```python
result = analyze_file(
    "report.pdf"
)

print(
    result["type"]
)
```

Przykład pozwala określić charakter dokumentu przed rozpoczęciem ekstrakcji danych. Może być wykorzystywany podczas budowy własnych reguł biznesowych.

---

## Odczyt rekomendowanego silnika

```python
result = analyze_file(
    "report.pdf"
)

print(
    result["recommended_tool"]
)
```

Wynik może zostać wykorzystany bezpośrednio przez moduł odpowiedzialny za ekstrakcję danych. Pozwala to automatycznie wybrać najlepszą metodę przetwarzania dokumentu.

---

# Przykłady integracji z innymi modułami

## Integracja z tableimport.py

```python
from checkpdf_module import (
    analyze_file
)

from tableimport import (
    run_pipeline_with_metrics
)

info = analyze_file(
    "input/report.pdf"
)

result = run_pipeline_with_metrics(
    pdf_path="input/report.pdf",
    template_path="szablon.docx",
    output_path="output/report.docx",
    pdf_type=info["type"]
)
```

Przykład pokazuje rzeczywiste użycie modułu w głównym pipeline projektu. Wynik klasyfikacji jest wykorzystywany do wyboru odpowiedniego silnika ekstrakcji danych.

---

# Uruchomienie z linii poleceń (CLI)

Moduł może działać jako samodzielne narzędzie diagnostyczne.

## Komenda

```bash
python3 checkpdf_module.py \
    --input input/report.pdf
```

---

## Przykładowy wynik

```json
{
  "file": "report.pdf",
  "exists": true,
  "valid_pdf": true,
  "encrypted": false,
  "pages": 5,
  "analysis": {
    "text_len": 2450,
    "images": 0,
    "tables": 4
  },
  "type": "tekstowy tabelaryczny",
  "recommended_tool": "pdfplumber / camelot"
}
```

Takie uruchomienie jest przydatne podczas testowania nowych dokumentów PDF lub diagnozowania problemów bez uruchamiania pełnego pipeline.

---

# Opis logowania

Moduł wykorzystuje bibliotekę:

```python
logging
```

Logi są generowane między innymi dla następujących sytuacji:

- niepoprawny PDF,
- błąd odczytu dokumentu,
- brak pliku,
- błąd analizy zawartości,
- zakończenie analizy.

Przykładowe wpisy:

```text
Plik nie istnieje: report.pdf

Bledny PDF: invalid file

Blad analizy PDF

Analiza PDF: {...}
```

---

# Opis zależności

## os

Biblioteka standardowa języka Python wykorzystywana do operacji na ścieżkach i plikach.

W module służy do sprawdzania istnienia pliku:

```python
os.path.exists()
```

Dokumentacja:

https://docs.python.org/3/library/os.html

---

## logging

Biblioteka standardowa języka Python odpowiedzialna za logowanie zdarzeń.

W module wykorzystywana jest do rejestrowania błędów i wyników analizy.

Dokumentacja:

https://docs.python.org/3/library/logging.html

---

## pdfplumber

Biblioteka służąca do ekstrakcji tekstu, tabel i obrazów z dokumentów PDF.

W module jest wykorzystywana podczas analizy zawartości dokumentu.

Dokumentacja:

https://github.com/jsvine/pdfplumber

Repozytorium:

https://github.com/jsvine/pdfplumber

---

## pypdf

Biblioteka służąca do odczytu dokumentów PDF.

W module jest wykorzystywana do walidacji dokumentu, odczytu liczby stron oraz wykrywania szyfrowania.

Dokumentacja:

https://pypdf.readthedocs.io/

Repozytorium:

https://github.com/py-pdf/pypdf

---

# Powiązane moduły projektu

## Batch Pipeline

Dokumentacja:

```markdown
batch_pipeline.md
```

Odpowiada za wsadowe przetwarzanie dokumentów PDF.

---

## Table Import

Dokumentacja:

```markdown
tableimport.md
```

Zarządza pipeline ekstrakcji danych i wyborem silnika.

---

## PDF to Word

Dokumentacja:

```markdown
pdf2word_module.md
```

Generuje dokumenty Word na podstawie wyekstrahowanych danych.

---

## Metrics

Dokumentacja:

```markdown
metrics.md
```

Odpowiada za zbieranie statystyk i generowanie dashboardu.

---

## Parallel Pipeline

Dokumentacja:

```markdown
parallel_pipeline.md
```

Obsługuje przetwarzanie równoległe dużych dokumentów.

---

# Podsumowanie

Moduł `checkpdf_module.py` odpowiada za wstępną analizę dokumentów PDF oraz przygotowanie informacji niezbędnych do dalszego przetwarzania. Łączy walidację dokumentu, analizę zawartości, klasyfikację oraz rekomendację odpowiedniego silnika ekstrakcji.

W większości przypadków pozostałe moduły projektu powinny korzystać z funkcji `analyze_file()`, ponieważ udostępnia ona komplet informacji potrzebnych do dalszej pracy pipeline PDF → DOCX.
