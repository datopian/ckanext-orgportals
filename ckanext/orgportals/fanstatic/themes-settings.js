(function themesSettings() {

  var createDashboardBtn = $('#create-dashboard-btn');
  var subdashboardFields = $('.themes-settings-subdashboard-fields');
  var themesProperties = $('.themes-properties');
  var themeItems;
  var totalItems;

  // Add a theme/dashboard
  createDashboardBtn.on('click', function onCreateDashboardBtnClick() {
    var newFields = subdashboardFields.contents().clone();

    themeItems = $('.themes-settings-subdashboard-fields__item');
    totalItems = themeItems.length;

    newFields.each(function(i, item) {
      var item = $(item);
      var themeTitle;
      var themeGroup;
      var themeEnabled;

      if (item.hasClass('themes-settings-subdashboard-fields__item')) {
        themeTitle = item.find('#theme_title');
        themeGroup = item.find('#theme_group');
        themeEnabled = item.find('#theme_enabled');

        themeTitle.attr('id', 'theme_title_' + totalItems);
        themeTitle.attr('name', 'theme_title_' + totalItems);

        themeGroup.attr('id', 'theme_group_' + totalItems);
        themeGroup.attr('name', 'theme_group_' + totalItems);

        themeEnabled.attr('id', 'theme_enabled_' + totalItems);
        themeEnabled.attr('name', 'theme_enabled_' + totalItems);
      }
    });

    themesProperties.append(newFields);

    // Limit the total number of themes to 6
    if (totalItems == 6) {
      createDashboardBtn.css('display', 'none');
    }
  });

  // Remove a theme/dashboard
  themesProperties.on('click', 'a', function (e) {
    $(e.target).parent().remove();

    themeItems = $('.themes-settings-subdashboard-fields__item');
    totalItems = themeItems.length;

    if (totalItems < 7) {
      createDashboardBtn.css('display', 'initial');
    }
  });

})();
