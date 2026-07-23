# Formatowanie tabel w dokumentach DOCX

## Cel

System generujący dokumenty Microsoft Word wykorzystuje mechanizm stylów zdefiniowanych w pliku szablonu DOCX.

Dzięki temu wygląd tabel nie jest zapisany na stałe w kodzie aplikacji. Formatowanie jest przechowywane w szablonie Word i może być modyfikowane bez konieczności zmiany kodu Python.

Takie rozwiązanie umożliwia:

- centralne zarządzanie wyglądem raportów,
- zachowanie spójnego formatowania we wszystkich dokumentach,
- łatwe dostosowanie wyglądu dokumentów do wymagań organizacji,
- oddzielenie warstwy prezentacji od logiki aplikacji.

---

# Mechanizm działania

## Szablon DOCX

System wykorzystuje plik:

```text
szablon.docx
```

W szablonie może zostać zdefiniowany własny styl tabeli.

Styl taki przechowuje wszystkie ustawienia odpowiadające za wygląd tabel.

Przykładowo styl może określać:

- rodzaj czcionki,
- rozmiar czcionki,
- kolor tekstu,
- kolor nagłówków,
- kolor tła komórek,
- obramowania,
- szerokość linii obramowania,
- odstępy wewnętrzne komórek,
- wyrównanie tekstu,
- zachowanie pierwszego i ostatniego wiersza,
- zachowanie pierwszej i ostatniej kolumny,
- formatowanie naprzemiennych wierszy.

---

## Dokument wynikowy

Podczas generowania raportu:

1. Wczytywany jest szablon DOCX.
2. Tworzone są nowe tabele.
3. Do tabel przypisywany jest styl zdefiniowany w szablonie.
4. Dokument zostaje zapisany jako plik wynikowy.

Dzięki temu każdy wygenerowany raport automatycznie korzysta z jednolitego formatowania.

---

# Zalecany sposób zarządzania stylem

Zaleca się definiowanie wszystkich ustawień wizualnych tabel wyłącznie w szablonie Word.

Nie należy modyfikować wyglądu tabel bezpośrednio w kodzie aplikacji, jeżeli wymagane zmiany można wprowadzić za pomocą stylu Word.

Pozwala to na:

- szybszą modyfikację raportów,
- łatwiejsze utrzymanie projektu,
- ograniczenie liczby zmian w kodzie,
- niezależność zespołu biznesowego od zespołu programistycznego.

---

# Tworzenie nowego stylu tabeli w Microsoft Word

## Krok 1 – Otwórz szablon

Uruchom Microsoft Word i otwórz:

```text
szablon.docx
```

---

## Krok 2 – Wstaw przykładową tabelę

W menu:

```text
Wstaw → Tabela
```

utwórz przykładową tabelę.

Przykład:

```text
3 kolumny
3 wiersze
```

---

## Krok 3 – Przygotuj wygląd tabeli

Skonfiguruj wszystkie elementy wizualne zgodnie z wymaganiami organizacji:

- czcionkę,
- kolor tekstu,
- kolor nagłówków,
- obramowania,
- szerokości kolumn,
- wyrównanie,
- odstępy.

---

## Krok 4 – Otwórz galerię stylów tabel

Kliknij dowolną komórkę tabeli.

Następnie przejdź do zakładki:

```text
Projektowanie tabeli
```

lub w angielskiej wersji:

```text
Table Design
```

W sekcji:

```text
Style tabel
```

kliknij przycisk:

```text
Więcej ▼
```

---

## Krok 5 – Utwórz nowy styl

Wybierz:

```text
Nowy styl tabeli...
```

---

## Krok 6 – Skonfiguruj styl

### Nazwa stylu

Podaj nazwę stylu.

Przykład:

```text
CorporateTable
```

lub

```text
ZWIR_TABLE
```

---

### Typ stylu

Wybierz:

```text
Tabela
```

---

### Elementy możliwe do formatowania

Word pozwala osobno konfigurować:

```text
Cała tabela
```

```text
Wiersz nagłówka
```

```text
Pierwsza kolumna
```

```text
Ostatnia kolumna
```

```text
Pierwszy wiersz
```

```text
Ostatni wiersz
```

```text
Naprzemienne wiersze
```

```text
Naprzemienne kolumny
```

---

## Krok 7 – Zapisz styl

Po zakończeniu konfiguracji wybierz:

```text
OK
```

Nowy styl zostanie zapisany w dokumencie.

---

## Krok 8 – Przypisz styl do tabeli

Zaznacz tabelę.

W galerii:

```text
Style tabel
```

wybierz utworzony styl.

Przykład:

```text
CorporateTable
```

---

## Krok 9 – Zapisz szablon

Zapisz plik:

```text
szablon.docx
```

---

# Aktualizacja istniejącego stylu

Jeżeli styl został już utworzony:

1. Otwórz szablon.
2. Wybierz tabelę korzystającą ze stylu.
3. Zmodyfikuj formatowanie.
4. Zaktualizuj definicję stylu.
5. Zapisz szablon.

Po zapisaniu wszystkie kolejne dokumenty generowane na podstawie tego szablonu będą korzystały z nowej wersji stylu.

---

# Przykład organizacyjny

Przykładowy styl tabeli może definiować:

```text
Nazwa stylu:
REPORT_TABLE
```

Parametry:

```text
Czcionka:
Calibri 10 pt
```

```text
Nagłówek:
Białe litery
Granatowe tło
```

```text
Obramowanie:
Czarne
```

```text
Wiersze:
Naprzemienne szare tło
```

```text
Wyrównanie:
Do lewej
```

Po zapisaniu szablonu wszystkie raporty wygenerowane przez system będą automatycznie wykorzystywały ten wygląd.

---

# Korzyści z wykorzystania stylów Word

## Dla użytkownika końcowego

- jednolity wygląd raportów,
- łatwa modyfikacja szablonu,
- brak potrzeby znajomości kodu.

## Dla programisty

- brak konieczności zmian w kodzie przy modyfikacji wyglądu,
- uproszczenie logiki generowania dokumentów,
- łatwiejsze utrzymanie projektu.

## Dla integratora systemu

- możliwość dostosowania wyglądu dokumentów do wymagań klienta,
- możliwość tworzenia wielu wariantów szablonów,
- oddzielenie konfiguracji wizualnej od logiki biznesowej.

---

# Podsumowanie

System wykorzystuje style tabel zapisane w pliku `szablon.docx` do kontrolowania wyglądu tabel w dokumentach wynikowych. Dzięki temu formatowanie nie jest zapisane w kodzie źródłowym i może być modyfikowane bez ingerencji w aplikację.

Zalecanym sposobem zarządzania wyglądem raportów jest tworzenie i utrzymywanie własnych stylów tabel bezpośrednio w Microsoft Word. Pozwala to zachować spójność dokumentów oraz znacząco upraszcza administrację i rozwój systemu.
