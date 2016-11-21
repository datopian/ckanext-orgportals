import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import helpers
import db
import actions
import auth


class OrgportalsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions, inherit=True)

    def __init__(self, name='OrgportalsPlugin'):
        db.init()
        db.Portal()

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'orgportals')

    # IRoutes

    def before_map(self, map):
        ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsController'

        map.connect('orgportal_pages_delete', '/organization/{name}/pages_delete{page:/.*|}',
                    action='pages_delete', ckan_icon='delete', controller=ctrl)

        map.connect('orgportal_pages_edit', '/organization/{name}/pages_edit{page:/.*|}',
                    action='pages_edit', ckan_icon='edit', controller=ctrl)

        map.connect('orgportal_pages_index', '/organization/{name}/pages',
                    action='pages_index', ckan_icon='file', controller=ctrl,
                    highlight_actions='pages_edit pages_index')

        map.connect('orgportals_nav_bar', '/organization/{name}/nav', controller=ctrl,
                    action='nav_bar', ckan_icon='list')


        map.connect('/organization/{name}/home', controller=ctrl,
                    action='view_portal')
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
        actions_dict = {
            'orgportals_pages_show': actions.pages_show,
            'orgportals_pages_update': actions.pages_update,
            'orgportals_pages_delete': actions.pages_delete,
            'orgportals_pages_list': actions.pages_list
        }
        return actions_dict

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'orgportals_pages_show': auth.pages_show,
            'orgportals_pages_update': auth.pages_update,
            'orgportals_pages_delete': auth.pages_delete,
            'orgportals_pages_list': auth.pages_list
       }

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
                helpers.orgportals_replace_or_add_url_param,
            'orgportals_get_current_url':
                helpers.orgportals_get_current_url
        }