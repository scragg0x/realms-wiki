$(function(){
  $(".ajax-form").submit(function(e){
    e.preventDefault();

    var submitting = 'submitting';

    if ($(this).data(submitting)) {
      return;
    }

    $(this).data(submitting, 1);

    var action = $(this).attr('action');
    var method = $(this).attr('method');
    var redirect = $(this).data('redirect');
    var data = $(this).serialize();

    var req = $.ajax({
      type: method,
      url: action,
      data: data,
      dataType: 'json'
    });

    req.done(function() {
      if (redirect) {
        location.href = redirect;
      }
    });

    req.fail(function(data, status, error) {
      console.log(data);
    });

    req.always(function() {
      $(this).removeData(submitting);
    });

  });
});