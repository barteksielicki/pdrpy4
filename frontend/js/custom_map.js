var CustomMap = function CustomMap(
  map_id,
  base_layer,
  heatmap_layer,
  center,
  scale
) {
  this.base_layer = base_layer;
  this.heatmap_layer = heatmap_layer;
  this.map = L.map(
    map_id,
    {layers: [base_layer, heatmap_layer]}
  ).setView(center, scale);
};

CustomMap.prototype.add_to_heatmap = function(heatmap_data) {
  heatmap_layer.addData(heatmap_data);
};
CustomMap.prototype.update_heatmap = function(heatmap_data) {
  console.log("Updating " + heatmap_data.length + " records.");
  // inverse records
  heatmap_data.forEach(function (element) {
    element.velocity = -element.velocity
  });
  heatmap_layer.setData({
    min: -40,
    max: 0,
    data: heatmap_data
  });
};
