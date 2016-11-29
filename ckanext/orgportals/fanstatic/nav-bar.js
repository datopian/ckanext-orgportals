(function nav_bar() {

  var navMenuContainer = document.querySelector('.portal-nav-menu-admin');

  dragula([navMenuContainer], {
    moves: function (el, container, handle) {
      return handle.classList.contains('grippy');
    }
  })
    .on('drag', function(el) {
      el.querySelector('.grippy').classList.add('cursor-grabbing');
    }).on('dragend', function(el) {
      el.querySelector('.grippy').classList.remove('cursor-grabbing');

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
