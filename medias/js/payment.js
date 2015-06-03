$(function(){
  $('form#payment').on('submit', function(evt){
    evt.preventDefault()

    // Validate datas
    var form_data = {}
    var errors = [];
    $.each($(this).serializeArray(), function(){
      form_data[this.name] = this.value;
    });
    if(!form_data['card-name'])
      errors.push('card-name');
    if(!paymill.validateCardNumber(form_data['card-number']))
      errors.push('card-number');
    if(!paymill.validateExpiry(form_data['expiry-month'], form_data['expiry-year']))
      errors.push('expiry');
    if(!paymill.validateCvc(form_data['cvc']))
      errors.push('cvc');

    // Hide errors, for cleanup
    $('form#payment div.form-group').removeClass('has-error').find('p.help-block').addClass('hidden');

    // Apply errors
    if(errors.length > 0){
      console.warn('errors', errors);
      $.each(errors, function(index, err){
        var group = $('form#payment #'+err).parents('div.form-group');
        group.addClass('has-error');
        group.find('p.help-block').removeClass('hidden');
      });

      return false;
    }

    // Lock submit button to prevent further clicks
    $('form#payment button[type="submit"]').attr('disabled', 'disabled');

    // Create Paymill token
    var token_data = {
      number:         form_data['card-number'],
      exp_month:      form_data['expiry-month'],
      exp_year:       form_data['expiry-year'],
      cvc:            form_data['cvc'],
      amount_int:     form_data['amount'],
      currency:       form_data['currency'],
      cardholder:     form_data['name'],
    };
    paymill.createToken(token_data, function(error, result){
      if(error){
        // Display errors
        console.error('Paymill errors', error);
      }else{
        // Send token to Backend
        console.info('Paymill token created', error, result);
        result['offer'] = form_data['offer'];
        $.ajax({
          type: "POST",
          url: '/api/v1/payment/token/',
          data: result,
          success : function(resp){
            console.info('Payment succeeded');
            window.location.href = '/premium';
          },
          error : function(err){
            console.error("Payment error", err);
            alert('Do some stuff, bad boy');
          },
          dataType: 'json',
        });
      }
    });

    return false;
  });
});
