# base_engine.py

## Cel modułu

Moduł `base_engine.py` definiuje bazowy interfejs dla wszystkich silników ekstrakcji danych wykorzystywanych w systemie.

Jego głównym zadaniem jest wymuszenie jednolitego API dla wszystkich implementacji silników przetwarzania dokumentów PDF.

Moduł definiuje kontrakt, który muszą spełniać wszystkie silniki ekstrakcji, między innymi:

- `PdfPlumberEngine`,
- `CamelotEngine`,
- `OCREngine`,
- przyszłe implementacje oparte o AI lub ML.

Dzięki zastosowaniu wspólnego interfejsu pozostałe moduły systemu mogą korzystać z różnych silników bez znajomości szczegółów ich implementacji.

---

# Miejsce modułu w architekturze systemu

```text
BaseEngine
     │
     ├── PdfPlumberEngine
     ├── CamelotEngine
     ├── OCREngine
     └── kolejne implementacje
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

Moduł znajduje się w warstwie abstrakcji silników ekstrakcji danych.

---

# Architektura modułu

## Rola modułu

Moduł definiuje wspólny kontrakt dla wszystkich silników.

Kontrakt obejmuje:

- identyfikację silnika,
- obsługiwane typy PDF,
- ekstrakcję całego dokumentu,
- ekstrakcję pojedynczej strony,
- walidację wyników,
- udostępnianie metadanych.

---

## Architektura klas

```text
ABC
 │
 ▼
BaseEngine
 │
 ├── supports()
 ├── extract()
 ├── extract_page()
 ├── validate_result()
 ├── get_metadata()
 ├── __str__()
 └── __repr__()
```

---

## Zakres odpowiedzialności

Moduł odpowiada za:

- definiowanie interfejsu silników,
- definiowanie wspólnego API,
- dostarczanie podstawowych metod pomocniczych,
- wymuszanie implementacji metod krytycznych.

---

## Poza zakresem modułu

Moduł nie odpowiada za:

- ekstrakcję danych,
- analizę PDF,
- OCR,
- generowanie Word,
- przetwarzanie równoległe,
- logowanie,
- raportowanie.

---

# Diagram przepływu danych

```text
tableimport.py
       │
       ▼
   BaseEngine
       │
       ▼
implementacja silnika
       │
       ├── supports()
       ├── extract()
       └── extract_page()
               │
               ▼
          wyniki danych
```

---

# Opis działania modułu

Moduł wykorzystuje mechanizm klas abstrakcyjnych dostarczany przez bibliotekę `abc`.

Klasa `BaseEngine` nie jest przeznaczona do bezpośredniego użycia.

Jej zadaniem jest definiowanie wymaganych metod dla wszystkich implementacji silników.

Każdy silnik dziedziczący po `BaseEngine` musi zaimplementować:

```python
supports()
extract()
extract_page()
```

Brak implementacji tych metod uniemożliwia poprawne utworzenie działającej klasy konkretnego silnika.

---

# Model danych

## Nazwa silnika

Każdy silnik definiuje pole:

```python
name
```

Domyślna wartość w klasie bazowej:

```python
name = "base"
```

---

## Struktura wyniku extract()

Przykład przedstawiony w dokumentacji kodu:

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

---

## Metadane silnika

Format zwracany przez:

```python
get_metadata()
```

```python
{
    "name": self.name,
    "class": self.__class__.__name__
}
```

---

# Klasa BaseEngine

## Przeznaczenie

Bazowa klasa abstrakcyjna wszystkich silników ekstrakcji danych z dokumentów PDF.

Zapewnia wspólny kontrakt pomiędzy komponentami systemu.

---

## Dziedziczenie

```python
class BaseEngine(ABC)
```

Klasa dziedziczy po:

```python
abc.ABC
```

---

## Atrybuty klasy

### name

Typ:

```python
str
```

Domyślna wartość:

```python
"base"
```

Przeznaczenie:

Identyfikacja silnika.

---

# Funkcje modułu

Moduł nie definiuje funkcji globalnych.

Cała funkcjonalność została zaimplementowana w klasie `BaseEngine`.

---

# Metody klasy BaseEngine

## supports()

### Przeznaczenie

Określa, czy silnik obsługuje wskazany typ dokumentu PDF.

Metoda jest abstrakcyjna i musi zostać zaimplementowana przez klasę pochodną.

---

### Sygnatura

```python
def supports(self, pdf_type):
```

### Parametry

#### pdf_type

Typ:

```python
str
```

Typ dokumentu PDF.

---

### Wartości zwracane

Typ:

```python
bool
```

---

### Przepływ działania

```text
pdf_type
 │
 ▼
implementacja silnika
 │
 ▼
obsługiwany?
 │
 ├── TAK
 │
 ▼
True
 │
 └── NIE
     ▼
False
```

---

### Obsługa błędów

Brak implementacji w klasie bazowej.

Obsługa błędów zależy od implementacji konkretnego silnika.

---

### Przykład użycia

```python
engine.supports("tekstowy")
```

### Przykładowy wynik

```python
True
```

### Co robi przykład

Sprawdza możliwość obsługi wskazanego typu dokumentu.

### Kiedy używać

Przed uruchomieniem ekstrakcji danych.

Pozwala wybrać odpowiedni silnik dla konkretnego dokumentu.

---

## extract()

### Przeznaczenie

Realizuje ekstrakcję danych z całego dokumentu PDF.

Metoda jest abstrakcyjna i wymaga implementacji w klasach pochodnych.

---

### Sygnatura

```python
def extract(self, pdf_path):
```

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

### Przykład struktury wyniku

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

---

### Przepływ działania

```text
pdf_path
 │
 ▼
implementacja silnika
 │
 ▼
ekstrakcja danych
 │
 ▼
lista wyników
```

---

### Obsługa błędów

Brak implementacji w klasie bazowej.

Obsługa błędów zależy od konkretnego silnika.

---

### Przykład użycia

```python
engine.extract("report.pdf")
```

### Przykładowy wynik

```python
[
    {
        "page": 1,
        "data": [...]
    }
]
```

### Co robi przykład

Uruchamia ekstrakcję danych z pełnego dokumentu.

### Kiedy używać

Gdy wymagane jest przetworzenie całego dokumentu PDF.

---

## extract_page()

### Przeznaczenie

Realizuje ekstrakcję danych z pojedynczej strony PDF.

Metoda jest wykorzystywana przez moduł:

```text
parallel_pipeline.py
```

---

### Sygnatura

```python
def extract_page(self, pdf_path, page_num):
```

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

Numer strony dokumentu.

---

### Wartości zwracane

Typ:

```python
list
```

---

### Przepływ działania

```text
pdf_path
 │
 ▼
page_num
 │
 ▼
implementacja silnika
 │
 ▼
ekstrakcja strony
 │
 ▼
wynik
```

---

### Obsługa błędów

Brak implementacji w klasie bazowej.

---

### Przykład użycia

```python
engine.extract_page(
    "report.pdf",
    5
)
```

### Przykładowy wynik

```python
[
    ...
]
```

### Co robi przykład

Przetwarza pojedynczą stronę dokumentu.

### Kiedy używać

Przy przetwarzaniu równoległym lub analizie pojedynczych stron.

---

## validate_result()

### Przeznaczenie

Weryfikuje poprawność wyniku zwracanego przez silnik.

Implementacja w klasie bazowej sprawdza wyłącznie typ wyniku.

---

### Sygnatura

```python
def validate_result(self, result):
```

### Parametry

#### result

Typ:

Nie został określony w kodzie.

---

### Wartości zwracane

Typ:

```python
bool
```

---

### Logika działania

```python
return isinstance(result, list)
```

---

### Przepływ działania

```text
result
 │
 ▼
isinstance(...)
 │
 ▼
True / False
```

---

### Obsługa błędów

Nie występuje.

---

### Przykład użycia

```python
engine.validate_result(result)
```

### Przykładowy wynik

```python
True
```

### Co robi przykład

Sprawdza, czy wynik jest listą.

### Kiedy używać

Przed dalszym przetwarzaniem wyników ekstrakcji.

---

## get_metadata()

### Przeznaczenie

Zwraca podstawowe metadane silnika.

---

### Sygnatura

```python
def get_metadata(self):
```

### Parametry

Brak.

---

### Wartości zwracane

Typ:

```python
dict
```

---

### Struktura wyniku

```python
{
    "name": self.name,
    "class": self.__class__.__name__
}
```

---

### Przepływ działania

```text
name
 │
 ▼
class
 │
 ▼
dict
```

---

### Obsługa błędów

Nie występuje.

---

### Przykład użycia

```python
metadata = engine.get_metadata()
```

### Przykładowy wynik

```python
{
    "name": "pdfplumber",
    "class": "PdfPlumberEngine"
}
```

### Co robi przykład

Pobiera informacje identyfikujące silnik.

### Kiedy używać

Podczas diagnostyki, logowania i raportowania.

---

## __str__()

### Przeznaczenie

Zwraca nazwę silnika.

---

### Sygnatura

```python
def __str__(self):
```

### Wartości zwracane

Typ:

```python
str
```

### Logika działania

```python
return self.name
```

### Przykład użycia

```python
str(engine)
```

### Przykładowy wynik

```python
pdfplumber
```

### Kiedy używać

Do prezentacji nazwy silnika użytkownikowi.

---

## __repr__()

### Przeznaczenie

Zwraca reprezentację diagnostyczną obiektu.

---

### Sygnatura

```python
def __repr__(self):
```

### Wartości zwracane

Typ:

```python
str
```

### Przykładowy wynik

```python
PdfPlumberEngine(name='pdfplumber')
```

### Kiedy używać

Podczas debugowania i analizy działania systemu.

---

# Kontrakt implementacyjny

Każdy silnik dziedziczący po `BaseEngine` musi implementować:

```python
supports()
```

```python
extract()
```

```python
extract_page()
```

Każdy silnik powinien definiować własną wartość:

```python
name
```

---

# Tryby pracy

Moduł nie definiuje trybów pracy.

---

# Multiprocessing

Moduł nie wykorzystuje multiprocessing.

Metoda:

```python
extract_page()
```

jest jednak przeznaczona do współpracy z:

```text
parallel_pipeline.py
```

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

Nie generuje wpisów logów.

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

Wykorzystuje:

```python
supports()
extract()
```

Rola:

Dobór i uruchamianie odpowiedniego silnika.

---

## parallel_pipeline.py

Wykorzystuje:

```python
extract_page()
```

Rola:

Równoległe przetwarzanie stron dokumentu.

---

## pdf2word_module.py

Korzysta z danych wyekstrahowanych przez silniki implementujące `BaseEngine`.

---

# Przykłady produkcyjne

## Definicja własnego silnika

```python
class MyEngine(BaseEngine):

    name = "myengine"

    def supports(self, pdf_type):
        return True

    def extract(self, pdf_path):
        return []

    def extract_page(self, pdf_path, page_num):
        return []
```

## Pobranie metadanych

```python
engine = MyEngine()

metadata = engine.get_metadata()
```

Wynik:

```python
{
    "name": "myengine",
    "class": "MyEngine"
}
```

---

# Wydajność

## Multiprocessing

Brak.

## Wpływ liczby workers

Nie dotyczy.

## Potencjalne wąskie gardła

Moduł nie wykonuje operacji obliczeniowych.

Stanowi jedynie warstwę abstrakcji.

## Najbardziej obciążające CPU

Brak.

## Najbardziej obciążające I/O

Brak.

---

# Zależności

## abc

### Przeznaczenie

Implementacja klas abstrakcyjnych.

### Miejsce użycia

```python
ABC
abstractmethod
```

### Dokumentacja

https://docs.python.org/3/library/abc.html

---

## ABC

### Przeznaczenie

Bazowa klasa abstrakcyjna.

### Miejsce użycia

```python
class BaseEngine(ABC)
```

---

## abstractmethod

### Przeznaczenie

Oznaczanie metod obowiązkowych.

### Miejsce użycia

```python
@abstractmethod
```

---

# Powiązane moduły projektu

- checkpdf_module.md
- batch_pipeline.md
- tableimport.md
- pdf2word_module.md
- [metrics.md](metrics.md)
- parallel_pipeline.md

## tableimport.py

Wykorzystuje kontrakt `BaseEngine` do zarządzania silnikami.

## parallel_pipeline.py

Wykorzystuje metodę `extract_page()`.

## pdf2word_module.py

Przetwarza dane zwracane przez implementacje silników.

## batch_pipeline.py

Może wykorzystywać silniki pośrednio przez pipeline przetwarzania PDF.

## metrics.py

Może analizować wyniki zwrócone przez silniki.

## checkpdf_module.py

Może dostarczać typ PDF wykorzystywany przez metodę `supports()`.

---

# Podsumowanie

Moduł `base_engine.py` definiuje bazowy kontrakt dla wszystkich silników ekstrakcji danych z dokumentów PDF. Dzięki zastosowaniu klasy abstrakcyjnej `BaseEngine` wszystkie implementacje udostępniają jednolite API i mogą być wykorzystywane zamiennie przez pozostałe komponenty systemu.

Najważniejszym zadaniem modułu jest wymuszenie implementacji metod `supports()`, `extract()` oraz `extract_page()`. Moduł stanowi fundament architektury pluginowej wykorzystywanej przez cały system przetwarzania dokumentów PDF.
