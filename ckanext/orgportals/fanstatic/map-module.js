ckan.module('orgportals_map', function ($, _) {
  'use strict';

  return {
    initialize: function() {
      ckan.orgportals.dashboardmap.init(this.options.id,
                                           this.options.organizationName,
                                           this.options.mapurl,
                                           this.options.color,
                                           this.options.main_property);
    }
  }
});
