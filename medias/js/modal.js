
$(function(){
  // Modals show
  $('.modal-action').click(load_modal);

  // Roles custom
  $(document).on('click', 'div.roles button', function(){
    $(this).parents('div.roles').find('input.role_value').val($(this).val());
  });
});

function load_modal(evt){
  // Get url
  var url = this.getAttribute('href');
  if(!url){
    console.error("No url for modal");
    return false;
  }
  evt.preventDefault();

  $.ajax({
    url : url,
    method : 'GET',
    success : function(data){
      var modal = $(data);
      modal.find('form').on('submit', function(evt){
        evt.preventDefault();

        // Use datas from form
        data = {}
        modal.find(':input').each(function(){
          v = $(this).val();
          n = this.getAttribute('name');
          if(n && v)
            data[n] = v;
        });

        // Send data
        $.ajax({
          url : this.getAttribute('action'),
          method : 'POST',
          data : data,
          success : function(data){
            modal.modal('hide');
          },
        });
        return false;
      });
      modal.modal();
    }
  });
  return false;
}

