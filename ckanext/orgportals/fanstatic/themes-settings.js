(function themesSettings() {

  var createDashboardBtn = $('#create-dashboard-btn');
  var subdashboardFields = [
    ''
  ];
  var subdashboardFields = $('.themes-settings-subdashboard-fields');
  var themesProperties = $('.themes-properties');

  createDashboardBtn.on('click', function onCreateDashboardBtnClick() {
    var newFields = subdashboardFields.contents().clone();

    themesProperties.append(newFields);
  });

  themesProperties.on('click', 'a', function (e) {
    $(e.target).parent().remove();
  });

})();
