ckan.module('orgportals_goto_next_section', function ($, _) {
  'use strict';

  return {
    initialize: function() {
      //We don't need to go to the next section if there is only one section
      if ($("[data-section]").length === 1) {
        $(".next-section-container").hide()
      }

      var nextSectionBtn = this.el;

      nextSectionBtn.on('click', function onNextSectionBtnClick() {
        var section = nextSectionBtn.closest('div[data-section]');
        var nextSection, topOffset;

        if (section.length === 1) {
          nextSection = section.next();
          topOffset = nextSection.offset().top;

          window.scrollTo(0, topOffset - 60);
        }
      });
    }
  }
});
