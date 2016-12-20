ckan.module('orgportals_map', function ($, _) {
  'use strict';

  return {
    initialize: function() {
      ckan.orgportals.dashboardmap.init(this.options.id,
                                        this.options.country_name,
                                        this.options.mapurl,
                                        this.options.color,
                                        this.options.main_property,
                                        this.options.map_selector_name,
                                        this.options.organization_entity_name);
    }
  }
});
