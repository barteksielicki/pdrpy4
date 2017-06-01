var Tram = function Tram(number, lat_lon, speed, icon) {
  this.number = number;
  var _speed;
  Object.defineProperty(this, 'speed', {
        get: function() { return _speed; },
        set: function(new_speed){ _speed = new_speed; }
      });
  this.speed = speed;
  var _position;
  Object.defineProperty(this, 'position', {
        get: function() { return _position; },
        set: function(new_position){ _position = new_position; }
      });
  this.position = lat_lon;
  this.icon = icon;
  this.marker = null;
};

Tram.prototype.label = function() {
  return [
    '<div class="tram-popup">',
    '  <div class="tram-number">',
    '    ' + this.number,
    '  </div>',
    '  <div class="tram-speed">',
    '    ' + this.speed + ' km/h',
    '  </div>',
    '</div>'
  ].join('\n');
};
Tram.prototype.update = function(new_speed=null, new_position=null) {
  var flag = false;
  if (new_speed != null) {
    this.speed = new_speed;
    flag = true;
  }
  if (new_position != null) {
    this.position = new_position;
    flag = true;
  }
  if (flag)
    this.update_marker();
};
Tram.prototype.add_to_map = function(map) {
  if (this.marker == null) {
    this.marker = L.marker(this.position, {icon: this.icon}).addTo(map);
    marker.bindPopup(self.label());
  }
};
Tram.prototype.update_marker = function() {
  if(this.marker) {
    this.marker.setLatLng(this.position);
    this.marker._popup.setContent(this.label());
  }
};
Tram.prototype.to_heatmap_data = function() {
  return {
    'lat': this.position[0],
    'lng': this.position[1],
    'speed': this.speed
  };
};
