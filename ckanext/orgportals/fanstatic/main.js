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

  $('head').append('<link rel="stylesheet" href="' + fontUrl + '" />');

  _setActiveLanguage();

  /*
   * Set the active language in the language picker
   * based on the active locale
   */
  function _setActiveLanguage() {
    var languageSelector = $('.language-selector');
    var currentLanguage = $('html').attr('lang');
    var languageElement;

    if (currentLanguage === 'en') {
      languageElement = languageSelector.find('li')[0];
    } else {
      languageElement = languageSelector.find('li')[1];
    }

    if (languageElement) {
      languageElement.className = 'active';
    }
  }

  var downloadAsPDFBtn = $('#download-as-pdf');

  downloadAsPDFBtn.on('click', function() {
    var promise = html2canvas($('body')[0]);

    promise.then(function(canvas) {
      var doc = new jsPDF('p', 'mm', [500, 500]);
      var image = canvas.toDataURL('image/png');

      doc.addImage(canvas, 'PNG', 0, 0, 0, 0);
      doc.save("dataurlnewwindow.pdf");
    });
  });

})();

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}
