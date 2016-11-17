import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.orgportals import helpers


class OrgportalsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'orgportals')

    # IRoutes

    def before_map(self, map):
        ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsController'

        map.connect('/organization/{name}/home', controller=ctrl,
                    action='homepage_show')
        map.connect('/organization/{name}/data', controller=ctrl,
                    action='datapage_show')
        map.connect('/organization/{name}/contact', controller=ctrl,
                    action='contactpage_show')
        map.connect('/organization/{name}/about', controller=ctrl,
                    action='aboutpage_show')
        map.connect('/organization/{name}/help', controller=ctrl,
                    action='helppage_show')
        map.connect('/organization/{name}/resources', controller=ctrl,
                    action='resourcespage_show')
        map.connect('/organization/{name}/glossary', controller=ctrl,
                    action='glossarypage_show')

        return map

    # IActions

    def get_actions(self):
        module_root = 'ckanext.orgportals.logic.action'
        action_functions = _get_logic_functions(module_root)

        return action_functions

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'orgportals_get_newly_released_data':
                helpers.orgportals_get_newly_released_data,
            'orgportals_convert_time_format':
                helpers.orgportals_convert_time_format,
            'orgportals_get_resource_view_url':
                helpers.orgportals_get_resource_view_url,
            'orgportals_get_group_entity_name':
                helpers.orgportals_get_group_entity_name,
            'orgportals_get_facet_items_dict':
                helpers.orgportals_get_facet_items_dict,
            'orgportals_replace_or_add_url_param':
                helpers.orgportals_replace_or_add_url_param
        }


def _get_logic_functions(module_root, logic_functions={}):
    module = __import__(module_root)

    for part in module_root.split('.')[1:]:
        module = getattr(module, part)

    for key, value in module.__dict__.items():
        if not key.startswith('_') and hasattr(value, '__call__')\
                and (value.__module__ == module_root):
                    logic_functions[key] = value

    return logic_functions
