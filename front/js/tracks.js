var $ = require('jquery');
var L = require('leaflet');

module.exports = function(){
  $('div.track_map').each(show_track_map);
  $('div.point_map').each(show_point_map);
};


// Simply build an OSM empty map
function init_map(element){
  var map = L.map(element);
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: 'Proudly powered by <a href="http://openstreetmap.org">OpenStreetMap</a>',
  }).addTo(map);
  return map;
}

// Show a track map
function show_track_map(){
  var url = this.getAttribute('data-src');
  if(!url)
    return;

  // Load map data
  var that = this;
  console.info("Show map from "+url);
  $.ajax({
    url : url,
    method : 'GET',
    type : 'json',
    success : function(track){
      // Add track using simple polyline
      var map = init_map(that);
      var polygon = L.polyline(track.coordinates).addTo(map);
      map.fitBounds(polygon.getBounds());
    },
    error: function(err){
      if(err.status == 403)
        $(that).empty().append($('<div/>', {
          text : 'You can\'t view this map',
          class : 'alert alert-danger',
        }));
      else
        console.error(err);
    },
  });
}

function show_point_map(){
  // Fetc lat & lon attributes
  var lat = this.getAttribute('data-lat');
  var lon = this.getAttribute('data-lon');
  if(!lat || !lon){
    console.error("Missing lat/lon to show a point on map.");
    return;
  }

  // Specific icon
  var LeafIcon = L.Icon.extend({
    options: {
      shadowUrl: '/static/img/leaflet/marker-shadow.png',
      iconSize:     [25, 41],
      shadowSize:   [41, 41],
    }
  });

  var icon = new LeafIcon({
    iconUrl: '/static/img/leaflet/marker-icon.png',
  });

  // Add point as a marker to map
  var map = init_map(this);
  var point = [parseFloat(lat), parseFloat(lon)];
  L.marker(point, {icon : icon}).addTo(map);
  map.setView(point, 13);
}
