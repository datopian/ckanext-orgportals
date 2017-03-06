import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.plugins as lib_plugins
from ckan import model as m
from sqlalchemy import and_

import helpers
import db
import actions
import auth

from ckan.lib.plugins import DefaultTranslation


class OrgportalsPlugin(plugins.SingletonPlugin,
                       lib_plugins.DefaultOrganizationForm,
                       DefaultTranslation):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IGroupForm, inherit=True)
    plugins.implements(plugins.ITranslation)

    def __init__(self, name='OrgportalsPlugin'):
        db.init()

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'orgportals')

    # IRoutes

    def before_map(self, map):
        ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsController'

        #edit portal admin routes
        map.connect('orgportals_pages_delete', '/organization/edit/{org_name}/pages_delete{page:/.*|}',
                    action='orgportals_pages_delete', ckan_icon='delete', controller=ctrl)
        map.connect('orgportals_pages_edit', '/organization/edit/{org_name}/pages_edit{page:/.*|}',
                    action='orgportals_pages_edit', ckan_icon='edit', controller=ctrl)
        map.connect('orgportals_pages_index', '/organization/edit/{org_name}/pages',
                    action='orgportals_pages_index', ckan_icon='file', controller=ctrl)
        map.connect('orgportals_nav_bar', '/organization/edit/{org_name}/nav', controller=ctrl,
                    action='orgportals_nav_bar', ckan_icon='list')
        map.connect('orgportals_subdashboards_index', '/organization/edit/{org_name}/subdashboards', controller=ctrl,
                    action='orgportals_subdashboards_index', ckan_icon='file')
        map.connect('orgportals_subdashboards_edit', '/organization/edit/{org_name}/subdashboards_edit{subdashboard:/.*|}',
                    action='orgportals_subdashboards_edit', ckan_icon='edit', controller=ctrl)
        map.connect('orgportals_subdashboards_delete', '/organization/edit/{org_name}/subdashboards_delete{subdashboard:/.*|}',
                    action='orgportals_subdashboards_delete', ckan_icon='delete', controller=ctrl)

        #portal routes for custom domain
        map.connect('/', controller=ctrl, action='show_portal_homepage')
        map.connect('/data', controller=ctrl, action='show_portal_datapage')
        map.connect('/contact', controller=ctrl, action='show_portal_contentpage', page_name='contact')
        map.connect('/aboutportal', controller=ctrl, action='show_portal_contentpage', page_name='about')
        map.connect('/help', controller=ctrl, action='show_portal_contentpage', page_name='help')
        map.connect('/resources', controller=ctrl, action='show_portal_contentpage', page_name='resources')
        map.connect('/glossary', controller=ctrl, action='show_portal_contentpage', page_name='glossary')
        map.connect('/pages/{page_name}', controller=ctrl, action='show_portal_custompage')
        map.connect('/subdashboard/{subdashboard_name}', controller=ctrl, action='show_portal_subdashboardpage')


        #portal routes for admin
        map.connect('/organization/{org_name}/portal/home', controller=ctrl,
                    action='view_portal', source='admin')
        map.connect('/organization/{org_name}/portal/data', controller=ctrl,
                    action='datapage_show', source='admin')
        map.connect('/organization/{org_name}/portal/subdashboard/{subdashboard_name}', controller=ctrl,
                    action='subdashboardpage_show', source='admin')
        map.connect('/organization/{org_name}/portal/contact', controller=ctrl,
                    action='contentpage_show', source='admin', page_name='contact')
        map.connect('/organization/{org_name}/portal/about', controller=ctrl,
                    action='contentpage_show', source='admin', page_name='about')
        map.connect('/organization/{org_name}/portal/help', controller=ctrl,
                    action='contentpage_show', source='admin', page_name='help')
        map.connect('/organization/{org_name}/portal/resources', controller=ctrl,
                    action='contentpage_show', source='admin', page_name='resources')
        map.connect('/organization/{org_name}/portal/glossary', controller=ctrl,
                    action='contentpage_show', source='admin', page_name='glossary')
        map.connect('/organization/{org_name}/portal/{page_name}', controller=ctrl,
                    action='custompage_show', source='admin')

        return map

    # IActions
    def get_actions(self):
        actions_dict = {
            'orgportals_pages_show': actions.pages_show,
            'orgportals_pages_update': actions.pages_update,
            'orgportals_pages_delete': actions.pages_delete,
            'orgportals_pages_list': actions.pages_list,
            'orgportals_resource_show_map_properties': actions.orgportals_resource_show_map_properties,
            'organization_create': actions.organization_create,
            'organization_update': actions.organization_update,
            'orgportals_subdashboards_list': actions.subdashboards_list,
            'orgportals_subdashboards_show': actions.subdashboards_show,
            'orgportals_subdashboards_update': actions.subdashboards_update,
            'orgportals_subdashboards_delete': actions.subdashboards_delete,
            'orgportals_show_datasets': actions.orgportals_show_datasets,
            'orgportals_dataset_show_resources': actions.orgportals_dataset_show_resources,
            'orgportals_resource_show_resource_views': actions.orgportals_resource_show_resource_views,
            'orgportals_share_graph_on_twitter': actions.orgportals_share_graph_on_twitter,
            'orgportals_download_dashboard': actions.orgportals_download_dashboard,
            'orgportals_share_image_on_twitter': actions.orgportals_share_image_on_twitter
        }
        return actions_dict

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'orgportals_pages_show': auth.pages_show,
            'orgportals_pages_update': auth.pages_update,
            'orgportals_pages_delete': auth.pages_delete,
            'orgportals_pages_list': auth.pages_list,
            'orgportals_subdashboards_show': auth.subdashboards_show,
            'orgportals_subdashboards_update': auth.subdashboards_update,
            'orgportals_subdashboards_delete': auth.subdashboards_delete,
            'orgportals_subdashboards_list': auth.subdashboards_list,
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
                helpers.orgportals_get_current_url,
            'orgportals_get_copyright_text':
                helpers.orgportals_get_copyright_text,
            'orgportals_convert_to_list':
                helpers.orgportals_convert_to_list,
            'orgportals_get_resource_url':
                helpers.orgportals_get_resource_url,
            'orgportals_get_resource_names_from_ids':
                helpers.orgportals_get_resource_names_from_ids,
            'orgportals_get_org_map_views':
                helpers.orgportals_get_org_map_views,
            'orgportals_resource_show_map_properties':
                helpers.orgportals_resource_show_map_properties,
            'orgportals_get_pages':
                helpers.orgportals_get_pages,
            'orgportals_get_chart_resources':
                helpers.orgportals_get_resourceview_resource_package,
            'orgportals_show_exit_button':
                helpers.orgportals_show_exit_button,
            'orgportals_is_subdashboard_active':
                helpers.orgportals_is_subdashboard_active,
            'orgportals_get_all_organizations':
                helpers.orgportals_get_all_organizations,
            'orgportals_get_available_languages':
                helpers.orgportals_get_available_languages,
            'orgportals_get_current_organization':
                helpers.orgportals_get_current_organization,
            'orgportals_get_secondary_portal':
                helpers.orgportals_get_secondary_portal,
            'orgportals_get_secondary_language':
                helpers.orgportals_get_secondary_language,
            'orgportals_get_country_short_name':
                helpers.orgportals_get_country_short_name,
            'orgportals_get_facebook_app_id':
                helpers.orgportals_get_facebook_app_id,
            'orgportals_get_countries':
                helpers.orgportals_get_countries,
            'orgportals_get_organization_entity_name':
                helpers.orgportals_get_organization_entity_name,
            'orgportals_get_twitter_consumer_keys':
                helpers.orgportals_get_twitter_consumer_keys,
            'orgportals_get_portal_page_url':
                helpers.orgportals_get_portal_page_url,
            'orgportals_get_organization_image':
                helpers.orgportals_get_organization_image
        }

    # IGroupForm

    def is_fallback(self):
        return False

    def group_types(self):
        return ['organization']

    def form_to_db_schema_options(self, options):
        ''' This allows us to select different schemas for different
        purpose eg via the web interface or via the api or creation vs
        updating. It is optional and if not available form_to_db_schema
        should be used.
        If a context is provided, and it contains a schema, it will be
        returned.
        '''
        schema = options.get('context', {}).get('schema', None)
        if schema:
            return schema

        if options.get('api'):
            if options.get('type') == 'create':
                return self.form_to_db_schema_api_create()
            else:
                return self.form_to_db_schema_api_update()
        else:
            return self.form_to_db_schema()

    def form_to_db_schema_api_create(self):
        schema = super(OrgportalsPlugin, self).form_to_db_schema_api_create()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema_api_update(self):
        schema = super(OrgportalsPlugin, self).form_to_db_schema_api_update()
        schema = self._modify_group_schema(schema)
        return schema

    def form_to_db_schema(self):
        schema = super(OrgportalsPlugin, self).form_to_db_schema()
        schema = self._modify_group_schema(schema)
        return schema

    def _modify_group_schema(self, schema):

        # Import core converters and validators
        _convert_to_extras = toolkit.get_converter('convert_to_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')

        default_validators = [_ignore_missing, _convert_to_extras]

        schema.update({
            'orgportals_is_active': default_validators,
            'orgportals_copyright': default_validators,
            'orgportals_lang_is_active': default_validators,
            'orgportals_base_color': default_validators,
            'orgportals_secondary_color': default_validators,
            'orgportals_main_color': default_validators,
            'orgportals_new_data_color': default_validators,
            'orgportals_all_data_color': default_validators,
            'orgportals_portal_created': default_validators,
            'orgportals_secondary_portal': default_validators,
            'orgportals_secondary_language': default_validators,
            'orgportals_portal_url': [_ignore_missing, _convert_to_extras, _domain_validator],
            'orgportals_country': default_validators
        })

        return schema

    def db_to_form_schema(self):

        # Import core converters and validators
        _convert_from_extras = toolkit.get_converter('convert_from_extras')
        _ignore_missing = toolkit.get_validator('ignore_missing')
        _not_empty = toolkit.get_validator('not_empty')

        schema = super(OrgportalsPlugin, self).form_to_db_schema()

        default_validators = [_convert_from_extras, _ignore_missing]
        schema.update({
            'orgportals_is_active': default_validators,
            'orgportals_copyright': default_validators,
            'orgportals_lang_is_active': default_validators,
            'orgportals_base_color': default_validators,
            'orgportals_secondary_color': default_validators,
            'orgportals_main_color': default_validators,
            'orgportals_new_data_color': default_validators,
            'orgportals_all_data_color': default_validators,
            'orgportals_portal_created': default_validators,
            'orgportals_secondary_portal': default_validators,
            'orgportals_secondary_language': default_validators,
            'num_followers': [_not_empty],
            'package_count': [_not_empty],
            'orgportals_portal_url': [_convert_from_extras, _ignore_missing, _domain_validator],
            'orgportals_country': default_validators
        })

        return schema

def _domain_validator(key, data, errors, context):

    session = context['session']
    group_name = data[('name',)]

    if not data[key]:
        return

    query = session.query(m.Group) \
        .join((m.GroupExtra, m.Group.id == m.GroupExtra.group_id)) \
        .filter(and_(m.GroupExtra.key == 'orgportals_portal_url',
                     m.GroupExtra.value == data[key],
                     m.Group.name != group_name))

    result = query.first()

    if result:
        errors[key].append(
            toolkit._('Domain name already exists in database'))
