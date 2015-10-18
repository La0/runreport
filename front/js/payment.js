// Configure Mangopay
var mangopay_init = function(client_id, debug, registration){
  if(debug)
    mangoPay.cardRegistration.baseURL = "https://api.sandbox.mangopay.com";
  else
    mangoPay.cardRegistration.baseURL = "https://api.mangopay.com";
  mangoPay.cardRegistration.clientId = client_id;

  // Second registration step
  mangoPay.cardRegistration.init({
    cardRegistrationURL: registration.url,
    preregistrationData: registration.data,
    accessKey: registration.key,
    Id: registration.id,
  });
};

// Register card using form data
var mangopay_register_card = function(evt){
  evt.preventDefault();

  // Disable action
  var form = $(this);
  form.find('button.action').hide();
  form.find('button.waiter').removeClass('hidden').show();

  // Load form data
  var data = {};
  $.each(form.serializeArray(), function(i, d){
    data[d.name] = d.value;
  });

  // Filter data
  var cardData = {
    cardNumber: data.number,
    cardExpirationDate: data.month + data.year,
    cardCvx: data.cvc,
    cardType: data.type,
  };

  // Remove all errors
  $('div.form-group.has-error').removeClass('has-error').children('.help-block').addClass('hidden');
  form.find('div.alert-danger').addClass('hidden');

  var onSuccess = function(resp){
    console.info('Card registered', resp);

    // Send registration data to our backend
    var validation = {
      'club' : data.club,
      'id' : resp.Id,
      'card' : resp.CardId,
      'data' : resp.RegistrationData,
    }
    $.ajax({
      url : '/api/v1/payment/card/',
      data : validation,
      dataType : 'json',
      method : 'POST',

      // Handle 3DS or display success
      success : function(resp){
        if(resp.redirect){
          window.location.href = resp.redirect;
        }else{
          $('form#payment').hide();
          $('div.alert-success').removeClass('hidden');
        }
      },

      // Log errors
      error : function(err){
        console.error('Card validation failed', err);
        retry('Vaidation failed, please retry.');
      },
    });
  };

  // Display retry error message
  var retry = function(message){
    form.find('div.alert-danger').removeClass('hidden').find('p').html(message);

    // Add button to reload
    form.find('button, a.action').hide();
    form.find('a.retry').removeClass('hidden');
  };

  // Error handling
  var onError = function(resp){
    console.error('Card failed', resp);

    // Filter errors
    var msg = resp.ResultMessage;
    var errors = [];
    switch(msg){
      case 'CARD_NUMBER_FORMAT_ERROR':
        errors.push('card-number');
        break;
      case 'EXPIRY_DATE_FORMAT_ERROR':
      case 'PAST_EXPIRY_DATE_ERROR':
        errors.push('expiry');
        break;
      case 'CVV_FORMAT_ERROR':
        errors.push('cvc');
        break;
    };

    // Display errors
    $.each(errors, function(i, err){
      var input = $('#'+err);
      if(!input)
        return;
      var block = input.parent().addClass('has-error');
      block.find('.help-block').removeClass('hidden');
    });

    // Generic error
    if(resp.Status == 'ERROR')
      return retry(msg);

    // Restore action button
    form.find('button.waiter').hide();
    form.find('button.action').show();
  };

  // Do the actual registration !
  mangoPay.cardRegistration.registerCard(cardData, onSuccess, onError);
};

// Register card on form submit
$('form#payment').on('submit', mangopay_register_card);
