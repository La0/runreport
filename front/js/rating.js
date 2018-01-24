var $ = require('jquery');

var MAX_STARS = 5;

// List all the css class for stars
// used to remove
var all_stars = function(){
  var stars = [];
  for(var i = 1; i <= MAX_STARS; i++)
    stars.push('star-'+i);
  return stars.join(' '); // space separated
};

var init_ratings = function(current){

  // Get current star nb
  var star = $(this);
  if(!current || typeof current === "object")
    current = parseInt(star.attr('data-star'));

  // Activate stars <= current count
  var stars = star.parent().children('.star');
  $.each(stars, function(i, s){
    var index = i + 1; // offset by 1
    $(s).removeClass(all_stars);
    if(index <= current)
      $(s).addClass('star-'+current);
  });

  // Show current help
  var help = star.parent().siblings('div.help');
  help.children('.level').removeClass('active');
  help.find('.level-'+current).addClass('active');
};

// Restore & Cleanup
var clear_ratings = function(){
  var block = $(this);

  if(block.hasClass('locked')){

    // Restore locked value
    var saved = parseInt(block.siblings('input').val()) ;
    if(saved){
      $.proxy(init_ratings, block.find('.star').first())(saved);
    }

    return;
  }

  // Cleanup when not locked
  block.children('.star').removeClass(all_stars);
  block.siblings('div.help').children('.level').removeClass('active');
};

// Save a new rating
var save_rating = function(){

  // Get current star nb
  var star = $(this);
  var current = parseInt(star.attr('data-star'));

  // Update hidden input
  var block = star.parent();
  block.siblings('input').val(current);

  // Mark star list as locked
  block.addClass('locked');
};

module.exports = function(){
  // Handle hover
  $(document.body).on('mouseover', 'div.rating .star', init_ratings);
  $(document.body).on('mouseleave', 'div.rating div.stars', clear_ratings);

  // Handle click to update note
  $(document.body).on('click', 'div.rating .star', save_rating);
}
