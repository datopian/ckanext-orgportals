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

  var downloadAsBtn = $('.snapshot-dashboard-menu');

  downloadAsBtn.on('click', function(event) {
    var target = event.target;
    var dataAttribute = target.getAttribute('data-download-as');
    var renderedCanvas;

    // Scroll the window to top, in order to capture the entire screen
    window.scrollTo(0, 0);

    _hideElementsBeforeDownload();

    html2canvas($('body')[0]).then(function(canvas) {
      var image = canvas.toDataURL('image/png');
      var doc;

      if (dataAttribute === 'pdf') {
        doc = new jsPDF('portrait', 'mm', [document.body.offsetWidth / 3.85, document.body.offsetHeight * 0.9]);
        doc.addImage(canvas, 'PNG', 0, 0, 0, 0);
        doc.save('download.pdf');
      } else if (dataAttribute === 'image') {
        Canvas2Image.saveAsPNG(canvas);
      }

      _showElementsAfterDownload();
    });
  });

  var heroMap = $('.hero-map-wrap');
  var newData = $('.new-data');
  var allData = $('.all-data');

  function _hideElementsBeforeDownload() {
    downloadAsBtn.parent().toggleClass('open');
    heroMap.hide();
    newData.hide();
    allData.hide();
  }

  function _showElementsAfterDownload() {
    heroMap.show();
    newData.show();
    allData.show();
  }

})();

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}
