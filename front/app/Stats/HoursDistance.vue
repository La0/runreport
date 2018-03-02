<script>
var VueChart = require('vue-chartjs');

module.exports = {
  extends: VueChart.Line,
  mounted : function(){
    var options = {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        xAxes: [{
          label: "plop"
        }],
        yAxes: [
          {
            label: "Y1",
          },
          {
            label: "Y2",
          },
        ],
      },
    };
    var datasets = [];
    datasets[0] = this.
    var labels = _.map(this.stats.periods, function(period){
      // TODO: use store locale
      var d = new Date(period * 1000);
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
