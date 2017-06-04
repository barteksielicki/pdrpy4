var CustomMap = function CustomMap(map_id,
                                   base_layer,
                                   heatmap_layer,
                                   center,
                                   scale) {
  this.base_layer = base_layer;
  this.heatmap_layer = heatmap_layer;
  this.map = L.map(
    map_id,
    {layers: [base_layer, heatmap_layer]}
  ).setView(center, scale);
};

CustomMap.prototype.add_to_heatmap = function (heatmap_data) {
  heatmap_layer.addData(heatmap_data);
};
CustomMap.prototype.update_heatmap = function (heatmap_data) {
  console.log("Updating " + heatmap_data.length + " records.");

  values = heatmap_data.map(function (el) {
    return el.velocity
  });
  var min = values.reduce(function (prev, curr) {
    return prev < curr ? prev : curr;
  });
  var max = values.reduce(function (prev, curr) {
    return prev > curr ? prev : curr;
  });
  var mean = values.reduce(function (a, b) {
    return a + b;
  }) / heatmap_data.length;

  heatmap_data.forEach(function (element) {
    element.velocity = -element.velocity
  });

  var gradient = {};
  gradient[0] = 'lime';
  gradient[1 - mean / max] = 'green';
  gradient[.995] = 'yellow';
  gradient[.999] = 'red';

  heatmap_layer.setData({
    min: max,
    max: min,
    data: heatmap_data
  });

  heatmap_layer._heatmap.configure({
    gradient: gradient
  });
  heatmap_layer._draw();
  return {
    "total": heatmap_data.length,
    "average": mean
  }
};
