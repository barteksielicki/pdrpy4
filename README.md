# pdrpy4

Projekt zrealizowany na zajęcią "Przetwarzanie danych w językach R i Python".
Głównym zadaniem było skorzystanie z API transportu publicznego miasta Warszawy
oraz wykonanie analizy prowadzącej do ciekawych rezultatów.

## Aplikacja

Nasza aplikacja składa się z aplikacji webowej, której głównym zadaniem jest
prezentowanie danych, które zostały przez nasz przetworzone a następnie
umieszczone w bazie danych MongoDB, aplikacja pobiera dane za pomocą api.
Aplikacja webowa prezentuje heatmap'ę prędkości wybranej linii tramwajowej,
bądź wszystkich linii w wybranym dniu, o wybranej godzinie.

## Obliczanie prędkości

Największym wyzwaniem przed jakim stanęliśmy, było dodanie do zebranych danych nowej kolumny
zawierającej średnią prędkość tramwaju. Prędkość wyraża iloraz różnicy odległości (wzdłuż linii
tramwajowych) i różnicy czasu między dwoma kolejnymi sygnałami nadanymi przez ten sam tramwaj.
Praca którą wykonaliśmy, to pobranie danych z przedziału tygodnia zapisując je do bazy MongoDB
na zdalnym serwerze oraz następnie:

### Zaciągnięcie danych
Zaciągnięcie danych z bazy na maszynie wykonującej obliczenia wykonujemy za pomocą skryptu `get_data.py`.
W rezultacie w katalogu `data` pojawiają się rekordy z zakresu od *04.05.2017 0:00*.
do *10.05.2017 23:59* podzielone na 13 plików (jeden plik zawiera rekordy z 12 godzin).
Skrypt łączy się 

### Obliczenie odległości
Obliczaniem odległości zajmuje się skrypt `process_data.py`. Jest to zadanie dość czasochłonne, dlatego skrypt
przystosowany jest do uruchomienia z wykorzystaniem wielu rdzeni korzystając z pakietu `multiprocessing`. Każdy
z równolegle wykonywanych procesów potomnych zajmuje się obliczaniem odległości dla rekordów z jednego pliku (czyli
1 z 13 zaciągniętych w kroku poprzednim).

**Obliczenie odległości dla pojednczej ramki danych (pojedynczego pliku):**
Rekordy z pliku są załadowane do obiektu typu `pandas.DataFrame` a następnie posortowane wg.
    
    - linii
    - brygady
    - czasu
    
   to pozwala nam stwierdzić że dwa następujące po sobie rekordy o ile mają ten sam numer linii
   oraz brygady zostały nadane kolejno przez ten sam tramwaj (zdarzają się oczywiście wyjątki,
   które uprzykrzały nam pracę).
   
   Aby móc obliczyć średnią prędkość z jaką poruszał się tramwaj między nadaniem dwóch sygnałów
   musimy znać różnicę czasu oraz między nimi oraz dystans jaki w tym czasie pokonał.
   Różnica czasu jest podana, dzięki kolumnie `time` - wystarczy odjąć wartości. Trudniejsze
   jest natomiast uzyskanie odległości jaką przebył tramwaj na podstawie dwóch par współrzędnych,
   i to tak aby była to odległość wzdłuż linii tramwajowych a nie "naiwna" długość odcinka
   między tymi dwoma punktami.
   
   Problem ten rozwiązaliśmy w nastepujący sposób. Z użyciem API Open Street Map pobraliśmy
   trasy poszczególnych linii tramwajowych w Warszawie w formacie węzłów oraz segmentów, gdzie
   węzeł to para współrzędnych a segment to ciąg węzłów. Dane te znajdują się w katalogu `routes`.
   Następnie na podstawie 25 linii tworzymy 25 grafów w których wierzchołkami są węzły tworzące
   daną trasę, krawędziami prostoliniowe segmenty danej trasy, a wagami odległość w linii prostej
   pomiędzy dwoma węzłami. Struktura grafu dla reprezentowania trasy została użyta dla wygody - 
   pozwali ona w łatwy i szybki sposób zmierzyć odległość pomiędzy dwoma punktami na danej trasie.
   
   Klasa `DistanceMeter` wystawiająca taką możliwosć znajduje się w pliku `distance_meter.py`
   
   Mając linie tramwajowe w postaci grafów oraz posortowaną ramkę danych sprawa staje się prosta.
   Iterujemy po `n - 1` parach kolejnych wierszy - jeżeli numer linii oraz brygady w obydwu
   jest identyczny oznacza to że sygnały zostały wysłane po sobie przez ten sam tramwaj.
   Możemy zatem wziąć punkty w których zostały wysłane, wstawić je do grafu reprezentującego daną
   linię (umieszczając dany punkt jako tymczasowy nowy wierzchołek na krawędzi do której jest mu
   najbliżej w sensie geometrycznym), obliczyć odległość używając algorytmu Dijkstry (dzięki
   temu że graf jest dość rzadki, acykliczny oraz stosunkowo niewielki jest to sprawne rozwiązanie)
   a następnie usunąć wierzchołki z grafu, żeby móc go wykorzystać przy szukaniu odległości dla
   kolejnej pary wierszy bez straty na wydajności.
   
   W momencie obliczania prędkość dla pary wierszy można natknąć się na problemy związane
   z jakością danych oferowanych przez API. Zdarza się że wysłany sygnał pochodzi "spoza" linii
   trasy którą przebiega dana linia. Z tego powodu pod uwagę bierzemy tylko te wiersze dla których
   odległość punktu od trasy jest nie większa niż pewien ustalony limit (domyślnie 10 metrów).
   
   Kolejnym problemem jest fakt, że czasem któraś z wartości rekordu jest "przekłamana" - np.
   natrafić można na parę sygnałów identyfikowanych tym samym numerem linii oraz brygady, wysłanych
   w odstępie sekundy, natomiast punkty z których zostałe wysłane leżą po przeciwnej stronie miasta.
   Z tego powodu rekordy w których obliczona prędkość jest na pierwszy rzut oka niewłaściwa (domyślnie
   większa niż 80 km/h) nie są brane pod uwagę.
   
   Obliczone prędkości są umieszczane w liście, która następnie jest dołączana do ramki danych
   jako kolejna kolumna (`velocity`), a sama ramka jest zapisywana do pliku `*.csv` w katalogu 
   `results`.
    
   
## Built with
#### Frontend
- [leaflet](http://leafletjs.com/)
- [heatmap.js](https://www.patrick-wied.at/static/heatmapjs/)
- [jquery](https://jquery.com/)
- [bootstrap](https://getbootstrap.com/)
#### Backend
- [MongoDB](https://www.mongodb.com/)
- [Python](https://www.python.org/)
  - [Sanic](https://github.com/channelcat/sanic)
  - [pandas](http://pandas.pydata.org/)
  - PyMongo
#### Dane
- [UM Warszawa](https://api.um.warszawa.pl/)
- [Open Street Map](https://www.openstreetmap.org/)
