(function () {
  'use strict';

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

  $(document).ready(function () {
    // Map select event handler

    function changeMainPropertyValues(element) {
      var map_main_property = $(element).parent().parent().parent()
        .find($('select[id="map_main_property"]'));

      element.attr('name', 'map_' + numResources);
      map_main_property.attr('name', 'map_main_property_' + numResources);

      if ($(element).find('option').length > 0)
        map_main_property.empty();

      // Get resource id
      var resource_id = $(element).find('option:selected').val();
      var params = {id: resource_id};
      api.get('orgportals_resource_show_map_properties', params)
        .done(function (data) {
          var opts = map_main_property;
          opts.append(new Option('None', ''));
          $.each(data.result, function (idx, elem) {
            opts.append(new Option(elem.value, elem.value));
          });
          map_main_property.removeClass('hidden');
        });
    }

    $('.map-properties').on('change', 'select', function (event) {
        if ($(event.target).attr('id') == 'map') {
          changeMainPropertyValues($(event.target));
        }
    });

    //Base color change event handler
    var secondary_element = $('#orgdashboards_dashboard_secondary_color'),
        lighter_color;
    $('#orgdashboards_base_color').change(function () {
      lighter_color = ColorLuminance('#' + this.value, 0.4);
      secondary_element.val(lighter_color.substr(1));
      secondary_element.css({'background-color': lighter_color});
    });

    var numResources = $('.map-fields').length;

    $('#new-field-btn').on('click', function () {
      var resourceField = $('#map-field_1').clone();
      numResources++;
      resourceField.attr('id', 'map-field_' + numResources);
      resourceField.appendTo($('.map-properties'));
      changeMainPropertyValues(resourceField.find($('select[id="map"]')));
    });

    $('.map-properties').on('click', 'a', function (e) {
      $(e.target).parent().remove();
    });

    function ColorLuminance(hex, lum) {

      // validate hex string
      hex = String(hex).replace(/[^0-9a-f]/gi, '');
      if (hex.length < 6) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
      }
      lum = lum || 0;

      // convert to decimal and change luminosity
      var rgb = "#", c, i;
      for (i = 0; i < 3; i++) {
        c = parseInt(hex.substr(i * 2, 2), 16);
        c = Math.round(Math.min(Math.max(0, c + (c * lum)), 255)).toString(16);
        rgb += ("00" + c).substr(c.length);
      }

      return rgb;
    }

  });
})($);
