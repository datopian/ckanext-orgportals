(function () {
  'use strict';

  var mediaContainer = $('div[data-section="media"]');
  var caption = window.location.href;

  mediaContainer.on('click', function onMediaContainerClick(event) {
    var target = $(event.target);

    if (target.hasClass('share-graph-fb-btn')) {
      FB.login(function(response) {

        if (response.authResponse) {
          var accessToken =   FB.getAuthResponse()['accessToken'];
          var userID =   FB.getAuthResponse()['userID'];

          var graphTitle = target.siblings('.graph-title').text();
          var svg;

          svg = target.parent('.graph-container').find('svg')[0];

          convertSVGGraphToImage(svg, graphTitle, function(imageData) {

            fbUpload(accessToken, userID, imageData, caption);

          });

        } else {
          console.log('User cancelled login or did not fully authorize.');
        }
      }, {scope: 'publish_actions'});
    }
  });

})($);


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

    callback(canvas.toDataURL('image/png', 1.0));
  };
};

function fbUpload(accessToken, userID, imageData, caption){
  var dataURL = imageData;
  var blob = dataURItoBlob(dataURL);
  var formData = new FormData();
  formData.append('token', accessToken);
  formData.append('source', blob);
  formData.append('caption', caption);

  var xhr = new XMLHttpRequest();
  xhr.open( 'POST', 'https://graph.facebook.com/'+ userID +'/photos?access_token=' + accessToken, true );
  xhr.onload = xhr.onerror = function() {
    console.log( xhr.responseText )
  };
  xhr.send( formData );
}

function dataURItoBlob(dataURI) {
  var byteString = atob(dataURI.split(',')[1]);
  var ab = new ArrayBuffer(byteString.length);
  var ia = new Uint8Array(ab);
  for (var i = 0; i < byteString.length; i++) { ia[i] = byteString.charCodeAt(i); }
  return new Blob([ab], { type: 'image/png' });
}
