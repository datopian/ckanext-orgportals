(function themesSettings() {

  var createItemBtn = $('#create-item-btn');
  var itemFields = $('.themes-settings-item-fields');
  var themesProperties = $('.themes-properties');
  var uploadsEnabled = themesProperties.attr('data-uploads-enabled');
  var themeItems;
  var totalItems;

  // Add a theme/dashboard
  createItemBtn.on('click', function onCreateDashboardBtnClick() {
    var newFields = itemFields.contents().clone();

    themeItems = $('.themes-settings-item-fields__item');
    totalItems = themeItems.length;

    newFields.each(function(i, item) {
      var item = $(item);
      var themeTitle;
      var themeSubdashboard;
      var themeEnabled;
      var fieldImageUrl;
      var fieldImageUpload;
      var imageUploadModule;

      if (item.hasClass('themes-settings-item-fields__item')) {
        themeTitle = item.find('#theme_title');
        themeSubdashboard = item.find('#theme_subdashboard');
        themeEnabled = item.find('#theme_enabled');
        themeOrder = item.find('#theme_order');
        themeImage = item.find('#field-image-url');
        themeUpload = item.find('#field-image-upload');

        themeTitle.attr('id', 'theme_title_' + totalItems);
        themeTitle.attr('name', 'theme_title_' + totalItems);
        themeTitle.attr('required', 'true' + totalItems);

        themeSubdashboard.attr('id', 'theme_subdashboard_' + totalItems);
        themeSubdashboard.attr('name', 'theme_subdashboard_' + totalItems);

        themeEnabled.attr('id', 'theme_enabled_' + totalItems);
        themeEnabled.attr('name', 'theme_enabled_' + totalItems);

        themeOrder.attr('id', 'theme_order_' + totalItems);
        themeOrder.attr('name', 'theme_order_' + totalItems);
        themeOrder.attr('value', totalItems);

        fieldImageUrl = 'theme_image_url_' + totalItems;
        fieldImageUpload = 'theme_image_upload_' + totalItems;

        if (uploadsEnabled == 'True') {
          imageUploadModule = item.find('[data-module="custom-image-upload"]');
          imageUploadModule.attr('data-module', 'image-upload');
          imageUploadModule.attr('data-module-field_upload', fieldImageUpload);
          imageUploadModule.attr('data-module-field_url', fieldImageUrl);
          themeUpload.attr('name', fieldImageUpload);
        }

        themeImage.attr('name', fieldImageUrl);

      }
    });

    themesProperties.append(newFields);

    if (uploadsEnabled == 'True') {
      window.ckan.module.initializeElement(newFields.find('[data-module="image-upload"]')[0]);
    }

    // Limit the total number of themes to 6
    if (totalItems == 6) {
      createItemBtn.css('display', 'none');
    }
  });

  // Remove a theme/dashboard
  themesProperties.on('click', '.themes-settings-item-fields__remove-btn', function (e) {
    $(e.target).parent().remove();

    _changeThemesOrder();

    themeItems = $('.themes-settings-item-fields__item');
    totalItems = themeItems.length;

    if (totalItems < 7) {
      createItemBtn.css('display', 'initial');
    }
  });


  dragula([themesProperties[0]], {
    moves: function (el, container, handle) {
      return handle.classList.contains('grippy');
    }
  })
    .on('drag', function(el, container, handle) {
      el.querySelector('.grippy').classList.add('cursor-grabbing');
    }).on('dragend', function(el) {
      el.querySelector('.grippy').classList.remove('cursor-grabbing');

      _changeThemesOrder();
    });

  function _changeThemesOrder() {
    var menuItems = $('.themes-settings-item-fields__item');
    var input;

    $.each(menuItems, function(key, item) {
      if (item.style.display !== 'hidden') {
        input = $(item).find('input[type="hidden"]');
        input.val(key);
      }
    });
  }

})();
