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
};

// Cleanup
var clear_ratings = function(){
  var star = $(this);
  if(star.parent().hasClass('locked'))
    return;
  star.removeClass('active').siblings('.star').removeClass('active');
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
$(document.body).on('mouseout', 'div.rating .star', clear_ratings);
//$('div.rating .star').hover(init_ratings, clear_ratings);

// Handle click to update note
$(document.body).on('click', 'div.rating .star', save_rating);
//$('div.rating .star').on('click', save_rating);
