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

  var url = window.location.pathname.split('/');
  var name;
  if (url[url.length - 1] === 'subdashboards_edit') {
    name = url[url.length - 2];
  } else {
    name = url[url.length - 3];
  }

  function populateDatasets(name){

    // Fetch and populate datasets dropdowns for existing chart items
    api.get('orgportals_show_datasets', {id: name}).done(function (data) {
      var inputs = $('[id*=chart_dataset_]');
      $.each(data.result, function (idx, elem) {
        inputs.append(new Option(elem.title, elem.name));
      });

      // Dataset event handlers
      var dataset_name;
      inputs.on('change', function () {
        var elem = $(this);
        dataset_name = elem.find(":selected").val();
        var dataset_select_id = elem.attr('id');
        var resource_select_id = dataset_select_id.replace('dataset', 'resource');
        var resourceview_select_id = resource_select_id.replace('resource', 'resourceview');

        // Empty all child selects
        if ($('#' + resource_select_id + ' option').length > 0)
          $('#' + resource_select_id).find('option').not(':first').remove();

        $('#' + resourceview_select_id + '_preview').empty();

        // Fetch and populate resources drop down
        api.get('orgportals_dataset_show_resources', {id: dataset_name}).done(
          function (data) {

            var opts = $('#' + resource_select_id);
            $.each(data.result, function (idx, elem) {
              opts.append(new Option(elem.name, elem.id));
            });

            $('.' + resource_select_id).removeClass('hidden');
          });
      });

      // Resource event handlers
      var resource_id;
      var resource_inputs = $('[id*=chart_resource_]');
      resource_inputs.on('change', function () {

        var elem = $(this);
        resource_id = elem.find(":selected").val();
        var resource_select_id = elem.attr('id');
        var resourceview_select_id = resource_select_id.replace('resource', 'resourceview');

        if ($('#' + resourceview_select_id + ' option').length > 0)
          $('#' + resourceview_select_id).find('option').not(':first').remove();

        $('#' + resourceview_select_id + '_preview').html();

        api.get('orgportals_resource_show_resource_views', {id: resource_id, view_type: 'Chart builder'}).done(
          function (data) {

            var opts = $('#' + resourceview_select_id);
            $.each(data.result, function (idx, elem) {
              opts.append(new Option(elem.title, elem.id));
            });

            $('.' + resourceview_select_id).removeClass('hidden');
          });
      });

      // Resource views event handlers
      var resourceview_inputs = $('[id*=chart_resourceview_]');
      resourceview_inputs.on('change', function () {

        var elem = $(this);
        var resourceview_id = elem.find(":selected").val();

        var resourceview_select_id = elem.attr('id');
        var chart_nr = resourceview_select_id.substr(resourceview_select_id.lastIndexOf('_') + 1);

        $('#save_chart_resourceview_' + chart_nr).val(resourceview_id)

        var base_url = ckan.sandbox().client.endpoint;
        var src = base_url + '/dataset/' + dataset_name + '/resource/' + resource_id + '/view/' + resourceview_id;

        ckan.sandbox().client.getTemplate('iframe.html', {source: src})
          .done(function (data) {

            $('#' + resourceview_select_id + '_preview').html();
            $('#' + resourceview_select_id + '_preview').html(data);
          });
      });

      // Charts subheaders event handlers
      var chart_subheader_inputs = $('[id*=chart_subheader_]');
      chart_subheader_inputs.on('keyup', function () {

        var elem = $(this);
        var chart_subheader = elem.val();

        var chart_subheader_id = elem.attr('id');
        var chart_nr = chart_subheader_id.substr(chart_subheader_id.lastIndexOf('_') + 1);

        $('#save_chart_subheader_' + chart_nr).val(chart_subheader);

      });

      // Charts size event handlers
      var chart_size_inputs = $('[id*=media_size_]');
      chart_size_inputs.on('change', function () {

        var elem = $(this);
        var chart_size = elem.find(":selected").val();

        var chart_size_id = elem.attr('id');
        var chart_nr = chart_size_id.substr(chart_size_id.lastIndexOf('_') + 1);

        $('#save_media_size_' + chart_nr).val(chart_size);

      });

    });
  };

  function handleItemsOrder() {

  };

  $(document).ready(function () {

    populateDatasets(name);
    var createMediaItemBtn = $('#create-media-item-btn');
    var removeMediaItemBtn = $('.remove-media-item-btn');

    // Remove item event handler for existing items
    removeMediaItemBtn.on('click', function (e) {
      $(e.target).parent().remove();
    });

      // Add new media item and Fetch and populate datasets dropdowns for the new item
    createMediaItemBtn.on('click', function() {

      var mediaItems = $('.orgportal-media-item');
      var totalItems = mediaItems.length + 1;

      $.proxyAll(this, /_on/);

      var mediaType;

      mediaType = $('#item_type').val();

      if (mediaType === 'chart') {

        ckan.sandbox().client.getTemplate('ajax_charts_list.html', {n: totalItems, media_type: mediaType})
           .done(function (data) {

             $('#content-settings-items').append(data);

             // Remove item event handler
             var removeMediaItemBtn = $('.remove-media-item-btn');
             removeMediaItemBtn.on('click', function (e) {
               $(e.target).parent().remove();
             });

             // Fetch and populate datasets dropdowns
             api.get('orgportals_show_datasets', {id: name}).done(function (data) {
               var inputs = $('[id=chart_dataset_'+ totalItems +']');
               $.each(data.result, function (idx, elem) {
                 inputs.append(new Option(elem.title, elem.name));
               });

               // Dataset event handlers
               var dataset_name;
               inputs.on('change', function () {
                 var elem = $(this);
                 dataset_name = elem.find(":selected").val();
                 var dataset_select_id = elem.attr('id');
                 var resource_select_id = dataset_select_id.replace('dataset', 'resource');
                 var resourceview_select_id = resource_select_id.replace('resource', 'resource_view');

                 // Empty all child selects
                 if ($('#' + resource_select_id + ' option').length > 0)
                   $('#' + resource_select_id).find('option').not(':first').remove();

                 $('#' + resourceview_select_id + '_preview').empty();

                 // Fetch and populate resources drop down
                 api.get('orgportals_dataset_show_resources', {id: dataset_name}).done(
                   function (data) {

                     var opts = $('#' + resource_select_id);
                     $.each(data.result, function (idx, elem) {
                       opts.append(new Option(elem.name, elem.id));
                     });

                     $('.' + resource_select_id).removeClass('hidden');
                   });
               });

               // Resource event handlers
               var resource_id;
               var resource_inputs = $('[id=chart_resource_'+ totalItems +']');
               resource_inputs.on('change', function () {

                 var elem = $(this);
                 resource_id = elem.find(":selected").val();
                 var resource_select_id = elem.attr('id');
                 var resourceview_select_id = resource_select_id.replace('resource', 'resourceview');

                 if ($('#' + resourceview_select_id + ' option').length > 0)
                   $('#' + resourceview_select_id).find('option').not(':first').remove();

                 $('#' + resourceview_select_id + '_preview').html();

                 api.get('orgportals_resource_show_resource_views', {id: resource_id, view_type: 'Chart builder'}).done(
                   function (data) {

                     var opts = $('#' + resourceview_select_id);
                     $.each(data.result, function (idx, elem) {
                       opts.append(new Option(elem.title, elem.id));
                     });

                     $('.' + resourceview_select_id).removeClass('hidden');
                   });
               });

               // Resource views event handlers
               var resourceview_inputs = $('[id=chart_resourceview_'+ totalItems +']');
               resourceview_inputs.on('change', function () {

                 var elem = $(this);
                 var resourceview_id = elem.find(":selected").val();

                 var resourceview_select_id = elem.attr('id');

                 var base_url = ckan.sandbox().client.endpoint;
                 var src = base_url + '/dataset/' + dataset_name + '/resource/' + resource_id + '/view/' + resourceview_id;

                 ckan.sandbox().client.getTemplate('iframe.html', {source: src})
                   .done(function (data) {

                     $('#' + resourceview_select_id + '_preview').html();
                     $('#' + resourceview_select_id + '_preview').html(data);
                   });
               });

             });

           });
      }

  });

  });
})($);