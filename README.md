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

## Build with
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
