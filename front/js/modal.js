var $ = require('jquery');

module.exports = function(){
  // Load a box, yks style !
  $('.box').each(function(i, box){
    load_inline_box(box);
  });

  // Modals show
  $(document).on('click', '.modal-action', load_modal);

  // Popover show
  $('[data-toggle="popover"]').popover();

  // Slugify inputs
	$('div.slugify input[type=text]').keyup(slugify);

  // Load anchor urls if available
  var hash = window.location.hash.substring(1);
  if(hash){
    var input = $('input[name="'+hash+'"]');
    var url = input.val();
    if(url)
      load_box(url, 'GET', {}, input.parent());
  }

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

  // Generic dropdown function
  // * update input value
  // * update selector
  var dropdown = function(){
    var value = $(this).attr('value');
    $(this).parent().addClass('active').siblings('li.active').removeClass('active');
    var selector = $(this).parents('div.dropdown');
    selector.find('input[type=hidden]').val(value);
    var btn = selector.find('button');
    btn.find('span.name').html($(this).html());
    selector.find('.btn-group').removeClass('open');
    return {
      btn : btn,
      value : value,
      selector : selector,
    }
  };

  // Sport choice dropdown
  $(document).on('click', 'form ul.sports li a', dropdown);

  // Session types dropdown
  $(document).on('click', 'form ul.types li a', function(){

    // Apply dropdown
    var dd = $.proxy(dropdown, this)();

    // Cleanup button class
    dd.btn.removeClass('rest').removeClass('training').removeClass('race');

    var rc = $(this).parents('form').find('div.race-category');
    if(dd.value == 'race'){

      // Show race category
      rc.show();

      // Button styling
      dd.btn.addClass('race');
    }else{

      // Hide race category
      rc.hide();

      // Button styling
      dd.btn.addClass(dd.value);

    }
  });

  // Don't reload page when hitting a dropdown choice
  $(document).on('click', 'form .dropdown-menu li a', function(evt){
    evt.preventDefault();
  });

  // Remember & activate tab for current page
  // in short lived page session storage
  var tab_name = 'tab:'+window.location.href;
  var tab_href = sessionStorage.getItem(tab_name);
  if(window.location.hash) // override by url
    tab_href = window.location.hash;
  if(tab_href){
    console.info("Showing tab : "+tab_href);
    $('a[href="'+tab_href+'"]').tab('show');
    sessionStorage.setItem(tab_name, tab_href);
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

  // Toggle friends display on calendar
  $('#toggle-friends button').on('click', function(evt){
    $('p.session.friends').toggle();
    var btn = $(evt.target);
    btn.hide();
    btn.siblings('button').show();
  });

  // Change date
  $('button.move_plan_session').datepicker({
    language : 'fr',
    todayHighlight : true,
    weekStart : 1,
  }).on('changeDate', function(evt){
    if(!evt.date)
      return;
    var btn = $(evt.target);
    var data = {
      psa : btn.attr('data-psa'),
      date : Math.floor(evt.date.getTime() / 1000),
    };
    load_box(btn.attr('data-url'), 'POST', data);
  });

  // Lock button during submit (on click)
  $('button[data-lock]').on('click', function(){
    var btn = $(this);
    var icon = $('<i>').addClass('icon-loading animate-spin');
    var msg = $('<span>').text(btn.attr('data-lock'));
    btn.html('').append(icon).append(msg).addClass('disabled');
  });
};

// Helper to add submit button data
// in serialization
function serialize_form(form, evt){
  var formData = form.serializeArray();

  // Add submit key/value
  if(evt && evt.originalEvent){
    var target = evt.originalEvent.explicitOriginalTarget || evt.originalEvent.target;
    formData.push({ name: target.name, value: target.value });
  }

  var data = {};
  $(formData).each(function(i, v){
    var k = v.name;
    if(data[k]){
      // Support multiple values
      if($.isArray(data[k])){
        // Append to array
        data[k].push(v.value);
      }else{
        // New array
        data[k] = [ data[k], v.value];
      }
    }else{
      // Direct usage
      data[k] = v.value;
    }
  });

  return data;
}

function submit_form(evt){
  evt.preventDefault();

  // Use datas from form
  var data = serialize_form($(this), evt);

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
    traditional : true, // Avoid dumb serialization with [] appended on arrays !
    success : function(data){

      // Override output from response
      if(data.output)
        output = $('#' + data.output);

      // Load a page
      if(data.status == 'load' && data.url){
        window.location = data.url;
        return;
      }

      // Reload boxes
      $.each(data.boxes, function(box, url){
        load_box(url, 'GET', {}, $('#'+box));
      });

      // Reload modales
      $.each(data.modales, function(i, url){
        load_box(url, 'GET', {}, 'modal');
      });

      // Close modal
      if($.inArray('close', data.options) != -1){
        if(modal == null){
          $('body').modalmanager('loading');
        }else{
          modal.modal('hide');
        }
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

      } else if(output instanceof jQuery) {
        // Render box element
        output.html(data.html);
        dom = output;

      } else {
        return;
      }

      // Trigger forms
      dom.find('form').on('submit', submit_form);

      // Add slow hideme trigger to fade out
      setInterval(function(){
        dom.find('.hideme').fadeOut('slow');
      }, 3000);

      // Load inline boxes
      dom.find('div.box').each(function(i, box){
        load_inline_box(box);
      });
    },
    error : function(xhr, st, err){
      // Hide box on forbidden access errors
      if((xhr && xhr.status == 403 || err == 'FORBIDDEN') && output instanceof jQuery){
        output.hide();
        return;
      }
      console.error("Failed to load box from "+url+" : "+err);

      // Try to show some errors in open modals
      if(output == 'modal'){
        var modals = $('body').modalmanager('getOpenModals');
        $.each(modals, function(i, m){
          $(m).find('.modal-error').show();
        });
      }
    }
  });

  // Move a plan session to another date
  $('.plan-session-move').datepicker({
    language : 'fr',
    todayHighlight : true,
    weekStart : 1,
  }).on('changeDate', function(evt){
    if(!evt.date)
      return;
    var btn = $(evt.target);
    var data = {
      psa : btn.attr('data-psa'),
      date : Math.floor(evt.date.getTime() / 1000),
    };
    load_box(btn.attr('data-href'), 'POST', data);
  });
}

// Load an inline box : yks style
function load_inline_box(box){
  if(!box.hasAttribute('data-src'))
    return;

  var src = box.getAttribute('data-src');
  console.info("Loading box "+src);

  load_box(src, 'GET', {}, $(box));
  box.removeAttribute('data-src'); // cleanup
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
  data = {};
  if(this.hasAttribute('data-action'))
    data['action'] = this.getAttribute('data-action');

  // Append extra data (start with data-post-)
  var filter = 'data-post-';
  $.each(this.attributes, function(i, attr){
    if(attr.name.substring(0, filter.length) != filter)
      return;
    data[attr.name.substring(filter.length)] = attr.value;
  });

  // Append target ?
  target = 'modal';
  if(this.hasAttribute('data-append')){
    target = $('<div/>', {'class': 'appended'});
    $('#' + this.getAttribute('data-append')).append(target)
  }

  // Replace target ?
  if(this.hasAttribute('data-replaces')){
    target = $('#' + this.getAttribute('data-replaces'));
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

// Slugify an input value and save it in a target input
function slugify(event){
  var target = $(this).parents('div.slugify').attr('data-target');
  if(!target)
    throw new Error("Missing slugify target");

  var str = $(this).val();
	str = str.toLowerCase();
	str = str.replace(/\s/g, '_');
  $(target).val(str);
}
