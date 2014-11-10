$(function(){

  $('div.track_map').each(show_map);

});


// Show a track map
function show_map(){
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
      // Init map
      var map = L.map(that);
      L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Proudly powered by <a href="http://openstreetmap.org">OpenStreetMap</a>',
      }).addTo(map);

      // Add track using simple polyline
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
