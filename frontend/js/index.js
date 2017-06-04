'use strict';

var API_URL = 'http://192.166.219.242:1337/speed';

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
  "radius": 0.0002,
  "maxOpacity": .6,
  // scales the radius based on map zoom
  "scaleRadius": true,
  // if set to false the heatmap uses the global maximum for colorization
  // if activated: uses the data maximum within the current map boundaries
  //   (there will always be a red spot with useLocalExtremas true)
  useLocalExtrema: false,
  // gradient
  minOpacity: .6,
  gradient: {
    0: 'lime',
    .1: 'green',
    .2: 'cyan',
    .6: 'yellow',
    .8: 'orange',
    .9: 'red'
  },
  // which field name in your data represents the latitude - default "lat"
  latField: 'latitude',
  // which field name in your data represents the longitude - default "lng"
  lngField: 'longtitude',
  // which field name in your data represents the data value - default "value"
  valueField: 'velocity'
};
var heatmap_layer = new HeatmapOverlay(cfg);


var map = new CustomMap(
  'main-map',
  base_layer,
  heatmap_layer,
  [52.222122, 21.007040],
  12
);


var timepicker_options = {
  timeFormat: "H:i", step: 60
};
$('.timepicker').timepicker(timepicker_options);

$("#main-form").submit(function (event) {
  event.preventDefault(); // to stop the form from submitting
  var hour = 60 * 60 * 1000;
  var dateFrom = new Date(
    $("select[name='day-select']").val() + "T" + $("input[name='time-input']").val()
  ).getTime() + (2 * hour);
  var dateTo = dateFrom + hour;
  var line = $("input[name='line-input']").val();
  var query_params = {
    'timestamp_from': dateFrom, 'timestamp_to': dateTo
  };

  if (line != "")
    query_params['line'] = parseInt(line);

  $.get(API_URL, query_params)
    .done(function (data) {
      console.log("Done!");
      map.update_heatmap(data.records);
    })
    .fail(function () {
      console.log("Error!");
    });
});

// tooltip
var map_div = document.querySelector('#main-map');
var tooltip = document.querySelector('.tooltip');

function update_tooltip(x, y, value) {
  // + 10 for distance to cursor
  var transl = 'translate(' + (x + 10) + 'px, ' + (y + 10) + 'px)';
  tooltip.style.webkitTransform = transl;
  tooltip.innerHTML = value;
};

map_div.onmousemove = function(ev) {
  var x = ev.layerX;
  var y = ev.layerY;
  var value = heatmap_layer._heatmap.getValueAt({
    x: x,
    y: y
  });
  console.log("x = ", x, "y = ", y, "speed = ", value);
  tooltip.style.display = 'block';
  update_tooltip(x, y, value);
};
// hide tooltip on mouseout
map_div.onmouseout = function() {
  tooltip.style.display = 'none';
};
