from datetime import datetime

from ckan.plugins import toolkit
from ckan.lib import search


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
