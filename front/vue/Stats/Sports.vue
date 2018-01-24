<script>
var VueChart = require('vue-chartjs');
var axios = require('axios');

module.exports = {
  extends: VueChart.Line,
  props : {
    user: String,

  },
  mounted : function(){

    // Load data from api
    var url = '/user/' + this.user + '/stats/';
    axios.get(url).then(function(resp){
      console.log(resp.data);
      // TODO load data
    });

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
    var datasets = [
      {
        label: 'Data One',
        backgroundColor: '#f87979',
        data: [40, 39, 10, 40, 39, 80, 40]
      },
      {
        label: 'Data TWO',
        backgroundColor: '#79AA79',
        data: [0, 10, 100, 40, 39, 80, 40]
      }
    ];
    this.renderChart({
      labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
      datasets: datasets,
    }, options);
  }
}
</script>
