
$(function(){
  // Modals show
  $('.modal-action').click(load_modal);
  
});

function load_modal(){
  var url = this.getAttribute('href');
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
}

