# ocr_engine.py

## Cel modułu

Moduł `ocr_engine.py` implementuje silnik ekstrakcji danych oparty na technologii OCR (Optical Character Recognition).

Silnik wykorzystuje:

- `pdf2image` do konwersji stron PDF na obrazy,
- `pytesseract` do rozpoznawania tekstu,
- `Tesseract OCR` jako silnik rozpoznawania znaków.

Moduł pełni rolę silnika awaryjnego (fallback) dla dokumentów, które nie mogą zostać poprawnie przetworzone przez silniki analizujące strukturę PDF.

Obsługiwane scenariusze obejmują:

- dokumenty będące skanami,
- dokumenty mieszane,
- dokumenty niejednoznaczne,
- sytuacje, w których pozostałe silniki nie zwróciły wyników.

---

# Miejsce modułu w architekturze systemu

```text
BaseEngine
    │
    ▼
OCREngine
    │
    ├── extract()
    ├── extract_page()
    ├── count_pages()
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

Moduł stanowi implementację silnika ekstrakcji zgodną z interfejsem `BaseEngine`.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- konwersję PDF do obrazów,
- uruchamianie OCR,
- ekstrakcję tekstu z dokumentów PDF,
- ekstrakcję danych z pojedynczych stron,
- dostarczanie danych w formacie zgodnym z architekturą projektu,
- udostępnianie informacji diagnostycznych,
- obsługę błędów OCR.

---

## Dziedziczenie

```python
class OCREngine(BaseEngine)
```

---

## Architektura logiczna

```text
OCREngine
│
├── supports()
├── extract()
├── extract_page()
├── _pdf_to_images()
├── _run_ocr()
├── count_pages()
└── get_document_info()
```

---

## Poza zakresem modułu

Moduł nie odpowiada za:

- generowanie dokumentów DOCX,
- walidację tabel,
- analizę jakości danych,
- przetwarzanie równoległe,
- zarządzanie fallback pomiędzy silnikami,
- klasyfikację typu PDF.

---

# Diagram przepływu danych

## Ekstrakcja całego dokumentu

```text
PDF
 │
 ▼
_pdf_to_images()
 │
 ▼
lista obrazów
 │
 ▼
_run_ocr()
 │
 ▼
tekst strony
 │
 ▼
format wynikowy
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
convert_from_path()
 │
 ▼
obraz strony
 │
 ▼
_run_ocr()
 │
 ▼
tekst
 │
 ▼
wynik
```

---

# Opis działania modułu

Silnik OCR przekształca strony PDF do postaci obrazów.

Następnie każda strona jest analizowana przez silnik Tesseract OCR.

Rozpoznany tekst jest umieszczany w strukturze zgodnej z architekturą projektu:

```python
{
    "page": numer_strony,
    "data": [[tekst]]
}
```

Silnik nie wykonuje analizy tabel ani struktury dokumentu. Zwracany jest wyłącznie tekst rozpoznany przez Tesseract.

---

# Model danych

## Struktura wyniku extract()

```python
[
    {
        "page": 1,
        "data": [
            [
                "rozpoznany tekst"
            ]
        ]
    }
]
```

---

## Struktura wyniku extract_page()

```python
[
    [
        [
            "rozpoznany tekst"
        ]
    ]
]
```

---

## Struktura wyniku get_document_info()

```python
{
    "pages": 12,
    "engine": "ocr"
}
```

---

# Klasa OCREngine

## Przeznaczenie

Implementacja silnika OCR wykorzystującego:

- Tesseract OCR,
- pdf2image,
- pytesseract.

Silnik przeznaczony jest głównie do przetwarzania skanów dokumentów PDF.

---

## Dziedziczenie

```python
OCREngine(BaseEngine)
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
"ocr"
```

---

# Funkcje modułu

Moduł nie definiuje funkcji globalnych.

Cała funkcjonalność została zaimplementowana jako metody klasy `OCREngine`.

---

# Metody klasy OCREngine

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

---

### Wartości zwracane

Typ:

```python
bool
```

---

### Obsługiwane typy

```python
[
    "skan (OCR)",
    "mieszany",
    "niejednoznaczny"
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
    "skan (OCR)"
)
```

### Przykładowy wynik

```python
True
```

### Co robi przykład

Sprawdza możliwość obsługi wskazanego typu PDF.

### Kiedy używać

Przed wyborem silnika ekstrakcyjnego.

Pozwala określić, czy OCR może zostać użyty dla danego dokumentu.

---

## extract()

### Przeznaczenie

Wykonuje OCR całego dokumentu PDF.

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

Ścieżka dokumentu PDF.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Struktura wyniku

```python
[
    {
        "page": 1,
        "data": [[tekst]]
    }
]
```

---

### Przepływ działania

```text
_pdf_to_images()
 │
 ▼
lista stron
 │
 ▼
_run_ocr()
 │
 ▼
utworzenie wyniku
 │
 ▼
return
```

---

### Obsługa błędów

Obsługiwane są:

- błędy konwersji PDF,
- błędy OCR,
- błędy przetwarzania pojedynczych stron.

Błędy są logowane.

---

### Przykład użycia

```python
engine = OCREngine()

result = engine.extract(
    "scan.pdf"
)
```

### Przykładowy wynik

```python
[
    {
        "page": 1,
        "data": [
            [
                "Przykładowy tekst"
            ]
        ]
    }
]
```

### Co robi przykład

Przetwarza cały dokument PDF.

### Kiedy używać

Dla dokumentów będących skanami lub dokumentów pozbawionych możliwej do odczytu struktury tekstowej.

---

## extract_page()

### Przeznaczenie

Wykonuje OCR pojedynczej strony dokumentu.

Metoda wykorzystywana przez moduł `parallel_pipeline.py`.

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

#### page_num

Typ:

```python
int
```

Numer strony.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Struktura wyniku

```python
[
    [
        [
            "rozpoznany tekst"
        ]
    ]
]
```

---

### Przepływ działania

```text
convert_from_path()
 │
 ▼
obraz strony
 │
 ▼
_run_ocr()
 │
 ▼
wynik
```

---

### Obsługa błędów

Błędy są logowane.

W przypadku błędu zwracane jest:

```python
[]
```

---

### Przykład użycia

```python
engine.extract_page(
    "scan.pdf",
    5
)
```

### Przykładowy wynik

```python
