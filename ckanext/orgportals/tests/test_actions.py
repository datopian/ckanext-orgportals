import base64
import os

from pylons import config

from ckan.tests.helpers import reset_db
from ckan import plugins
from ckan.tests import factories
from ckan.plugins import toolkit

from ckanext.orgportals.tests.helpers import (id_generator,
                                              create_mock_data,
                                              upload_json_resource,
                                              mock_map_properties,
                                              create_subdashboard)


class TestCustomActions():

    @classmethod
    def setup_class(self, **kwargs):
        # Every time the test is run, the database is resetted
        reset_db()

        if not plugins.plugin_loaded('image_view'):
            plugins.load('image_view')

        if not plugins.plugin_loaded('orgportals'):
            plugins.load('orgportals')

        organization_name = id_generator()
        dataset_name = id_generator()
        group_name = id_generator()
        resource_name = id_generator()
        resource_view_title = id_generator()

        self.mock_data = create_mock_data(
            organization_name=organization_name,
            dataset_name=dataset_name,
            group_name=group_name,
            resource_name=resource_name,
            resource_view_title=resource_view_title)

        self.subdashboard = create_subdashboard(self.mock_data)

    @classmethod
    def teardown_class(self):
        plugins.unload('image_view')
        plugins.unload('orgportals')

    def test_show_datasets(self):
        data_dict = {'id': self.mock_data['organization_name']}

        datasets = toolkit.get_action('orgportals_show_datasets')(
            self.mock_data['context'], data_dict)

        # Create 5 datasets
        for id in range(0, 5):
            factories.Dataset()

        for id in range(5, 0):
            assert datasets[id]['name'] == 'test_dataset_{id}'.format(id=id)

    def test_dataset_show_resources(self):
        data_dict = {'id': self.mock_data['dataset_name']}
        resource_found = False

        resources = toolkit.get_action('orgportals_dataset_show_resources')(
            self.mock_data['context'], data_dict)

        assert len(resources) > 0

        for item in resources:
            if item['name'] == self.mock_data['resource_name']:
                resource_found = True

        assert resource_found is True

    def test_resource_show_resource_views(self):
        data_dict = {
            'id': self.mock_data['resource_id'],
            'view_type': 'image_view'
        }
        resource_view_found = False

        resource_views = toolkit.\
            get_action('orgportals_resource_show_resource_views')(
                self.mock_data['context'], data_dict)

        assert len(resource_views) > 0

        for item in resource_views:
            if item['title'] == self.mock_data['resource_view_title']:
                resource_view_found = True

        assert resource_view_found is True

    def test_resource_show_map_properties(self):
        resource = upload_json_resource(
            self.mock_data['dataset_name'],
            resource_name=id_generator())
        resource_id = resource['id']

        data_dict = {'id': resource_id}

        map_properties = toolkit.get_action(
            'orgportals_resource_show_map_properties')(
            self.mock_data['context'], data_dict)

        assert len(map_properties) == 4

        for i, item in enumerate(mock_map_properties.iteritems()):
            assert map_properties[i]['value'] == item[0]
            assert map_properties[i]['text'] == item[0]

    def test_orgportals_share_graph_on_twitter(self):
        image_path = os.path.join(os.path.realpath(
            os.path.join(os.getcwd(),
                         os.path.dirname(__file__))), 'graph_image.png')

        with open(image_path, 'rb') as image_file:
            base64_image = base64.b64encode(image_file.read())

        data_dict = {
            'oauth_token':
                config.get('ckanext.orgportals.twitter_oauth_token'),
            'oauth_token_secret':
                config.get('ckanext.orgportals.twitter_oauth_token_secret'),
            'graph_title': 'test',
            'subdashboard_url': 'http://google.com',
            'image': base64_image
        }

        response = toolkit.get_action('orgportals_share_graph_on_twitter')(
            self.mock_data['context'], data_dict)

        assert response['share_status_success'] is True

    def test_organization_create(self):
        org = toolkit.get_action('organization_create')(
            self.mock_data['context'], {'name': 'test_org'})

        assert 'orgportals_portal_created' in org
        assert org['orgportals_portal_created'] == '1'

        data_dict = {
            'org_name': org['name']
        }

        pages = toolkit.get_action('orgportals_pages_list')(
            self.mock_data['context'], data_dict)

        assert len(pages) > 0

    def test_orgportals_pages_show(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'home'
        }

        page = toolkit.get_action('orgportals_pages_show')(
            self.mock_data['context'], data_dict)

        assert page['name'] == 'home'
        assert page['org_name'] == self.mock_data['organization_name']

    def test_orgportals_pages_update(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'home',
            'page_title': 'Home',
            'name': 'home',
            'type': 'home',
            'content_title': 'Test title'
        }

        # Update existing page
        toolkit.get_action('orgportals_pages_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'home'
        }

        page = toolkit.get_action('orgportals_pages_show')(
            self.mock_data['context'], data_dict)

        assert page['name'] == 'home'
        assert page['org_name'] == self.mock_data['organization_name']
        assert page['page_title'] == 'Home'
        assert page['content_title'] == 'Test title'

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'test',
            'page_title': 'Test',
            'name': 'test',
            'type': 'custom',
        }

        # Create custom page
        toolkit.get_action('orgportals_pages_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'test'
        }

        page = toolkit.get_action('orgportals_pages_show')(
            self.mock_data['context'], data_dict)

        assert page['name'] == 'test'
        assert page['org_name'] == self.mock_data['organization_name']
        assert page['page_title'] == 'Test'

    def test_orgportals_pages_delete(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'test2',
            'page_title': 'Test2',
            'name': 'test2',
            'type': 'custom',
        }

        # Create custom page
        toolkit.get_action('orgportals_pages_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'test2'
        }

        # Delete the just created custom page
        toolkit.get_action('orgportals_pages_delete')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'page_name': 'test2'
        }

        page = toolkit.get_action('orgportals_pages_show')(
            self.mock_data['context'], data_dict)

        assert page is None

    def test_orgportals_pages_list(self):
        data_dict = {
            'org_name': self.mock_data['organization_name']
        }

        pages = toolkit.get_action('orgportals_pages_list')(
            self.mock_data['context'], data_dict)

        assert len(pages) > 0

    def test_orgportals_subdashboards_show(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'subdashboard_name': self.mock_data['group_name']
        }

        subdashboard = toolkit.get_action('orgportals_subdashboards_show')(
            self.mock_data['context'], data_dict)

        assert subdashboard['name'] == self.mock_data['group_name']
        assert subdashboard['org_name'] == self.mock_data['organization_name']

    def test_orgportals_subdashboards_update(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'name': 'test',
            'group': self.mock_data['group_name'],
            'is_active': True,
            'data_section_enabled': True,
            'content_section_enabled': True
        }

        # Create new subdashboard
        toolkit.get_action('orgportals_subdashboards_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'subdashboard_name': 'test'
        }

        subdashboard = toolkit.get_action('orgportals_subdashboards_show')(
            self.mock_data['context'], data_dict)

        assert subdashboard['name'] == 'test'
        assert subdashboard['org_name'] == self.mock_data['organization_name']
        assert subdashboard['group'] == self.mock_data['group_name']
        assert subdashboard['is_active'] is True
        assert subdashboard['data_section_enabled'] is True
        assert subdashboard['content_section_enabled'] is True

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'name': 'test',
            'subdashboard_name': 'test',
            'group': 'test_group',
            'is_active': True,
            'data_section_enabled': True,
            'content_section_enabled': True
        }

        # Update existing subdashboard
        toolkit.get_action('orgportals_subdashboards_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'subdashboard_name': 'test'
        }

        subdashboard = toolkit.get_action('orgportals_subdashboards_show')(
            self.mock_data['context'], data_dict)

        assert subdashboard['name'] == 'test'
        assert subdashboard['org_name'] == self.mock_data['organization_name']
        assert subdashboard['group'] == 'test_group'
        assert subdashboard['is_active'] is True
        assert subdashboard['data_section_enabled'] is True
        assert subdashboard['content_section_enabled'] is True

    def test_orgportals_subdashboards_delete(self):
        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'name': 'test2',
            'group': self.mock_data['group_name'],
            'is_active': True,
            'data_section_enabled': True,
            'content_section_enabled': True
        }

        # Create new subdashboard
        toolkit.get_action('orgportals_subdashboards_update')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'subdashboard_name': 'test2'
        }

        # Delete the just created custom page
        toolkit.get_action('orgportals_subdashboards_delete')(
            self.mock_data['context'], data_dict)

        data_dict = {
            'org_name': self.mock_data['organization_name'],
            'subdashboard_name': 'test2'
        }

        subdashboard = toolkit.get_action('orgportals_subdashboards_show')(
            self.mock_data['context'], data_dict)

        assert subdashboard is None

    def test_orgportals_subdashboards_list(self):
        data_dict = {
            'org_name': self.mock_data['organization_name']
        }

        subdashboards = toolkit.get_action('orgportals_subdashboards_list')(
            self.mock_data['context'], data_dict)

        assert len(subdashboards) > 0
