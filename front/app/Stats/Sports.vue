<script>
var VueChart = require('vue-chartjs');

module.exports = {
  extends: VueChart.Line,
  props : {
  },
  mounted : function(){
    var options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        xAxes: [{
          stacked: true,
        }],
        yAxes: [{
          stacked: true
        }],
      },
    };
    var datasets = this.stats.sports;
    var labels = _.map(this.stats.periods, function(period){
      // TODO: use store locale
      var d = new Date(period.timestamp * 1000);
      var month = d.toLocaleString(this.$store.state.locale, { month: "long" });
      return month + " " + d.getFullYear();
    }.bind(this));
    this.renderChart({
      labels: labels,
      datasets: datasets,
      options: options,
    });
  },
  computed : {
    stats : function(){
      return this.$store.state.stats;
    },
  },
}
</script>
