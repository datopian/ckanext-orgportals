this.ckan = this.ckan || {};
this.ckan.orgportals = this.ckan.orgportals || {};
this.ckan.orgportals.dashboardmap = this.ckan.dashboardmap || {};

(function (self, $) {

  self.init = function init(elementId, organizationName, mapURL, color, mainProperty, map_selector_name, organization_entity_name) {
    renderMap(elementId, organizationName, mapURL, color, mainProperty, map_selector_name, organization_entity_name);
  };

  var disclaimerText = $('.hero-info .media-body');
  var disclaimerContainer = $('.media.hero-info');

  // Click handler for the disclaimer icon.
  $('.hero-info > .media-left').click(function onMapDisclaimerClick(event) {
    var bodyWidth = $('body').outerWidth();
    var topPosition;

    if (disclaimerText.hasClass('hidden')) {
      topPosition = bodyWidth <= 976 ? '790px' : '295px';

      disclaimerText.removeClass('hidden');
      disclaimerContainer.css({
          'width': '300px',
          'padding': '10px',
      });
    } else {
      topPosition = bodyWidth <= 976 ? '905px' : '410px';

      disclaimerText.addClass('hidden');
      disclaimerContainer.css({
          'width': '54px',
          'padding': '2px',
      });
    }
  });

  function renderMap(elementId, organizationName, mapURL, color, mainProperty, map_selector_name, organization_entity_name) {
    var mainProperties = [];
    var fitBounds = false;

    if (mapURL.length > 0 && typeof mainProperty === 'string') {
      var mapURLS = mapURL.split(',');

      mainProperties = mainProperty.split(',');
    }

    if (organization_entity_name === 'country') {
      $.getJSON('https://maps.googleapis.com/maps/api/geocode/json?address=' + encodeURI(organizationName)).done(function (data) {
         if (data['status'] == 'ZERO_RESULTS') {
           initLeaflet(elementId, 39, 40, 2);
         } else {
           var lat = data['results'][0]['geometry']['location']['lat'],
             lng = data['results'][0]['geometry']['location']['lng'];
           initLeaflet(elementId, lat, lng, 5);
         }
       }).fail(function (data) {
         console.log(data);
         initLeaflet(elementId, 39, 40, 2);
       });
    } else {
      fitBounds = true;
      initLeaflet(elementId, 39, 40, 2);
    }


    // geo layer
    var geoL;

    function initLeaflet(elementId, lat, lng, zoom) {
      var map;

      if (fitBounds) {
        if (!mapURLS && mainProperties.length === 0) {
          map = new L.Map(elementId, {scrollWheelZoom: false, inertiaMaxSpeed: 200}).setView([lat, lng], zoom);
        } else {
          map = new L.Map(elementId, {scrollWheelZoom: false, inertiaMaxSpeed: 200});
        }
      } else {
        map = new L.Map(elementId, {scrollWheelZoom: false, inertiaMaxSpeed: 200}).setView([lat, lng], zoom);
      }

      var osmUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
      var osmAttrib = 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
      var osm = new L.TileLayer(osmUrl, {
        minZoom: 2,
        maxZoom: 18,
        attribution: osmAttrib
      });

      map.addLayer(osm);

      if (mapURLS && mainProperties.length > 0) {

        // Initialize markers
        initDatasetMarkers(mapURLS[0], mainProperties[0]);
      }

      highlightCountry();

      function highlightCountry() {
        var countriesUrl = 'http://localhost:5000/countries.json';
        var country;

        $.getJSON(countriesUrl).done(function(data) {
          data.features.some(function(feature) {
            if (feature.properties.name === organizationName) {
              country = L.geoJson(feature);
              country.setStyle({fill: false})
              map.addLayer(country);
              map.fitBounds(country.getBounds());
              return true;
            }
          });
        });
      }

      function initDatasetMarkers(mapURL, mainField) {

        var layers = [];

        $.getJSON(mapURL).done(function (data) {
          geoL = L.geoJson(data, {
            style: function (feature) {
              var styles = {};
              var color = feature.properties.stroke;
              var fillColor = feature.properties.fill;

              if (color) {
                styles.color = color;
              }

              if (fillColor) {
                styles.fillColor = fillColor;
              }

              return styles;
            },
            pointToLayer: function (feature, latlng) {
              var markerColor = feature.properties['marker-color'] || '#c71111';
              markerColor = markerColor.substr(1);
              var icon = L.divIcon({
                html: '<img class="orgportals-marker-icon" src="https://a.tiles.mapbox.com/v4/marker/pin-m+' + markerColor + '.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6IlpIdEpjOHcifQ.Cldl4wq_T5KOgxhLvbjE-w" />'
              });

              return L.marker(latlng, {
                icon: icon
              });
            },
            onEachFeature: function (feature, layer) {
              var popup = document.createElement("div"),
                header = document.createElement("h5"),
                headerText = document.createTextNode(feature.properties[mainField]),
                list = document.createElement("ul"),
                listElement,
                listElementText,
                boldElement,
                boldElementText;
              header.appendChild(headerText);
              for (var info in feature.properties) {
                if (info != mainField) {
                  boldElementText = document.createTextNode(info + ': ');
                  boldElement = document.createElement("b");
                  boldElement.appendChild(boldElementText);

                  listElementText = document.createTextNode(feature.properties[info]);
                  listElement = document.createElement("li");
                  listElement.appendChild(boldElement);
                  listElement.appendChild(listElementText);

                  list.appendChild(listElement);
                }
              }
              popup.appendChild(header);
              popup.appendChild(list);
              layer.bindPopup(popup);
              layer.name = feature.properties[mainField];
              layers.push(layer);
            }
          }).addTo(map);

          map.on('popupopen', function (e) {
            if (map._zoom == 10) {
              var px = map.project(e.popup._latlng, 10);
              px.y -= e.popup._container.clientHeight / 2;
              map.flyTo(map.unproject(px), 10, {animate: true, duration: 1});
            } else {
              map.flyTo(e.popup._latlng, 10, {animate: true, duration: 1})
            }
            $('.leaflet-popup-content-wrapper').css({'border-top': '5px solid ' + color});
          });

          var select_dataset = $('#dataset');
          var select_resource = $('#orgportals_resource');
          select_dataset.append('<option>Select Data Point</option>');

          for (var elem in layers) {
            select_dataset.append('<option>' + layers[elem].name + '</option>');
          }


          select_dataset.change(
            function datasetsClick(a) {
              var selected = $('#dataset option:selected').text();
              for (var elem in layers) {
                if (layers[elem].name == selected) {
                  layers[elem].openPopup();
                }
              }
            }
          );

          $('#map-info').removeClass('hidden');

          // Properly zoom the map to fit all markers/polygons
          if (fitBounds) {
            map.fitBounds(geoL.getBounds().pad(0.5));
          }
        }).fail(function (data) {
          console.log("GeoJSON could not be loaded " + mapURL);
        });

      }


      $(document).ready(function () {
        $('.leaflet-control-zoom-in').css({'color': color});
        $('.leaflet-control-zoom-out').css({'color': color});

        var select_resource = $('#orgportals_resource');
        var select_dataset = $('#dataset');

        select_resource.change(function click() {
          var selectedIndex = $('#orgportals_resource').prop('selectedIndex');
          fitBounds = true;
          select_dataset.children('option').remove();
          layers = [];
          map.removeLayer(geoL);
          initDatasetMarkers(mapURLS[selectedIndex], mainProperties[selectedIndex]);
        });

      });
    }

  }
})(this.ckan.orgportals.dashboardmap, this.jQuery);
