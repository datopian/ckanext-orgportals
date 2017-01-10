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

  function handleChartItems(name, item_id){

    // Fetch and populate datasets dropdowns for existing chart items
    api.get('orgportals_show_datasets', {id: name}).done(function (data) {
      var inputs;
      if (item_id) {
        inputs = $('[id=chart_dataset_'+ item_id +']');
        inputs.prop('required', 'required');
      } else {
        inputs = $('[id*=chart_dataset_]');
      }

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

        $('#' + resource_select_id).prop('required', 'required');
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
      var resource_inputs;
      if (item_id) {
        resource_inputs = $('[id=chart_resource_'+ item_id +']');
      } else {
        resource_inputs = $('[id*=chart_resource_]');
      }
      resource_inputs.on('change', function () {

        var elem = $(this);
        resource_id = elem.find(":selected").val();
        var resource_select_id = elem.attr('id');
        var resourceview_select_id = resource_select_id.replace('resource', 'resourceview');

        if ($('#' + resourceview_select_id + ' option').length > 0)
          $('#' + resourceview_select_id).find('option').not(':first').remove();

        $('#' + resourceview_select_id).prop('required', 'required');
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
      var resourceview_inputs;
      if (item_id) {
        resourceview_inputs = $('[id=chart_resourceview_'+ item_id +']');
      } else {
        resourceview_inputs = $('[id*=chart_resourceview_]');
      }

      resourceview_inputs.on('change', function () {

        var elem = $(this);
        var resourceview_id = elem.find(":selected").val();

        var resourceview_select_id = elem.attr('id');
        var chart_nr = resourceview_select_id.substr(resourceview_select_id.lastIndexOf('_') + 1);

        $('#save_chart_resourceview_' + chart_nr).val(resourceview_id);

        var base_url = ckan.sandbox().client.endpoint;
        var src = base_url + '/dataset/' + dataset_name + '/resource/' + resource_id + '/view/' + resourceview_id;

        ckan.sandbox().client.getTemplate('iframe.html', {source: src})
          .done(function (data) {

            $('#' + resourceview_select_id + '_preview').html();
            $('#' + resourceview_select_id + '_preview').html(data);
          });
      });

      // Charts subheaders event handlers
      var chart_subheader_inputs;
      if (item_id) {
        chart_subheader_inputs = $('[id=chart_subheader_'+ item_id +']');
      } else {
        chart_subheader_inputs = $('[id*=chart_subheader_]');
      }

      chart_subheader_inputs.on('keyup', function () {

        var elem = $(this);
        var chart_subheader = elem.val();

        var chart_subheader_id = elem.attr('id');
        var chart_nr = chart_subheader_id.substr(chart_subheader_id.lastIndexOf('_') + 1);

        $('#save_chart_subheader_' + chart_nr).val(chart_subheader);

      });

      // Charts size event handlers
      var chart_size_inputs;
      if (item_id) {
        chart_size_inputs = $('[id=media_size_'+ item_id +']');
        chart_size_inputs.prop('required', 'required');
      } else {
        chart_size_inputs = $('[id*=media_size_]');
      }
      chart_size_inputs.on('change', function () {

        var elem = $(this);
        var chart_size = elem.find(":selected").val();

        var chart_size_id = elem.attr('id');
        var chart_nr = chart_size_id.substr(chart_size_id.lastIndexOf('_') + 1);

        $('#save_media_size_' + chart_nr).val(chart_size);

      });

    });
  };

  function handleVideoItems (item_id) {

    // Videos source event handlers
      var video_source_inputs;
      if (item_id) {
        video_source_inputs = $('[id=video_source_'+ item_id +']');
      } else {
        video_source_inputs = $('[id*=video_source_]');
      }

      video_source_inputs.on('change paste keyup', function () {

        var elem = $(this);
        var video_source = elem.val();
        var url = video_source.replace('watch?v=', 'embed/');

        var video_source_id = elem.attr('id');
        var video_nr = video_source_id.substr(video_source_id.lastIndexOf('_') + 1);

        $('#video_source_preview_' + video_nr).prop('src', url);
        $('#video_source_preview_' + video_nr).removeClass('hidden');
        $('#save_video_source_' + video_nr).val(url);

      });
  };

  function handleItemsOrder() {

    $('.change-chart-btn').hide();
    $('#create-media-item-section').hide();
    $('#media-section-info-msg').removeClass('hidden');
    var media_type_input;
    var media_size_input;
    var chart_resourceview_input;
    var chart_subheader_input;
    var save_video_source_input;
    var image_url_input;
    var image_upload_input;
    var image_title_input;

    var mediaItems = $('.orgportal-media-item');

    $.each(mediaItems, function(key, item) {

      var media_type = $(item).find('[id*=media_type_]').val();
      var media_order = key + 1;

      if (media_type === 'chart') {

        media_type_input =  $(item).find('[id*=media_type_]');
        media_size_input =  $(item).find('[id*=save_media_size_]');
        chart_resourceview_input =  $(item).find('[id*=save_chart_resourceview_]');
        chart_subheader_input =  $(item).find('[id*=save_chart_subheader_]');

        media_type_input.attr('id', 'media_type_' + media_order);
        media_type_input.attr('name', 'media_type_' + media_order);

        media_size_input.attr('id', 'save_media_size_' + media_order);
        media_size_input.attr('name', 'media_size_' + media_order);

        chart_resourceview_input.attr('id', 'save_chart_resourceview_' + media_order);
        chart_resourceview_input.attr('name', 'chart_resourceview_' + media_order);

        chart_subheader_input.attr('id', 'save_chart_subheader_' + media_order);
        chart_subheader_input.attr('name', 'chart_subheader_' + media_order);

      } else if (media_type === 'youtube_video') {

        media_type_input =  $(item).find('[id*=media_type_]');
        save_video_source_input =  $(item).find('[id*=save_video_source_]');


        media_type_input.attr('id', 'media_type_' + media_order);
        media_type_input.attr('name', 'media_type_' + media_order);

        save_video_source_input.attr('id', 'save_video_source_' + media_order);
        save_video_source_input.attr('name', 'video_source_' + media_order);
      } else if (media_type === 'image') {

        media_type_input =  $(item).find('[id*=media_type_]');
        image_url_input =  $(item).find('[name*=media_image_url_]');
        image_upload_input =  $(item).find('[name*=media_image_upload_]');
        image_title_input =  $(item).find('[name*=media_image_title_]');

        media_type_input.attr('id', 'media_type_' + media_order);
        media_type_input.attr('name', 'media_type_' + media_order);

        image_url_input.attr('name', 'media_image_url_' + media_order);
        image_upload_input.attr('name', 'media_image_upload_' + media_order);

        image_title_input.attr('id', 'media_image_title_' + media_order);
        image_title_input.attr('name', 'media_image_title_' + media_order);
      }

    });

  };

  function handleImageItems(item_id) {
    var contentContainer = $('#content-settings-items');
    var contentContainerChildren = contentContainer.children();
    var uploadsEnabled = contentContainer.attr('data-uploads-enabled');
    var item;
    var fieldImageUrl;
    var fieldImageUpload;
    var imageUploadModule;
    var mediaImage;
    var mediaUpload;
    var removeLinkBtn;
    var image_url_inputs;
    var remove_url_inputs;
    var image_upload_inputs;
    var image_title_inputs;

    if (item_id) {
      item = contentContainerChildren.last();
      mediaImage = item.find('#field-image-url');
      mediaUpload = item.find('#field-image-upload');

      fieldImageUrl = 'media_image_url_' + item_id;
      fieldImageUpload = 'media_image_upload_' + item_id;

      if (uploadsEnabled == 'True') {
        imageUploadModule = item.find('[data-module="custom-image-upload"]');
        imageUploadModule.attr('data-module', 'image-upload');
        imageUploadModule.attr('data-module-field_upload', fieldImageUpload);
        imageUploadModule.attr('data-module-field_url', fieldImageUrl);
        mediaUpload.attr('name', fieldImageUpload);
      }

      mediaImage.attr('name', fieldImageUrl);

      if (uploadsEnabled == 'True') {
        window.ckan.module.initializeElement(imageUploadModule[0]);
      }
    }

    if (item_id) {
      image_url_inputs = $('[name=media_image_url_'+ item_id +']');
      image_upload_inputs = $('[name=media_image_upload_'+ item_id +']');
      image_title_inputs = $('[name=media_image_title_'+ item_id +']');
    } else {
      image_url_inputs = $('[name*=media_image_url_]');
      image_upload_inputs = $('[name*=media_image_upload_]');
      image_title_inputs = $('[name*=media_image_title_]');
    }

    image_url_inputs.on('change keyup paste', function onMediaImageChange() {
      var elem = $(this);
      var image_url_id = elem.attr('name');
      var image_id = image_url_id.substr(image_url_id.lastIndexOf('_') + 1);
      var imageUrl = $('#image_url_' + image_id);

      imageUrl.val(elem.val());
    });

    image_upload_inputs.on('change', function onMediaImageChange() {
      var elem = $(this);
      var image_upload_id = elem.attr('name');
      var image_id = image_upload_id.substr(image_upload_id.lastIndexOf('_') + 1);
      var imageUpload = $('#image_upload_' + image_id);

      imageUpload.val(elem.val());
    });

    image_title_inputs.on('change keyup paste', function onMediaImageChange() {
      var elem = $(this);
      var image_title_id = elem.attr('name');
      var image_id = image_title_id.substr(image_title_id.lastIndexOf('_') + 1);
      var imageTitle = $('#image_title_' + image_id);

      imageTitle.val(elem.val());
    });

    setTimeout(function() {
      if (item_id) {
        remove_url_inputs = image_url_inputs.closest('.btn-remove-url');
      } else {
        remove_url_inputs = $('.btn-remove-url');
      }

      remove_url_inputs.on('click', function onMediaImageChange() {
        var elem = $(this);
        elem = elem.next();
        var image_url_id = elem.attr('name');
        var image_id = image_url_id.substr(image_url_id.lastIndexOf('_') + 1);
        var imageUrl = $('#image_url_' + image_id);

        imageUrl.val(elem.val());
      });
    }, 1000)


  }

  $(document).ready(function () {

    handleChartItems(name);
    handleVideoItems();
    handleImageItems();

    var createMediaItemBtn = $('#create-media-item-btn');
    var removeMediaItemBtn = $('.remove-media-item-btn');

    // Remove item event handler for existing items
    removeMediaItemBtn.on('click', function (e) {
      $(e.target).parent().remove();
      handleItemsOrder();
    });

      // Add new media item and Fetch and populate datasets dropdowns for the new item
    createMediaItemBtn.on('click', function() {

      var mediaItems = $('.orgportal-media-item');
      var totalItems = mediaItems.length + 1;

      $.proxyAll(this, /_on/);

      var mediaType;

      mediaType = $('#item_type').val();

      if (mediaType === 'chart') {

        ckan.sandbox().client.getTemplate('charts_list.html', {n: totalItems, media_type: 'chart'})
           .done(function (data) {

             $('#content-settings-items').append(data);

             // Remove item event handler
             var removeMediaItemBtn = $('.remove-media-item-btn');
             removeMediaItemBtn.on('click', function (e) {
               $(e.target).parent().remove();
//               handleItemsOrder(e);
             });

             handleChartItems(name, totalItems);

           });
      } else if (mediaType === 'image') {

        ckan.sandbox().client.getTemplate('images_list.html', {n: totalItems, media_type: 'image'})
           .done(function (data) {

             $('#content-settings-items').append(data);

             // Remove item event handler
             var removeMediaItemBtn = $('.remove-media-item-btn');
             removeMediaItemBtn.on('click', function (e) {
               $(e.target).parent().remove();
             });

             handleImageItems(totalItems);

           });

      } else if (mediaType === 'youtube_video') {

        ckan.sandbox().client.getTemplate('videos_list.html', {n: totalItems, media_type: 'youtube_video'})
           .done(function (data) {

             $('#content-settings-items').append(data);

             // Remove item event handler
             var removeMediaItemBtn = $('.remove-media-item-btn');
             removeMediaItemBtn.on('click', function (e) {
               $(e.target).parent().remove();
             });

             handleVideoItems(totalItems);

           });

      }

  });

  dragula([$('#content-settings-items')[0]], {
    moves: function(el, container, handle) {
      return handle.classList.contains('grippy');
    }
  })
   .on('drag', function(el, container, handle) {
     el.querySelector('.grippy').classList.add('cursor-grabbing');
   }).on('dragend', function(el) {
     el.querySelector('.grippy').classList.remove('cursor-grabbing');

     handleItemsOrder();
   });

  });
})($);
