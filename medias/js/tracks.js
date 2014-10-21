$(function(){

  $('div.track_map').each(show_map);

});


// Show a track map
function show_map(){
  var url = this.getAttribute('data-src');
  if(!url)
    return;

  // Init map
  var map = L.map(this);
  L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Proudly powered by <a href="http://openstreetmap.org">OpenStreetMap</a>',
  }).addTo(map);

  // Load map data
  console.info("Show map from "+url);
  $.ajax({
    url : url,
    method : 'GET',
    type : 'json',
    success : function(track){
      // Add track using simple polyline
      var polygon = L.polyline(track.coordinates).addTo(map);
      map.fitBounds(polygon.getBounds());
    }
  });
}
