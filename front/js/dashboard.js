var RING_MAX_SIZE = 400;

// Colors
var RING_COLOR_SESSIONS = '#F00';
var RING_COLOR_DISTANCE = '#0F0';
var RING_COLOR_HOURS = '#00F';
var RING_COLOR_DATE = '#000';

// Helper to draw a raphel slice of a circle
var slice = function (canvas, cx, cy, r, startAngle, percent, params) {
  var rad = Math.PI / 180;
  var endAngle = startAngle + percent * 180.0;

  var x1 = cx + r * Math.cos(-startAngle * rad);
  var x2 = cx + r * Math.cos(-endAngle * rad);
  var y1 = cy + r * Math.sin(-startAngle * rad);
  var y2 = cy + r * Math.sin(-endAngle * rad);

  return canvas.path([
    "M", cx, cy,
    "L", x1, y1,
    "A", r, r, 0, +(endAngle - startAngle > 180),
    0, x2, y2, "z"]
  ).attr(params);
}

var display_week_rings = function(){

  // Setup main raphael zone
  var zone = $('#rings');
  var ring_size = Math.min(zone.width() / this.length, RING_MAX_SIZE);
  var margin_y = 100;
  var r = Raphael(zone[0], zone.width(), ring_size + margin_y);

  // Init data
  var weeks = [];
  var max = {
    sessions : 0,
    hours : 0,
    distance : 0,
  };

  $.each(this, function(index, elt){
    // Get values from html elements
    // Store index & element too
    var week_elt = $(elt);
    var week = {
      index : index,
      sessions : parseInt(week_elt.attr('data-sessions')) || 0,
      distance : parseFloat(week_elt.attr('data-distance')) || 0,
      hours : parseFloat(week_elt.attr('data-hours')) || 0,
      element : week_elt,
    };
    weeks.push(week);

    // Search max values
    max.sessions = Math.max(max.sessions, week.sessions);
    max.distance = Math.max(max.distance, week.distance);
    max.hours = Math.max(max.hours, week.hours);
  });

  // Display normalized data as rings
  $.each(weeks, function(index, week){
    // Calc radius for current week
    // Based on available ring size
    var radius = Math.max(week.sessions * ring_size / (2 * max.sessions), 5);

    // Calc center of rings
    var x = ring_size * (week.index + 0.5);
    var y = ring_size / 2.0;

    // Draw slice for distance
    slice(r, x, y, radius, 90, week.distance / max.distance, {
      stroke : 'none',
      fill : RING_COLOR_DISTANCE,
      opacity : 0.4,
    });

    // Draw slice for hours
    slice(r, x, y, radius, 270, week.hours / max.hours, {
      stroke : 'none',
      fill : RING_COLOR_HOURS,
      opacity : 0.4,
    });

    // Draw main rings for sessions
    var ring = r.circle(x, y, radius * 0.8).attr({
      stroke: "none",
      fill: RING_COLOR_SESSIONS,
      opacity : 1.0,
    });

    // Draw date on bottom of ring
    r.text(x, ring_size + 20, week.element.find('.date').text()).attr({
      fill : RING_COLOR_DATE,
      'font-size' : 14,
      'font-family' : 'Arial, Helvetica, sans-serif',
    });

    // Draw sessions nb
    if(week.sessions > 0){
      r.text(x, ring_size / 2.0, week.sessions).attr({
        fill : RING_COLOR_SESSIONS,
        'font-size' : 18,
        'font-family' : 'Arial, Helvetica, sans-serif',
      });
    }

    // Draw distance
    if(week.distance > 0){
      r.text(x - radius, ring_size / 4.0, Math.round(week.distance) + ' km').attr({
        fill : RING_COLOR_DISTANCE,
        'font-size' : 12,
        'font-family' : 'Arial, Helvetica, sans-serif',
      });
    }

    // Draw hours
    if(week.hours > 0){
      r.text(x + radius, ring_size * 3 / 4.0, Math.round(week.hours) + 'h' ).attr({
        fill : RING_COLOR_HOURS,
        'font-size' : 12,
        'font-family' : 'Arial, Helvetica, sans-serif',
      });
    }

    ring[0].onmouseover = function(){
      console.info('Mouse over', week);
    };

  });
};

// Expose as jquery plugin
$.fn.ringify = display_week_rings;
