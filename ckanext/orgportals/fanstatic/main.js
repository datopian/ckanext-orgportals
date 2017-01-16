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

  var api = {
    get: function (action, params, api_ver=3) {
      var base_url = ckan.sandbox().client.endpoint;
      params = $.param(params);
      var url = base_url + '/api/' + api_ver + '/action/' + action + '?' + params;
      return $.getJSON(url);
    },
    post: function (action, data, api_ver=3) {
      var base_url = ckan.sandbox().client.endpoint;
      var url = base_url + '/api/' + api_ver + '/action/' + action;
      return $.post(url, JSON.stringify(data), "json");
    }
  };

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

  var downloadAsPdfBtn = $('#download-as-pdf');
  var subdashboardMeta = $('#subdashboard-meta');
  var orgName = subdashboardMeta.attr('data-org-name') || 'org-name';
  var subdashboardName = subdashboardMeta.attr('data-subdashboard-name') || 'subdashboard-name';
  var date = new Date().toJSON().slice(0, 10);
  var subdashboardFileName = 'dashboard-[org-name]-[subdashboard-name]-[date]'.replace('[org-name]', orgName).replace('[subdashboard-name]', subdashboardName).replace('[date]', date);

  downloadAsPdfBtn.on('click', function(event) {
    var data = {
      url: window.location.href + '?download_dashboard=true'
    };
    var socialMediaShareAlert = $('.social-media-share-alert');

    socialMediaShareAlert.find('.alert-text').text('Creating snapshot...');
    socialMediaShareAlert.addClass('alert-info');
    socialMediaShareAlert.show();

    api.get('orgportals_download_dashboard', data)
      .done(function(data) {
        var imageData = data.result.image_data;
        var link;

        if (imageData) {
          socialMediaShareAlert.hide();
          link = document.createElement('a');
          link.download = subdashboardFileName;
          link.href = 'data:image/png;base64,' + imageData;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        } else {
          console.log('data ', data);

          socialMediaShareAlert.removeClass('alert-info');
          socialMediaShareAlert.addClass('alert-danger');
          socialMediaShareAlert.find('.alert-text').text('Error while creating snapshot...');

          setTimeout(function() {
            socialMediaShareAlert.hide();
            socialMediaShareAlert.removeClass('alert-danger');
          }, 2000);
        }
      })
      .error(function(error) {
        console.log('error ', error);
        socialMediaShareAlert.removeClass('alert-info');
        socialMediaShareAlert.addClass('alert-danger');
        socialMediaShareAlert.find('.alert-text').text('Error while creating snapshot...');

        setTimeout(function() {
          socialMediaShareAlert.hide();
          socialMediaShareAlert.removeClass('alert-danger');
        }, 2000);
      });
  });

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

  _focusSearchData();

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

function _focusSearchData() {
  var current_url = location.toString();
  var parameters = {};
  var parameter;
  var query;

  try {
    query = current_url.match(/\?(.+)$/)[1].split('&');
    parameters = {};
    parameter;

    for (var i = 0; i < query.length; i++) {
      parameter = query[i].split('=');

      if (parameter.length === 1) {
          parameter[1] = '';
      }

      parameters[decodeURIComponent(parameter[0])] = decodeURIComponent(parameter[1]);
    }

    if (parameters.q && parameters.q.indexOf('#search-data') === -1) {
      window.location.href = window.location.href + '#search-data';
    }
  } catch(error) {

  }
}
