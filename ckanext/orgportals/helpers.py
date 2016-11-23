from datetime import datetime
from urllib import urlencode

from pylons import config

from ckan.plugins import toolkit
from ckan.lib import search
import ckan.lib.helpers as lib_helpers
from ckan.logic.validators import resource_id_exists
from ckan import model


def _get_ctx():
    return {
        'model': model,
        'session': model.Session,
        'user': 'sysadmin'
    }


def orgportals_get_newly_released_data(organization_name, limit=4):
    try:
        pkg_search_results = toolkit.get_action('package_search')(data_dict={
            'fq': ' organization:{}'.format(organization_name),
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
                                        action, context_name):
    for k, v in params:
        # Reset the page to the first one
        if k == 'page':
            params.remove((k, v))
            params.insert(0, ('page', '1'))
        if k != name:
            continue
        params.remove((k, v))

    params.append((name, value))

    url = lib_helpers.url_for(controller=controller,
                              action=action,
                              name=context_name)

    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params]

    return url + u'?' + urlencode(params)


def orgportals_get_current_url(page, params, controller, action, name,
                               exclude_param=''):
    url = lib_helpers.url_for(controller=controller, action=action, name=name)

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


def orgportals_get_menu(org_name):
    data_dict = {
        'org_name': org_name
    }
    menu = toolkit.get_action('orgportals_get_menu')({}, data_dict)

    return menu


def orgportals_convert_to_list(resources):
    if not resources.startswith('{'):
        return [resources]
    resources = resources[1:len(resources) - 1].split(',')
    for i in range(len(resources)):
        if resources[i].startswith('"'):
            resources[i] = resources[i][1:len(resources[i]) - 1]

    return resources


def orgportals_get_resource_url(id):
    if not resource_id_exists(id, _get_ctx()):
        return None

    data = toolkit.get_action('resource_show')({}, {'id': id})

    return data['url']


def orgportals_get_resource_names_from_ids(resource_ids):
    resource_names = []

    for resource_id in resource_ids:
        resource_names.append(toolkit.get_action('resource_show',
                                                 {},
                                                 {'id': resource_id})['name'])

    return resource_names
