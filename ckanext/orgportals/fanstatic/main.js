(function main() {

  $('#newly-released-data-btn').on('click', function () {
    if ($('#newly-released-data').hasClass('hidden')) {
      $('#newly-released-data-btn').html('');
      $('#newly-released-data').removeClass('hidden');
      $('#newly-released-data-btn').html('<i class="fa fa-compress pull-right"></i>');
    } else {
      $('#newly-released-data-btn').html('');
      $('#newly-released-data').addClass('hidden');
      $('#newly-released-data-btn').html('<i class="fa fa-expand pull-right"></i>');
    }
  });

  $('.orgportals-filters').on('change', function () {
    var url = $(this).val();

    if (url) {
      window.location = url + '#search-data';
    }

    return false;
  });

  var fontUrl = 'http://mmwebfonts.comquas.com/fonts/?font=zawgyi';

  $('head').append('<link rel="stylesheet" href="' + fontUrl + '" />')

})();

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}
