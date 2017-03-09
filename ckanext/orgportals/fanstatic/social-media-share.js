(function() {
    'use strict';

    var api = {
        get: function(action, params, api_ver = 3) {
            var base_url = ckan.sandbox().client.endpoint;
            params = $.param(params);
            var url = base_url + '/api/' + api_ver + '/action/' + action + '?' + params;
            return $.getJSON(url);
        },
        post: function(action, data, api_ver = 3) {
            var base_url = ckan.sandbox().client.endpoint;
            var url = base_url + '/api/' + api_ver + '/action/' + action;
            return $.post(url, JSON.stringify(data), "json");
        }
    };

    var caption = window.location.href;
    var twitterConsumerKey = window.twitterConsumerKey;
    var twitterConsumerSecret = window.twitterConsumerSecret;
    var twitterUserToken = localStorage.twitter_user_oauth_token;
    var twitterUserTokenSecret = localStorage.twitter_user_oauth_token_secret;
    var twitterOAuthToken = localStorage.twitter_oauth_token;
    var twitterOAuthTokenSecret = localStorage.twitter_oauth_token_secret;
    var cb, urlLocationSearch;

    if (twitterConsumerKey && twitterConsumerSecret) {
        cb = new Codebird;
        cb.setConsumerKey(twitterConsumerKey, twitterConsumerSecret);

        urlLocationSearch = location.search;

        // Request access token after the app is authorized
        if (urlLocationSearch.indexOf('oauth_token') > -1 &&
            urlLocationSearch.indexOf('oauth_verifier') > -1 &&
            !twitterUserToken &&
            !twitterUserTokenSecret) {
            _twitterGetAccessToken();
        }

        // If the authorization is denied then delete the oauth tokens
        if (urlLocationSearch !== '') {
            var hasDeniedQuery = urlLocationSearch.substr(1).indexOf('denied') > -1;

            if (hasDeniedQuery) {
                localStorage.removeItem('oauth_token');
                localStorage.removeItem('oauth_token_secret');
            }
        }

        if (twitterOAuthToken && twitterOAuthTokenSecret) {
            cb.setToken(twitterOAuthToken, twitterOAuthTokenSecret);
        }
    }

    $('.content-container').on('click', '.fb-url', function(e) {
        e.preventDefault();
        var target = $(event.target);
        var container = target.parents('.content-container');
        FB.login(function(response) {
            if (response.authResponse) {
                var accessToken = FB.getAuthResponse()['accessToken'];
                var userID = FB.getAuthResponse()['userID'];

                var linkTitle = container.find('h3').text();
                var url = container.find('.fb-url').attr('data-fb-url');
                fbShareLink(accessToken, userID, linkTitle, url);
            }
        },{
            scope: 'publish_actions'
        });
    });

    $('.content_container').on('click', '.share-video-fb-btn', function(e) {
        e.preventDefault();
        var target = $(event.target);
        var container = target.parents('.content-container');
        FB.login(function(response) {
            if (response.authResponse) {
                var accessToken = FB.getAuthResponse()['accessToken'];
                var userID = FB.getAuthResponse()['userID'];

                var linkTitle = container.find('h3').text();
                var url = container.find('.fb-url').attr('data-fb-url');
                fbShareLink(accessToken, userID, linkTitle, url);
            }
        },{
            scope: 'publish_actions'
        });
    });

    $('.content-container').on('click', '.twitter-url', function(e) {
        var target = $(event.target);
        var container = target.parents('.content-container');
        var message, className, duration;
        e.preventDefault();

        if (cb) {
            if (!localStorage.twitter_oauth_token) {
                message = 'Authenticating...';
                className = 'alert-info';
                duration = 1500;

                _showAlert(message, className, duration);

                var requestParams = {
                    oauth_callback: location.href
                };

                cb.__call('oauth_requestToken', requestParams, function(reply, rate) {
                        if (reply.httpstatus === 200) {
                            cb.setToken(reply.oauth_token, reply.oauth_token_secret);

                            // Store the tokens in localStorage for later use
                            localStorage.twitter_oauth_token = reply.oauth_token;
                            localStorage.twitter_oauth_token_secret = reply.oauth_token_secret;

                            // Authorize the application to access user's data
                            cb.__call('oauth_authorize', {}, function(auth_url) {
                                window.open(auth_url);
                            });
                        } else {
                            message = 'An error occured.';
                            className = 'alert-danger';
                            duration = 3000;

                            _showAlert(message, className, duration);
                        }
                    });
            } else if (!localStorage.twitter_user_oauth_token) {

                // Authorize the application to access user's data
                cb.__call('oauth_authorize', {}, function(auth_url) {
                    window.open(auth_url);
                });
            } else {
                message = 'Sharing on Twitter...';
                className = 'alert-info';
                duration = 1500;

                _showAlert(message, className, duration);

                var url_type = container.find('.twitter-url').attr('data-url-type');

                _shareLinkOnTwitter(container, url_type);
            }
        }
    });

    $('.graph-container').on('click', function onMediaContainerClick(event) {
        var target = $(event.target);
        var resourceViewId, message, className, duration, requestParams;

        if (target.hasClass('share-graph-fb-btn')) {
            FB.login(function(response) {
                if (response.authResponse) {
                    var accessToken = FB.getAuthResponse()['accessToken'];
                    var userID = FB.getAuthResponse()['userID'];

                    var graphTitle = target.siblings('.graph-title').text();
                    var svg;

                    svg = target.parent('.graph-container').find('svg')[0];

                    convertSVGGraphToImage(svg, graphTitle, function(imageData) {
                        fbUpload(accessToken, userID, imageData, caption);
                    });
                } else {
                    console.log('User cancelled login or did not fully authorize.');
                }
            }, {
                scope: 'publish_actions'
            });
        } else if (target.hasClass('share-graph-twitter-btn')) {

            if (cb) { // Check of existence for a Codebird instance

                if (!localStorage.twitter_oauth_token) { // Request a token
                    resourceViewId = target.siblings('.graph-container-resource-view').attr('data-id');

                    message = 'Authenticating...';
                    className = 'alert-info';
                    duration = 1500;

                    _showAlert(message, className, duration);

                    requestParams = {
                        oauth_callback: location.href + '?resource_view_id=' + resourceViewId
                    };

                    cb.__call('oauth_requestToken', requestParams, function(reply, rate) {
                        if (reply.httpstatus === 200) {
                            cb.setToken(reply.oauth_token, reply.oauth_token_secret);

                            // Store the tokens in localStorage for later use
                            localStorage.twitter_oauth_token = reply.oauth_token;
                            localStorage.twitter_oauth_token_secret = reply.oauth_token_secret;

                            // Authorize the application to access user's data
                            cb.__call('oauth_authorize', {}, function(auth_url) {
                                window.open(auth_url);
                            });
                        } else {
                            message = 'An error occured.';
                            className = 'alert-danger';
                            duration = 3000;

                            _showAlert(message, className, duration);
                        }
                    });
                } else if (!localStorage.twitter_user_oauth_token) {

                    // Authorize the application to access user's data
                    cb.__call('oauth_authorize', {}, function(auth_url) {
                        window.open(auth_url);
                    });
                } else {
                    message = 'Sharing on Twitter...';
                    className = 'alert-info';
                    duration = 1500;

                    _showAlert(message, className, duration);

                    _shareGraphOnTwitter(target);
                }
            }
        }
    });

    function _shareGraphOnTwitter(target) {
        var graphTitle, svg;

        twitterUserToken = localStorage.twitter_user_oauth_token;
        twitterUserTokenSecret = localStorage.twitter_user_oauth_token_secret;

        if (twitterUserToken && twitterUserTokenSecret) {
            graphTitle = target.siblings('.graph-title').text();
            svg = target.parent('.graph-container').find('svg')[0];

            convertSVGGraphToImage(svg, graphTitle, function(imageData) {
                imageData = imageData.substr(22);
                imageData = encodeURIComponent(imageData);

                var params = {
                    oauth_token: twitterUserToken,
                    oauth_token_secret: twitterUserTokenSecret,
                    image: imageData,
                    graph_title: graphTitle,
                    subdashboard_url: location.origin + location.pathname
                };
                var message, className, duration;

                api.post('orgportals_share_graph_on_twitter', params)
                    .done(function(data) {
                        if (data.success && data.result.share_status_success) {
                            message = 'The graph is successfully shared on Twitter!';
                            className = 'alert-success';
                            duration = 3000;

                            _showAlert(message, className, duration);
                        } else {
                            message = 'Error while sharing the graph on Twitter.';
                            className = 'alert-danger';
                            duration = 3000;

                            _showAlert(message, className, duration);
                        }
                    })
                    .error(function(error) {
                        message = 'Error while sharing the graph on Twitter.';
                        className = 'alert-danger';
                        duration = 3000;

                        _showAlert(message, className, duration);
                    });
            });
        }
    }

    function _shareLinkOnTwitter(container, url_type) {
        var message, className, duration;
        var title, url;

        twitterUserToken = localStorage.twitter_user_oauth_token;
        twitterUserTokenSecret = localStorage.twitter_user_oauth_token_secret;

        if (twitterUserToken && twitterUserTokenSecret) {
            console.log(container);
            url = container.find('.twitter-url').attr('data-twitter-url');
            title = container.find('h3').text();

            var params = {
                oauth_token: twitterUserToken,
                oauth_token_secret: twitterUserTokenSecret,
                url: url,
                title: title,
                subdashboard_url: location.origin + location.pathname,
                url_type: url_type
            };

            api.post('orgportals_share_link_on_twitter', params)
                .done(function(data) {
                    if (data.success && data.result.share_status_success) {
                        message = 'The ' + url_type + ' is successfully shared on Twitter!';
                        className = 'alert-success';
                        duration = 3000;

                        _showAlert(message, className, duration);
                    } else {
                        message = 'Error while sharing the ' + url_type + ' on Twitter.';
                        className = 'alert-danger';
                        duration = 3000;

                        _showAlert(message, className, duration);
                    }
                })
                .error(function(error) {
                    message = 'Error while sharing the ' + url_type + 'on Twitter.';
                    className = 'alert-danger';
                    duration = 3000;

                    _showAlert(message, className, duration);
                });
        }

    }

    function _twitterGetAccessToken() {
        var current_url = location.toString();
        var query = current_url.match(/\?(.+)$/)[1].split('&');
        var parameters = {};
        var parameter;
        var requestParams;

        for (var i = 0; i < query.length; i++) {
            parameter = query[i].split('=');

            if (parameter.length === 1) {
                parameter[1] = '';
            }

            parameters[decodeURIComponent(parameter[0])] = decodeURIComponent(parameter[1]);
        }

        if (typeof parameters.oauth_verifier !== 'undefined') {
            cb.setToken(localStorage.twitter_oauth_token, localStorage.twitter_oauth_token_secret);

            requestParams = {
                oauth_verifier: parameters.oauth_verifier
            };

            cb.__call('oauth_accessToken', requestParams, function(reply, rate) {
                var resourceViewId, target, message, className, duration;

                if (reply.httpstatus === 200) {

                    // Store the tokens in localStorage for later use
                    localStorage.twitter_user_oauth_token = reply.oauth_token;
                    localStorage.twitter_user_oauth_token_secret = reply.oauth_token_secret;

                    resourceViewId = parameters.resource_view_id;

                    target = $('div[data-id=' + resourceViewId + ']');

                    message = 'Sharing on Twitter...';
                    className = 'alert-info';
                    duration = 1500;

                    _showAlert(message, className, duration);

                    _shareGraphOnTwitter(target);
                } else {
                    message = 'An error occured.';
                    className = 'alert-danger';
                    duration = 3000;

                    _showAlert(message, className, duration);
                }
            });
        }
    }

})($);

function _showAlert(message, className, duration) {
    var socialMediaShareAlert = $('.social-media-share-alert');

    socialMediaShareAlert.find('.alert-text').text(message);
    socialMediaShareAlert.addClass(className);
    socialMediaShareAlert.show();

    setTimeout(function() {
        socialMediaShareAlert.hide();
        socialMediaShareAlert.removeClass(className);
    }, duration);
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

        result = graphTitle.substr(0, i);

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
        ctx.drawImage(img, 0, 70);

        callback(canvas.toDataURL('image/png', 1.0));
    };
};

function fbUpload(accessToken, userID, imageData, caption) {
    var dataURL = imageData;
    var blob = dataURItoBlob(dataURL);
    var formData = new FormData();

    formData.append('token', accessToken);
    formData.append('source', blob);
    formData.append('caption', caption);

    var xhr = new XMLHttpRequest();

    xhr.open('POST', 'https://graph.facebook.com/' + userID + '/photos?access_token=' + accessToken, true);

    xhr.onreadystatechange = function(data) {
        if (xhr.readyState == 4 && xhr.status == 200) {
            message = 'The graph is successfully shared on Facebook!';
            className = 'alert-success';
            duration = 3000;

            _showAlert(message, className, duration);
        } else {

            message = 'An error occured.';
            className = 'alert-danger';
            duration = 3000;

            _showAlert(message, className, duration);
        }
    };

    xhr.onerror = function(error) {
        message = 'An error occured.';
        className = 'alert-danger';
        duration = 3000;

        _showAlert(message, className, duration);
    };

    xhr.send(formData);
}

function dataURItoBlob(dataURI) {
    var byteString = atob(dataURI.split(',')[1]);
    var ab = new ArrayBuffer(byteString.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {
        type: 'image/png'
    });
}

function fbShareLink(accessToken, userID, linkTitle, url) {
    FB.api(
        '/me/feed',
        'POST',
        {
            'message': linkTitle + ' ' + window.location.href,
            'link': url
        }, function(response){
            if (response && !response.error) {
                _showAlert('Successfully shared on Facebook!', 'alert-success', 3000);
            } else {
                console.log(response.error);
                _showAlert('Error sharing on Facebook!', 'alert-danger', 3000);
            }
    });
}
