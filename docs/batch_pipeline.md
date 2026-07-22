# Architektura modułu

## Odpowiedzialność modułu

Moduł `batch_pipeline.py` pełni rolę głównego koordynatora procesu wsadowego przetwarzania dokumentów PDF.

Odpowiada za:

- wyszukiwanie dokumentów PDF w katalogu wejściowym,
- uruchamianie procesu przetwarzania,
- wybór trybu pracy (`single`, `merged`, `grouped`),
- koordynację przepływu danych pomiędzy modułami,
- obsługę multiprocessing,
- obsługę retry,
- agregację wyników,
- generowanie dashboardu,
- zapis raportu JSON,
- rejestrowanie przebiegu procesu.

Moduł nie odpowiada za:

- analizę struktury dokumentów PDF,
- ekstrakcję tabel,
- wykonywanie OCR,
- wybór algorytmu ekstrakcji,
- generowanie zawartości dokumentów DOCX.

Powyższe zadania są realizowane przez wyspecjalizowane moduły projektu.

---

## Publiczne API modułu

Funkcją przeznaczoną do wykorzystania przez inne moduły projektu jest:

```python
run_batch()
```

Jest to główny punkt wejścia aplikacji.

W większości przypadków pozostałe moduły powinny korzystać wyłącznie z tej funkcji zamiast bezpośrednio wywoływać funkcje pomocnicze.

---

## Funkcje wewnętrzne

Poniższe funkcje są wykorzystywane przez `run_batch()` i stanowią implementację wewnętrzną modułu:

```python
setup_logging()
process_single()
process_with_retry()
run_merged()
run_grouped()
print_dashboard()
main()
```

Funkcje te nie zostały zaprojektowane jako publiczny interfejs integracyjny.

---

# Wejście i wyjście

## Dane wejściowe

Moduł oczekuje katalogu zawierającego pliki PDF.

Przykład:

```text
input/
├── 0.pdf
├── 1.pdf
├── 2.pdf
└── ...
```

Każdy odnaleziony plik PDF zostaje przekazany do procesu analizy i ekstrakcji danych.

---

## Dane wyjściowe

### Tryb `single`

Dla każdego dokumentu PDF tworzony jest osobny dokument DOCX.

```text
output/
├── 0.docx
├── 1.docx
├── 2.docx
└── ...
```

### Tryb `merged`

Wszystkie dokumenty PDF trafiają do jednego wspólnego dokumentu DOCX.

```text
output/
└── wynik_zbiorczy.docx
```

### Tryb `grouped`

Dokumenty PDF są grupowane zgodnie z wartością parametru:

```python
group_size
```

Przykład:

```text
output/
├── part_001.docx
├── part_002.docx
└── part_003.docx
```

---

## Dodatkowe artefakty

Po zakończeniu pracy moduł generuje również:

```text
dashboard.json
```

oraz:

```text
batch.log
```

---

# Tabela funkcji modułu

| Funkcja | Przeznaczenie |
|----------|----------|
| `setup_logging()` | Konfiguracja systemu logowania |
| `process_single()` | Przetwarzanie pojedynczego dokumentu PDF |
| `process_with_retry()` | Obsługa retry dla pojedynczego dokumentu |
| `run_merged()` | Scalanie wielu PDF do jednego DOCX |
| `run_grouped()` | Grupowanie PDF do wielu dokumentów DOCX |
| `print_dashboard()` | Prezentacja statystyk procesu |
| `run_batch()` | Główny punkt wejścia modułu |
| `main()` | Interfejs CLI |

---

# Zależności między modułami

```text
batch_pipeline.py
│
├── checkpdf_module.py
│     └── analiza dokumentów PDF
│
├── tableimport.py
│     └── ekstrakcja danych
│
├── metrics.py
│     └── agregacja wyników i statystyk
│
└── pdf2word_module.py
      └── tworzenie dokumentów DOCX
```

---

# Dane przekazywane pomiędzy modułami

## checkpdf_module.py → batch_pipeline.py

Wywołanie:

```python
result = analyze_file(pdf_path)
```

Przykładowy wynik:

```python
{
    "valid_pdf": True,
    "pages": 12,
    "type": "tekstowy"
}
```

Wykorzystywane są następujące pola:

```python
result["valid_pdf"]
result["pages"]
result["type"]
```

Informacje te decydują o dalszym przebiegu procesu.

---

## batch_pipeline.py → tableimport.py

Wywołanie:

```python
run_pipeline_with_metrics(
    pdf_path=pdf_path,
    template_path=template_path,
    output_path=output_path,
    pdf_type=result["type"],
    pages=pages,
    forced_engine="auto",
    parallel=(pages > 10)
)
```

Przekazywane są:

- ścieżka dokumentu PDF,
- ścieżka szablonu DOCX,
- ścieżka dokumentu wynikowego,
- typ dokumentu PDF,
- liczba stron,
- informacja o pracy równoległej.

---

## tableimport.py → batch_pipeline.py

Odbierane są informacje o przebiegu procesu ekstrakcji:

```python
{
    "engine": "pdfplumber",
    "tables_total": 6,
    "tables_valid": 6
}
```

Wyniki te są przekazywane do systemu metryk.

---

# Artefakty generowane przez moduł

## Dokumenty DOCX

Tworzone są w katalogu:

```text
output/
```

Przykłady:

```text
0.docx
1.docx
2.docx
```

lub:

```text
wynik_zbiorczy.docx
```

lub:

```text
part_001.docx
part_002.docx
part_003.docx
```

---

## dashboard.json

Raport podsumowujący proces.

Przechowuje:

- liczbę plików PDF,
- liczbę błędów,
- współczynnik sukcesu,
- jakość ekstrakcji,
- czasy wykonania,
- wykorzystanie silników.

---

## batch.log

Centralny log działania modułu.

Zawiera:

- rozpoczęcie procesu,
- zakończenie procesu,
- retry,
- informacje diagnostyczne,
- błędy,
- wyniki przetwarzania.

---

# Integracja z Metrics

Moduł wykorzystuje klasę:

```python
Metrics
```

Tworzenie obiektu:

```python
metrics = Metrics()
```

Dodawanie wyników:

```python
metrics.add_result(result)
```

Generowanie podsumowania:

```python
summary = metrics.summary()
```

Wynik podsumowania jest wykorzystywany do:

- wyświetlenia dashboardu,
- wygenerowania raportu JSON,
- obliczenia statystyk jakości.

### Przepływ danych

```text
process_single()
        ↓
result
        ↓
metrics.add_result()
        ↓
Metrics.summary()
        ↓
summary
        ↓
print_dashboard()
        ↓
dashboard.json
```

---

# Sekwencja wykonania

Typowy przebieg procesu:

```text
main()
 ↓
setup_logging()
 ↓
run_batch()
 ↓
process_with_retry()
 ↓
process_single()
 ↓
analyze_file()
 ↓
run_pipeline_with_metrics()
 ↓
Metrics.add_result()
 ↓
Metrics.summary()
 ↓
print_dashboard()
 ↓
dashboard.json
```

Diagram pokazuje pełną ścieżkę przetwarzania od uruchomienia aplikacji do wygenerowania raportów.

---

# Scenariusze użycia

## Przetwarzanie niewielkiej liczby dokumentów

Przykład:

```text
10 PDF
```

Rekomendowana konfiguracja:

```python
merge_mode="single"
```

Zalecane dla codziennego przetwarzania niewielkich partii dokumentów. Każdy dokument jest przetwarzany niezależnie i generowany jest osobny plik DOCX.

---

## Przetwarzanie dużej liczby dokumentów

Przykład:

```text
500 PDF
```

Rekomendowana konfiguracja:

```python
workers=4
merge_mode="single"
```

Pozwala wykorzystać multiprocessing oraz rozłożyć obciążenie pomiędzy wiele procesów roboczych.

---

## Generowanie raportu zbiorczego

Przykład:

```text
30 PDF
 ↓
1 DOCX
```

Rekomendowany tryb:

```python
merge_mode="merged"
```

Przydatny podczas generowania dokumentacji projektowej, raportów okresowych lub dokumentów archiwalnych.

---

## Archiwizacja dokumentów

Przykład:

```text
250 PDF
```

Rekomendowany tryb:

```python
merge_mode="grouped"
```

Pozwala podzielić duży zbiór dokumentów na logiczne partie i ograniczyć rozmiar pojedynczych dokumentów DOCX.

---

# Obsługa błędów

W tej sekcji należy umieścić pełny opis mechanizmów obsługi błędów obejmujący:

- walidację dokumentów PDF,
- obsługę wyjątków w `process_single()`,
- mechanizm retry,
- obsługę błędów w `run_merged()`,
- obsługę błędów w `run_grouped()`,
- obsługę pustego katalogu wejściowego,
- logowanie błędów,
- agregację błędów w metrykach,
- odporność procesu na błędy.

Zaleca się umieszczenie rozbudowanego rozdziału „Obsługa błędów” jako osobnego rozdziału następującego bezpośrednio po opisie funkcji modułu.

---

# Wydajność

## Multiprocessing

Moduł wykorzystuje:

```python
multiprocessing.Pool
```

Domyślna konfiguracja:

```python
workers = min(cpu_count(), 4)
```

Tryb multiprocessing wykorzystywany jest wyłącznie podczas pracy w trybie:

```python
merge_mode="single"
```

## Potencjalne wąskie gardła

Najbardziej kosztowne operacje obejmują:

- analizę dokumentów PDF,
- ekstrakcję danych z dokumentów wielostronicowych,
- operacje OCR wykonywane przez moduły podrzędne,
- zapis dokumentów DOCX,
- zapis raportów i logów.

## Wpływ liczby workers

Zwiększenie liczby procesów roboczych pozwala skrócić czas przetwarzania dużych zbiorów dokumentów.

Korzyści są największe dla:

- dużej liczby plików PDF,
- dokumentów wielostronicowych,
- środowisk wielordzeniowych.

---

# Znane ograniczenia

Aktualna implementacja posiada następujące ograniczenia:

- multiprocessing wykorzystywany jest wyłącznie w trybie `single`,
- moduł obsługuje wyłącznie dokumenty PDF,
- brak mechanizmu wznowienia procesu po przerwaniu działania aplikacji,
- plik `dashboard.json` jest nadpisywany przy każdym uruchomieniu,
- logi są zapisywane do jednego wspólnego pliku `batch.log`,
- brak dedykowanej kolejki zadań i trwałego mechanizmu restartu przetwarzania.

---

# Powiązane moduły projektu

- checkpdf_module.md
- [Table Import](tableimport.md)
- pdf2word_module.md
- [Metrics](metrics.md)
- parallel_pipeline.md

## Rola modułów

### checkpdf_module.py

Analiza i klasyfikacja dokumentów PDF przed rozpoczęciem ekstrakcji.

### tableimport.py

Główny pipeline ekstrakcji danych oraz wybór odpowiedniego silnika przetwarzania.

### pdf2word_module.py

Tworzenie oraz zapis dokumentów Microsoft Word.

### metrics.py

Gromadzenie wyników procesu, obliczanie statystyk oraz generowanie danych wykorzystywanych przez dashboard.

### parallel_pipeline.py

Rozszerzenia związane z przetwarzaniem równoległym oraz obsługą dużych zbiorów dokumentów.

---

# Decyzje architektoniczne

## Separacja odpowiedzialności

Każdy moduł odpowiada za jeden obszar funkcjonalny:

```text
checkpdf_module     → analiza PDF
tableimport         → ekstrakcja danych
pdf2word_module     → generowanie DOCX
metrics             → statystyki
batch_pipeline      → orkiestracja procesu
```

Takie podejście upraszcza utrzymanie kodu oraz rozwój poszczególnych komponentów.

## Odporność na błędy

Proces został zaprojektowany w sposób umożliwiający kontynuację pracy nawet w przypadku błędów pojedynczych dokumentów.

Błędy:

- nie zatrzymują całego procesu,
- są raportowane w logach,
- są uwzględniane w metrykach,
- są prezentowane w dashboardzie.

## Skalowalność

Architektura umożliwia:

- zwiększanie liczby procesów roboczych,
- obsługę rosnącej liczby dokumentów,
- rozszerzanie liczby silników ekstrakcji bez modyfikowania logiki orchestratora.
