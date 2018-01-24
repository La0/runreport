console.info('Starting RunReport...');

// Load our theme (using sass)
require('scss/main.scss');
require('css/runreport-embedded.css');
require('css/animation.css');

// Bootstrap deps
require('bootstrap/dist/js/bootstrap.js');

// Load JS deps
var $ = require('jquery');

// Load Vue deps
var Vue = require('vue/dist/vue.js');

// Load our old scripts
var csrf = require('js/csrf.js');
var modal = require('js/modal.js');
var tracks = require('js/tracks.js');
var rating = require('js/rating.js');
var gear = require('js/gear.js');

// Share publicky
window.RRDashboard = require('js/dashboard.js');

// Boot jquery
$(function(){
	console.info('Booting jQuery...');
	csrf();
	modal();
	tracks();
	rating();
	gear();
});

// Setup Axios for API
var axios = require('axios');
axios.defaults.baseURL = '/api/v2';
axios.defaults.headers.common['X-CSRFTOKEN'] = document.querySelector('#csrf').getAttribute('content');


// Run modern vue js app
var app = new Vue({
  el : '#main',
  components : {
    StatsSports : require('vue/Stats/Sports.vue'),
  },
});
