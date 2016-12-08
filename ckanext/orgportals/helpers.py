from datetime import datetime
from urllib import urlencode
import urllib

from pylons import config


from ckan.plugins import toolkit
from ckan.lib import search
import ckan.lib.helpers as lib_helpers
from ckan.logic.validators import resource_id_exists
from ckan import model
from ckan.common import json
import ckan.logic as l


def _get_ctx():
    return {
        'model': model,
        'session': model.Session,
        'user': 'sysadmin'
    }

def _get_action(action, context_dict, data_dict):
    return toolkit.get_action(action)(context_dict, data_dict)


def orgportals_get_newly_released_data(organization_name, subdashboard_group_name, limit=4):
    fq = ' organization:"{}"'.format(organization_name)

    if subdashboard_group_name:
        fq = '{0}+groups:{1}'.format(fq, subdashboard_group_name)

    try:
        pkg_search_results = toolkit.get_action('package_search')(data_dict={
            'fq': fq,
            'sort': 'metadata_modified desc',
            'rows': limit
        })['results']

    except toolkit.ValidationError, search.SearchError:
        return []
    else:
        pkgs = []

        for pkg in pkg_search_results:
            package = toolkit.get_action('package_show')(data_dict={
                'id': pkg['id']
            })
            modified = datetime.strptime(
                package['metadata_modified'].split('T')[0], '%Y-%m-%d')
            package['human_metadata_modified'] = modified.strftime("%d %B %Y")
            pkgs.append(package)

        return pkgs


def orgportals_convert_time_format(package):
    modified = datetime.strptime(
        package['metadata_modified'].split('T')[0], '%Y-%m-%d')

    return modified.strftime("%d %B %Y")


def orgportals_get_resource_view_url(id, dataset):
    return '/dataset/{0}/resource/{1}'.format(dataset, id)


def orgportals_get_group_entity_name():
    return config.get('ckanext.orgportals.group_entity_name', 'group')


def orgportals_get_facet_items_dict(value):
    try:
        return lib_helpers.get_facet_items_dict(value)
    except:
        return None


def orgportals_replace_or_add_url_param(name, value, params, controller,
                                        action, context_name, subdashboard_name):
    for k, v in params:
        # Reset the page to the first one
        if k == 'page':
            params.remove((k, v))
            params.insert(0, ('page', '1'))
        if k != name:
            continue
        params.remove((k, v))

    params.append((name, value))

    if subdashboard_name:
        url = lib_helpers.url_for(controller=controller,
                                  action=action,
                                  org_name=context_name,
                                  subdashboard_name=subdashboard_name)
    else:
        url = lib_helpers.url_for(controller=controller,
                                  action=action,
                                  org_name=context_name)


    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]

    return url + u'?' + urlencode(params)


def orgportals_get_current_url(page, params, controller, action, name,
                               exclude_param=''):
    url = lib_helpers.url_for(controller=controller, action=action, org_name=name)

    for k, v in params:
        if k == exclude_param:
            params.remove((k, v))

    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]

    if (params):
        url = url + u'?page=' + str(page) + '&' + urlencode(params)
    else:
        url = url + u'?page=' + str(page)

    return url


def orgportals_get_copyright_text(organization_name):
    data_dict = {
        'id': organization_name,
        'include_extras': True
    }
    organization = toolkit.get_action('organization_show')(data_dict=data_dict)

    return organization['orgportals_copyright']


def orgportals_convert_to_list(resources):
    if ';' not in resources:
        return [resources]

    resources = resources.split(';')

    return resources


def orgportals_get_resource_url(id):
    if not resource_id_exists(id, _get_ctx()):
        return None

    data = toolkit.get_action('resource_show')({}, {'id': id})

    return data['url']


def orgportals_get_resource_names_from_ids(resource_ids):
    resource_names = []

    for resource_id in resource_ids:
        resource_names.append(toolkit.get_action('resource_show')({},
                                                 {'id': resource_id})['name'])

    return resource_names


def orgportals_get_org_map_views(name):
        allMaps = {}
        result = [{'value': '', 'text': 'None'}]
        for item in _get_organization_views(name, type='Maps'):
            data = {
                'value': item['id'],
                'text': 'UNNAMED' if item['name'] == '' else item['name']
            }
            result.append(data)
            allMaps.update({name: result})

        return allMaps.get(name) or {}


def _get_organization_views(name, type='chart builder'):
    data_dict = {
        'id': name,
        'include_datasets': True
    }
    data = toolkit.get_action('organization_show')({}, data_dict)

    result = []
    package_names = data.pop('packages', [])

    if any(package_names):
        for _ in package_names:
            package = toolkit.get_action('package_show')({}, {'id': _['name']})
            if not package['num_resources'] > 0:
                continue

            if type == 'chart builder':
                resource_views = map(lambda p: toolkit.get_action('resource_view_list')({},
                                                          {'id': p['id']}), package['resources'])
                if any(resource_views):
                    map(lambda l: result.extend(filter(lambda i: i['view_type'].lower() == type, l)), resource_views)

            elif type.lower() == 'maps':
                result.extend(filter(lambda r: r['format'].lower() in ['geojson', 'gjson'], package['resources']))

            else:
                pass
            # Raise not handled exception

    return result


def orgportals_resource_show_map_properties(id):
    return orgportals_get_geojson_properties(id)


def orgportals_get_geojson_properties(resource_id):
    url = orgportals_get_resource_url(resource_id)

    r = urllib.urlopen(url)

    data = unicode(r.read(), errors='ignore')
    geojson = json.loads(data)

    result = []
    for k, v in geojson.get('features')[0].get('properties').iteritems():
        result.append({'value':k, 'text': k})

    return result


def orgportals_get_pages(org_name):
    data_dict = {'org_name': org_name}

    return toolkit.get_action('orgportals_pages_list')({}, data_dict)

def orgportals_get_resourceview_resource_package(resource_view_id):
    if not resource_view_id:
        return None

    data_dict = {
        'id': resource_view_id
    }
    try:
        resource_view = toolkit.get_action('resource_view_show')({}, data_dict)

    except l.NotFound:
        return None

    data_dict = {
        'id': resource_view['resource_id']
    }
    resource = toolkit.get_action('resource_show')({}, data_dict)

    data_dict = {
        'id': resource['package_id']
    }

    try:
        package = toolkit.get_action('package_show')({}, data_dict)

    except l.NotFound:
        return None

    return [resource_view, resource, package]

def orgportals_show_exit_button(params):
    print params
    for item in params.items():
        if item[0] == 'q':
            return True

    return False

def orgportals_is_subdashboard_active(org_name, subdashboard_name):
    data_dict = {
        'org_name': org_name,
        'subdashboard_name': subdashboard_name
    }

    subdashboard = toolkit.get_action('orgportals_subdashboards_show')({}, data_dict)

    return subdashboard['is_active']
