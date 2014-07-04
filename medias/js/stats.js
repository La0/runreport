var months = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Décembre'];
var months_short = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aout", "Sep", "Oct", "Nov", "Déc"];

function plot_hours_distances(hours, distances){

  // Hours & distances
	$.plot("#stats .hours_distances", [
    { data: distances, label: "Distances" },
    { data: hours, label: "Heures", yaxis: 2 }
  ], {
  xaxes: [ { 
    mode : 'time',
    timeformat: "%b %Y",
    monthNames: months_short,
  } ],
  legend: { position: "sw" },
  series: {
    lines: {
      show: true
    },
    points: {
      show: true
    }
  },
  yaxes: [ { min: 0 }, {
    min: 0,
    alignTicksWithAxis: true,
    position: 'right',
    }],
    grid: {
      hoverable: true,
    },
  });

  // Tooltip
  var tooltip = $("#stats .tooltip");
  $("#stats .hours_distances").on("plothover", function (event, pos, item) {
    if(!item){
      tooltip.hide();
      return;
    }

    // Display the tooltip
    var unit = item.series.label == 'Heures' ? 'h' : 'km';
    var date = new Date(item.datapoint[0]);
    
    var val = item.datapoint[1];
    if (unit == 'km')
      val = val.toFixed(2);
    tooltip.html(months[date.getMonth()] + " " + date.getFullYear() + " : " + val + "  " + unit)
      .css({top: item.pageY+5, left: item.pageX+5})
      .fadeIn(200);
  });
}

function plot_sports(sports){

  // Sports
  $.plot("#stats .sports", sports, {
    legend: { position: "sw" },
    xaxis: { 
      mode : 'time',
      timeformat: "%b %Y",
      monthNames: months_short,
    },
    yaxis : {
      min: 0,
    },
    series: {
      stack: true,
      bars: {
        show: true,
        fill: true,
        barWidth: 24 * 60 * 60 * 1000 * 15, // for time series, with must be set in seconds !
      }
    }
  });

}
