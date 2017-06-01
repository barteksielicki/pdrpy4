'use strict';

// base layer
var base_layer = L.tileLayer(
  'https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={access_token}',
  {
    maxZoom: 20,
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' + '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' + 'Imagery © <a href="http://mapbox.com">Mapbox</a>',
    id: 'mapbox.streets',
    access_token: 'pk.eyJ1Ijoic2thcnp5bnNraWwiLCJhIjoiY2ozYnpxZmoyMDAwMDJ4bG40NHljYmV4aSJ9.USuWvX5MvkmeA4IrrHheHA'
});

// heatmap layer
var cfg = {
  // radius should be small ONLY if scaleRadius is true (or small radius is intended)
  // if scaleRadius is false it will be the constant radius used in pixels
  "radius": 1,
  "maxOpacity": .8,
  // scales the radius based on map zoom
  "scaleRadius": true,
  // if set to false the heatmap uses the global maximum for colorization
  // if activated: uses the data maximum within the current map boundaries
  //   (there will always be a red spot with useLocalExtremas true)
  "useLocalExtrema": true,
  // which field name in your data represents the latitude - default "lat"
  latField: 'lat',
  // which field name in your data represents the longitude - default "lng"
  lngField: 'lng',
  // which field name in your data represents the data value - default "value"
  valueField: 'speed'
};
var heatmap_layer = new HeatmapOverlay(cfg);

var tram_icon = L.icon({
      iconUrl: '../assets/tram.png',
      // size of the icon
      iconSize:     [42, 42],
      // point of the icon which will correspond to marker's location
      iconAnchor:   [22, 94],
      // point from which the popup should open relative to the iconAnchor
      popupAnchor:  [-3, -76],
      className: 'tram-icon'
});

var map = new CustomMap(
  'main-map',
  base_layer,
  heatmap_layer,
  [52.222122, 21.007040],
  13
);
