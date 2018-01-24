var $ = require('jquery');

module.exports = function(){

  $('#gear .moderated span.btn').on('click', function(evt){
    var btn = $(this);
    var block = btn.parent().parent();
    var other = block.siblings('div');

    // Empty current val
    block.find(':input').val('');

    // Toggle blocks
    block.hide();
    other.show()

    // Activate & empty new one
    other.find(':input').val('').focus();
  });

};
