
$(function(){
  // Modals show
  $(document).on('click', '.modal-action', load_modal);

  // Roles custom
  $(document).on('click', 'div.roles button.role', function(){
    if($(this).hasClass('disabled')) return false;
    $(this).parents('div.roles').find('input.role_value').val($(this).val());
  });

  // Session types
  // * update input value
  // * update selector
  $(document).on('click', 'ul.types li a', function(){
    var type = $(this).attr('value');
    $(this).parent().addClass('active').siblings('li.active').removeClass('active');
    var selector = $(this).parents('div.types-name');
    selector.find('input[type=hidden]').val(type);
    var btn = selector.find('button');
    btn.removeClass('rest').removeClass('training').removeClass('race');
    var rc = $(this).parents('fieldset').find('div.race-category');
    if(type == 'race'){

      // Show race category
      rc.show();

      // Button styling
      btn.addClass('race');
    }else{

      // Hide race category
      rc.hide();

      // Button styling
      btn.addClass(type);
		
    }
    btn.find('span.name').html($(this).text());
    selector.find('.btn-group').removeClass('open');
  });
});

function submit_form(evt){
  evt.preventDefault();

  // Use datas from form
  var data = $(this).serialize();

  // Send data
  load_box(this.getAttribute('action'), 'POST', data);
  return false;
}

// Load & Display a json "box"
var modal = null;
function load_box(url, method, data){
  if(modal == null)
    $('body').modalmanager('loading'); // loading state

  $.ajax({
    url : url,
    method : method,
    data : data ? data : null,
    dataType : 'json',
    success : function(data){

      // Load a page
      if(data.status == 'load' && data.url){
        window.location = data.url;
        return;
      }

      // Close modal
      if($.inArray('close', data.options) != -1 && modal != null){
        modal.hide();
        $('.modal-backdrop').remove();
        $('.modal-scrollable').remove();
      }

      // Reload parent
      if($.inArray('body_reload', data.options) != -1){
        window.location = window.location;
        return;
      }

      // Build a new modal
      modal = $(data.html).modal({
        show : true,
        replace : true,
      });

      // Trigger forms
      modal.find('form').on('submit', submit_form);
    },
  });
}

// Init methos, used from click
function load_modal(evt){
  // Get url
  var url = this.getAttribute('href');
  if(!url){
    console.error("No url for modal");
    return false;
  }
  evt.preventDefault();
  method = $(this).hasClass('modal-post') ? 'POST' : 'GET';
  data = null;
  if(this.hasAttribute('data-action'))
    data = { 'action' : this.getAttribute('data-action')};
  load_box(url, method, data);
  return false;
}

