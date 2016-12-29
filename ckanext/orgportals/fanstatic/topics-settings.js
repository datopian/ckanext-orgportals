(function topicsSettings() {

  var createItemBtn = $('#create-item-btn');
  var itemFields = $('.topics-settings-item-fields');
  var topicsProperties = $('.topics-properties');
  var uploadsEnabled = topicsProperties.attr('data-uploads-enabled');
  var topicItems;
  var totalItems;

  // Add a topic/dashboard
  createItemBtn.on('click', function onCreateDashboardBtnClick() {
    var newFields = itemFields.contents().clone();

    topicItems = $('.topics-settings-item-fields__item');
    totalItems = topicItems.length;

    newFields.each(function(i, item) {
      var item = $(item);
      var topicTitle;
      var topicSubdashboard;
      var topicEnabled;
      var fieldImageUrl;
      var fieldImageUpload;
      var imageUploadModule;

      if (item.hasClass('topics-settings-item-fields__item')) {
        topicTitle = item.find('#topic_title');
        topicSubdashboard = item.find('#topic_subdashboard');
        topicEnabled = item.find('#topic_enabled');
        topicOrder = item.find('#topic_order');
        topicImage = item.find('#field-image-url');
        topicUpload = item.find('#field-image-upload');

        topicTitle.attr('id', 'topic_title_' + totalItems);
        topicTitle.attr('name', 'topic_title_' + totalItems);
        topicTitle.attr('required', 'true');

        topicSubdashboard.attr('id', 'topic_subdashboard_' + totalItems);
        topicSubdashboard.attr('name', 'topic_subdashboard_' + totalItems);

        topicEnabled.attr('id', 'topic_enabled_' + totalItems);
        topicEnabled.attr('name', 'topic_enabled_' + totalItems);

        topicOrder.attr('id', 'topic_order_' + totalItems);
        topicOrder.attr('name', 'topic_order_' + totalItems);
        topicOrder.attr('value', totalItems);

        fieldImageUrl = 'topic_image_url_' + totalItems;
        fieldImageUpload = 'topic_image_upload_' + totalItems;

        if (uploadsEnabled == 'True') {
          imageUploadModule = item.find('[data-module="custom-image-upload"]');
          imageUploadModule.attr('data-module', 'image-upload');
          imageUploadModule.attr('data-module-field_upload', fieldImageUpload);
          imageUploadModule.attr('data-module-field_url', fieldImageUrl);
          topicUpload.attr('name', fieldImageUpload);
        }

        topicImage.attr('name', fieldImageUrl);

      }
    });

    topicsProperties.append(newFields);

    if (uploadsEnabled == 'True') {
      window.ckan.module.initializeElement(newFields.find('[data-module="image-upload"]')[0]);
    }

    // Limit the total number of topics to 6
    if (totalItems == 6) {
      createItemBtn.css('display', 'none');
    }
  });

  // Remove a topic/dashboard
  topicsProperties.on('click', '.topics-settings-item-fields__remove-btn', function (e) {
    $(e.target).parent().remove();

    _changeTopicOrder();

    topicItems = $('.topics-settings-item-fields__item');
    totalItems = topicItems.length;

    if (totalItems < 7) {
      createItemBtn.css('display', 'initial');
    }
  });


  dragula([topicsProperties[0]], {
    moves: function (el, container, handle) {
      return handle.classList.contains('grippy');
    }
  })
    .on('drag', function(el, container, handle) {
      el.querySelector('.grippy').classList.add('cursor-grabbing');
    }).on('dragend', function(el) {
      el.querySelector('.grippy').classList.remove('cursor-grabbing');

      _changeTopicOrder();
    });

  function _changeTopicOrder() {
    var menuItems = $('.topics-settings-item-fields__item');
    var input;

    $.each(menuItems, function(key, item) {
      if (item.style.display !== 'hidden') {
        input = $(item).find('input[type="hidden"]');
        input.val(key);
      }
    });
  }

})();
