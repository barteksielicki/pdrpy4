'use strict';

var API_URL = 'localhost:1337/'

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


var timepicker_options = {
  twentyFour: true, //Display 24 hour format, defaults to false
  upArrow: 'wickedpicker__controls__control-up', //The up arrow class selector to use, for custom CSS
  downArrow: 'wickedpicker__controls__control-down', //The down arrow class selector to use, for custom CSS
  close: 'wickedpicker__close', //The close class selector to use, for custom CSS
  hoverState: 'hover-state', //The hover state class to use, for custom CSS
  title: 'Timepicker', //The Wickedpicker's title,
  showSeconds: false, //Whether or not to show seconds,
  secondsInterval: 1, //Change interval for seconds, defaults to 1
  minutesInterval: 1, //Change interval for minutes, defaults to 1
  beforeShow: null, //A function to be called before the Wickedpicker is shown
  show: null, //A function to be called when the Wickedpicker is shown
  clearable: true, //Make the picker's input clearable (has clickable "x")
};
$('.timepicker').wickedpicker(timepicker_options);


var update_speed = function(day, time, line) {
  var query_params = {
    'time': time,
    'line': line
  };
  if (line)
    query_params['line'] = line;
  $.get(API_URL + 'speed', query_params)
    .done(function(data) {
      var records = data['records'];
      for(var record in records) {
        trams[record['line']].update(new_speed=record['speed']);
      }
    })
    .fail(function() {
      console.log('GET ERROR!');
    });
};

$("#main-form").submit(function(event) {
  event.preventDefault(); // to stop the form from submitting
  update_speed(
    $("select[name='day-select']")[0].value,
    $("input[name='time-input']")[0].value,
    $("input[name='line-input']")[0].value
  );
  this.submit();
});
