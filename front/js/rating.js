var MAX_STARS = 5;

var init_ratings = function(){

  // Get current star nb
  var star = $(this);
  var current = parseInt(star.attr('data-star'));

  // Activate stars <= current count
  for(var i = 1; i <= MAX_STARS; i++){
    if(i < current){
      star.siblings('.star-'+i).addClass('active');
    }else if(i == current){
      star.addClass('active');
    }else{
      star.siblings('.star-'+i).removeClass('active');
    }
  }

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
    if(saved)
      $.proxy(init_ratings, block.find('.star-'+saved))();

    return;
  }

  // Cleanup when not locked
  star.removeClass('active').siblings('.star').removeClass('active');
  star.parent().siblings('div.help').children('.level').removeClass('active');
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

// Handle hover
$(document.body).on('mouseover', 'div.rating .star', init_ratings);
$(document.body).on('mouseleave', 'div.rating div.stars', clear_ratings);

// Handle click to update note
$(document.body).on('click', 'div.rating .star', save_rating);
