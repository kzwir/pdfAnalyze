# Logging Configuration Module

## Cel modułu

Moduł `logging_config.py` odpowiada za centralną konfigurację mechanizmu logowania wykorzystywanego przez pozostałe moduły projektu.

Jego zadaniem jest:

- tworzenie katalogu logów,
- konfiguracja poziomu logowania,
- konfiguracja pliku logów,
- konfiguracja formatu wpisów logów,
- zwracanie skonfigurowanego obiektu loggera,
- udostępnianie loggerów przez nazwę.

Moduł stanowi wspólną warstwę logowania dla całego systemu.

---

# Miejsce modułu w architekturze systemu

```text
Aplikacja
│
├── glowny.py
├── batch_pipeline.py
├── tableimport.py
├── checkpdf_module.py
│
└── logging_config.py
        │
        ▼
      logging
        │
        ▼
      logs/
      ├── app.log
      ├── main.log
      └── ...
```

Moduł znajduje się w warstwie infrastrukturalnej i odpowiada za konfigurację wspólnego mechanizmu rejestrowania zdarzeń.

---

# Architektura modułu

## Odpowiedzialność modułu

Moduł odpowiada za:

- tworzenie katalogu logów,
- budowanie pełnej ścieżki pliku logów,
- konfigurację poziomu logowania,
- konfigurację formatowania wpisów,
- tworzenie i konfigurację loggera,
- usuwanie wcześniej skonfigurowanych handlerów,
- dostęp do loggerów przez nazwę.

Moduł nie odpowiada za:

- zapis logiki biznesowej,
- generowanie raportów analizy danych,
- przetwarzanie PDF,
- zarządzanie pipeline.

---

## Publiczne API modułu

Moduł udostępnia dwie funkcje:

```python
setup_logging()
```

oraz

```python
get_logger()
```

Są to funkcje przeznaczone do wykorzystania przez pozostałe moduły projektu.

---

# Diagram przepływu danych

```text
setup_logging()
        │
        ▼
os.makedirs()
        │
        ▼
logging.getLogger()
        │
        ▼
logging.FileHandler()
        │
        ▼
logging.Formatter()
        │
        ▼
logger
        │
        ▼
moduły projektu
        │
        ▼
plik logów
```

---

# Opis działania modułu

Podczas wywołania funkcji:

```python
setup_logging()
```

moduł:

1. Tworzy katalog logów.
2. Tworzy pełną ścieżkę do pliku logów.
3. Wyznacza poziom logowania.
4. Pobiera główny logger.
5. Usuwa istniejące handlery.
6. Ustawia nowy poziom logowania.
7. Tworzy obiekt `FileHandler`.
8. Konfiguruje format wpisów.
9. Dodaje handler do loggera.
10. Zwraca skonfigurowany logger.

---

# Wejście i wyjście

## Dane wejściowe

### log_dir

Typ:

```python
str
```

Katalog przechowywania logów.

Przykład:

```python
"logs"
```

---

### log_file

Typ:

```python
str
```

Nazwa pliku logów.

Przykład:

```python
"main.log"
```

---

### log_level

Typ:

```python
str
```

Poziom logowania.

Przykłady:

```python
"DEBUG"
"INFO"
"WARNING"
"ERROR"
"CRITICAL"
```

---

## Dane wyjściowe

### Logger

Typ:

```python
logging.Logger
```

Skonfigurowany obiekt loggera.

---

# Tabela funkcji modułu

| Funkcja | Przeznaczenie |
|----------|----------|
| `setup_logging()` | Konfiguracja logowania |
| `get_logger()` | Pobranie loggera o wskazanej nazwie |

---

# Funkcje modułu

## setup_logging()

### Przeznaczenie

Konfiguruje centralny mechanizm logowania aplikacji.

Tworzy katalog logów, ustawia poziom logowania, konfiguruje plik logów oraz przygotowuje logger do użycia przez pozostałe moduły systemu.

---

### Sygnatura

```python
def setup_logging(
    log_dir="logs",
    log_file="app.log",
    log_level="INFO"
):
```

---

### Parametry

#### log_dir

Typ:

```python
str
```

Domyślna wartość:

```python
"logs"
```

Katalog przeznaczony do przechowywania plików logów.

---

#### log_file

Typ:

```python
str
```

Domyślna wartość:

```python
"app.log"
```

Nazwa pliku logów.

---

#### log_level

Typ:

```python
str
```

Domyślna wartość:

```python
"INFO"
```

Poziom logowania.

---

### Wartości zwracane

Typ:

```python
logging.Logger
```

Zwracany jest skonfigurowany główny logger aplikacji.

---

### Zależności wejścia/wyjścia

#### Wejście

```python
log_dir
log_file
log_level
```

#### Operacje pośrednie

```python
os.makedirs(...)
```

```python
logging.getLogger()
```

```python
logging.FileHandler(...)
```

#### Wyjście

```python
logger
```

oraz plik logu.

---

### Przepływ działania

```text
setup_logging()
 ↓
utworzenie katalogu
 ↓
utworzenie ścieżki logu
 ↓
wyznaczenie poziomu logowania
 ↓
pobranie loggera
 ↓
usunięcie handlerów
 ↓
FileHandler
 ↓
Formatter
 ↓
logger
```

---

### Obsługa błędów

Funkcja nie zawiera jawnych bloków:

```python
try:
except:
```

Obsługa wyjątków delegowana jest do bibliotek:

```python
os
logging
```

Funkcja wykonuje jednak zabezpieczenie:

```python
if logger.hasHandlers():
    logger.handlers.clear()
```

które usuwa wcześniej skonfigurowane handlery.

Dzięki temu nie dochodzi do wielokrotnego dodawania tych samych handlerów podczas kolejnych wywołań funkcji.

---

### Przykład użycia

```python
from logging_config import setup_logging

logger = setup_logging(
    log_dir="logs",
    log_file="main.log",
    log_level="INFO"
)

logger.info("Start programu")
```

---

### Przykładowy wynik

Plik:

```text
logs/main.log
```

Przykładowa zawartość:

```text
2026-01-15 12:01:11 INFO Start programu
```
