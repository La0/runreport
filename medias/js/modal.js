
$(function(){
  // Modals show
  $(document).on('click', '.modal-action', load_modal);

  // Link on other elements
  $(document).on('click', '.link', function(){
    var url = this.getAttribute('href');
    if(url)
      window.location.href = url;
  });

  // Form load
  $(document).on('submit', 'form.box', load_form);

  // Tooltips show
  $('.do-tooltip').tooltip();

  // Roles custom
  $(document).on('click', 'div.roles button.role', function(){
    if($(this).hasClass('disabled')) return false;
    $(this).parents('div.roles').find('input.role_value').val($(this).val());
  });

  // Sport choice
  // * update input value
  // * update selector
  $(document).on('click', 'form ul.sports li a', function(){
    var sport = $(this).attr('value');
    $(this).parent().addClass('active').siblings('li.active').removeClass('active');
    var selector = $(this).parents('div.sport-session');
    selector.find('input[type=hidden]').val(sport);
    var btn = selector.find('button');
    btn.find('span.name').html($(this).html());
    selector.find('.btn-group').removeClass('open');
  });

  // Session types
  // * update input value
  // * update selector
  $(document).on('click', 'form ul.types li a', function(){
    var type = $(this).attr('value');
    $(this).parent().addClass('active').siblings('li.active').removeClass('active');
    var selector = $(this).parents('div.types-name');
    selector.find('input[type=hidden]').val(type);
    var btn = selector.find('button');
    btn.removeClass('rest').removeClass('training').removeClass('race');
    var rc = $(this).parents('form').find('div.race-category');
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

  // Don't reload page when hitting a dropdown choice
  $(document).on('click', 'form .dropdown-menu li a', function(evt){
    evt.preventDefault();
  });

  // Remember & activate tab for current page
  // in short lived page session storage
  var tab_name = 'tab:'+window.location.href;
  var tab_href = sessionStorage.getItem(tab_name);
  if(tab_href){
    console.info("Showing tab : "+tab_href);
    $('a[href="'+tab_href+'"]').tab('show');
  }
  $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    // Save new tab
    tab_href = $(e.target).attr('href');
    sessionStorage.setItem(tab_name, tab_href);
    console.info("Saved tab : "+tab_href);
  });

  // Toggle messages actions on hover
  $(document).on('mouseenter mouseleave', 'div.actions-hover', function(evt){
    var actions = $(this).find('div.actions');
    if(evt.type == 'mouseenter'){
      actions.fadeIn();
    }else{
      actions.fadeOut('slow');
    }
  });
});

function submit_form(evt){
  evt.preventDefault();

  // Use datas from form
  var data = $(this).serialize();

  // Send data
  output = $(this).hasClass('box') ? $(this) : 'modal';
  load_box(this.getAttribute('action'), 'POST', data, output);
  return false;
}

// Load & Display a json "box"
var modal = null;
function load_box(url, method, data, output){
  method = method.toUpperCase();
  if(!output)
    output = 'box'; // Box by default
  if(output =='modal' && modal == null)
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

      // Reload boxes
      $.each(data.boxes, function(box, url){
        load_box(url, 'GET', {}, $('#'+box));
      });

      // Close modal
      if($.inArray('close', data.options) != -1 && modal != null){
        modal.modal('hide');
      }

      // Reload parent
      if($.inArray('body_reload', data.options) != -1){
        window.location = window.location;
        return;
      }

      var dom = null;
      if(output == 'modal'){
        // Build a new modal
        dom = $(data.html);
        modal = dom.modal({
          show : true,
          replace : true
        });

        // Trigger forms
        modal.find('form').on('submit', submit_form);

      } else if(output instanceof jQuery) {
        // Render box element
        output.html(data.html);
        dom = output;
      } else {
        return;
      }

      // Add slow hideme trigger to fade out
      setInterval(function(){
        dom.find('.hideme').fadeOut('slow');
      }, 3000);
    },
    error : function(xhr, st, err){
      console.error("Failed to load box from "+url+" : "+err);
    }
  });
}

// Init a modal, used from click
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

  // Append target ?
  target = 'modal';
  if(this.hasAttribute('data-append')){
    target = $('<div/>', {'class': 'appended'});
    $('#' + this.getAttribute('data-append')).append(target)
  }
  load_box(url, method, data, target);
  return false;
}

// Load a form
function load_form(evt){
  var url = this.getAttribute('action');
  var method = this.getAttribute('method');
  if(!url || !method){
    console.error("No url or method for form");
    return false;
  }
  evt.preventDefault();
  var data = $(this).serialize();
  load_box(url, method, data, $(this));
  return false;
}

// Autologin for demo
function demo(login, password){
  $('input[name="username"]').val(login);
  $('input[name="password"]').val(password);
  $('form.form-signin').submit();
  return false;
}
