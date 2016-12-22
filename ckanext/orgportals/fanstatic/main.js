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

  var fontUrl = 'https://mmwebfonts.comquas.com/fonts/?font=zawgyi';

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

  var snapshotDashboardMenu = $('.snapshot-dashboard-menu');
  var subdashboardMeta = $('#subdashboard-meta');
  var orgName = subdashboardMeta.attr('data-org-name') || 'org-name';
  var subdashboardName = subdashboardMeta.attr('data-subdashboard-name') || 'subdashboard-name';
  var date = new Date().toJSON().slice(0, 10);
  var subdashboardFileName = 'dashboard-[org-name]-[subdashboard-name]-[date]'.replace('[org-name]', orgName).replace('[subdashboard-name]', subdashboardName).replace('[date]', date);

  snapshotDashboardMenu.on('click', function(event) {
    var target = event.target;
    var dataAttribute = target.getAttribute('data-download-as');
    var renderedCanvas;

    // Scroll the window to top, in order to capture the entire screen
    window.scrollTo(0, 0);

    _hideElementsBeforeDownload();

    html2canvas($('body')[0]).then(function(canvas) {
      var image = canvas.toDataURL('image/png');
      var doc;
      var link;

      if (dataAttribute === 'pdf') {
        doc = new jsPDF('portrait', 'mm', [document.body.offsetWidth / 3.85, document.body.offsetHeight * 0.9]);
        doc.addImage(canvas, 'PNG', 0, 0, 0, 0);
        doc.save(subdashboardFileName + '.pdf');
      } else if (dataAttribute === 'image') {
        link = document.createElement('a');
        link.download = subdashboardFileName;
        link.href = image;
        link.click();
      }

      _showElementsAfterDownload();
    });
  });

  var heroMap = $('.hero-map-wrap');
  var newData = $('.new-data');
  var allData = $('.all-data');
  var goDownArrows = $('.go-down-arrow');
  var downloadAsBtn = $('#download-as-pdf');
  var mediaSection = $('[data-section="media"]');
  var downloadGraphBtns = $('.download-graph-btn');
  var shareGraphFb = $('.share-graph-fb-btn');
  var shareGraphTwitter = $('.share-graph-twitter-btn');

  function _hideElementsBeforeDownload() {
    snapshotDashboardMenu.parent().toggleClass('open');
    heroMap.hide();
    newData.hide();
    allData.hide();
    goDownArrows.hide();
    downloadAsBtn.hide();
    downloadGraphBtns.hide();
    shareGraphFb.hide();
    shareGraphTwitter.hide();

    mediaSection.css('margin-bottom', '70px');
  }

  function _showElementsAfterDownload() {
    heroMap.show();
    newData.show();
    allData.show();
    goDownArrows.show();
    downloadAsBtn.show();
    downloadGraphBtns.show();
    shareGraphFb.show();
    shareGraphTwitter.show();

    mediaSection.css('margin-bottom', 'initial');
  }

  var mediaContainer = $('div[data-section="media"]');

  mediaContainer.on('click', function onMediaContainerClick(event) {
    var target = $(event.target);
    var graphTitle = target.siblings('.graph-title').text();
    var graphFileName = 'USEDATA-[graph-name]-[date]'.replace('[graph-name]', graphTitle).replace('[date]', date);
    var svg;

    if (target.hasClass('download-graph-btn')) {
      svg = target.parent('.graph-container').find('svg')[0];

      convertSVGGraphToImage(svg, graphTitle, function(imageData) {
        var link = document.createElement('a');

        link.download = graphFileName;
        link.href = imageData;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    }
  });

})();

function toggleResources(resourceId) {
  $('#' + resourceId).toggleClass('hidden');
}

function convertSVGGraphToImage(svg, graphTitle, callback) {
  var width = 0;
  var fontSize = 15;
  var lines = [];
  var i, j, result, canvasWidth, canvasHeight, img;
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var svgData = new XMLSerializer().serializeToString(svg);
  var canvasWidth = Number(svg.getAttribute('width')) + 50;
  var canvasHeight = Number(svg.getAttribute('height')) + 100;

  canvas.style.backgroundColor = 'white';
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;

  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  ctx.fillStyle = '#000';
  ctx.font = fontSize + 'px Arial';

  // Split the graph's title into multiple lines if it's wider than the canvas's width
  while (graphTitle.length) {
    for (i = graphTitle.length; ctx.measureText(graphTitle.substr(0, i)).width > (canvasWidth - 20); i--);

    result = graphTitle.substr(0,i);

    if (i !== graphTitle.length) {
      for (j = 0; result.indexOf(' ', j) !== -1; j = result.indexOf(' ', j) + 1);
    }

    lines.push(result.substr(0, j || result.length));
    width = Math.max(width, ctx.measureText(lines[lines.length - 1]).width);
    graphTitle = graphTitle.substr(lines[lines.length - 1].length, graphTitle.length);
  }

  for (i = 0, j = lines.length; i < j; ++i) {
    ctx.fillText(lines[i], 20, 10 + fontSize + (fontSize + 5) * i);
  }

  img = document.createElement('img');
  img.setAttribute('src', 'data:image/svg+xml;base64,' + btoa(svgData));

  img.onload = function() {
    ctx.drawImage( img, 0, 70 );

    callback(canvas.toDataURL('image/png'));
  };
}
