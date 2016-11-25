(function nav_bar() {

  var navMenuContainer = document.querySelector('.portal-nav-menu-admin');

  dragula([navMenuContainer])
    .on('drag', function(el) {
      el.classList.add('cursor-grabbing');
    }).on('dragend', function(el) {
      el.classList.remove('cursor-grabbing');

      _changeMenuOrder();
    });

  function _changeMenuOrder() {
    var menuItems = $('.portal-nav-menu-admin__item')

    $.each(menuItems, function(key, item) {
      var input = $(item).find('input');

      input.val(key);
    });
  }

})();
