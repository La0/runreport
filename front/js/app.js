console.info('Starting RunReport...');

// Load our theme (using sass)
require('scss/main.scss');
require('css/runreport-embedded.css');
require('css/animation.css');

// TODO: add bootstrap datepicker

// Load JS deps
var $ = require('jquery');

// Load our old scripts
var csrf = require('js/csrf.js');
var modal = require('js/modal.js');
var tracks = require('js/tracks.js');
var stats = require('js/stats.js');
var dashboard = require('js/dashboard.js');
var rating = require('js/rating.js');
var gear = require('js/gear.js');
require('js/config.js');

// Boot jquery
$(function(){
	console.info('Booting jQuery...');
	csrf();
	//modal(); // disabled for now
	tracks();
	//stats(); // not a function
	//dashboard(); // not a function
	rating();
	gear();

});
