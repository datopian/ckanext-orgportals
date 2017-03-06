import logging
from urllib import urlencode
import cgi
import json
from operator import itemgetter
from urlparse import urlparse
import requests

from pylons import config
from paste.deploy.converters import asbool

import ckan.model as model
from ckan.common import OrderedDict, _, request, c, g, response
from ckan.controllers.package import (PackageController,
                                      _encode_params)
import ckan.lib.base as base
import ckan.logic as logic
import ckan.plugins as p

import ckan.lib.helpers as h
from ckan.lib.search import SearchError
import ckan.lib.maintain as maintain
import ckan.lib.uploader as uploader

from ckanext.orgportals import emailer

log = logging.getLogger(__name__)

check_access = logic.check_access
get_action = logic.get_action


class OrgportalsController(PackageController):
    ctrl = 'ckanext.orgportals.controllers.portals:OrgportalsController'

    def _get_group_dict(self, org_name):
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   }
        data_dict = {'id': org_name,
                     'include_datasets': False,
                     'include_extras': True
                     }

        try:
            group_dict = get_action('organization_show')(context, data_dict)
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Unauthorized to see organization'))
        except p.toolkit.ObjectNotFound:
            p.toolkit.abort(404, _('Group not found'))
        return group_dict


    def orgportals_pages_index(self, org_name):
        data_dict = {'org_name': org_name}
        pages = get_action('orgportals_pages_list')({}, data_dict)

        c.pages = pages
        c.group_dict = self._get_group_dict(org_name)

        return p.toolkit.render('organization/pages_list.html')

    def orgportals_pages_edit(self, org_name, page=None, data=None, errors=None, error_summary=None):

        if page:
            page = page[1:]
        data_dict = {
            'org_name': org_name,
            'page_name': page
        }
        _page = get_action('orgportals_pages_show')({}, data_dict)

        if _page is None and len(page) > 0:
            p.toolkit.abort(404, _('Page not found.'))

        if _page is None:
            _page = {}

        if p.toolkit.request.method == 'POST' and not data:
            if 'type' not in _page:
                _page['type'] = 'custom'

            data = dict(p.toolkit.request.POST)

            # Upload images for portal pages
            if 'image_upload' in dict(p.toolkit.request.params):
                image_upload =  dict(p.toolkit.request.params)['image_upload']

                if isinstance(image_upload, cgi.FieldStorage):
                    upload = uploader.get_uploader('portal', data['image_url'])
                    upload.update_data_dict(data, 'image_url', 'image_upload', 'clear_upload')
                    upload.upload(uploader.get_max_image_size())
                    image_url = upload.filename
                else:
                    image_url = data['image_url']
            else:
                image_url = None

            if 'type' in _page and _page['type'] == 'data':
                _page['map'] = []
                _page['map_main_property'] = []

                for k, v in data.items():
                    if k.startswith('map_main_property'):
                        _page['map_main_property'].append(v)
                    elif k.startswith('map_') and not k.startswith('map_enabled'):
                        _page['map'].append(v)

                _page['map'] = ';'.join(_page['map'])
                _page['map_main_property'] = ';'.join(_page['map_main_property'])

                topics = []

                for k, v in data.items():
                    item = {}

                    if k.startswith('topic_title'):
                        id = k[-1]
                        item['title'] = data['topic_title_{}'.format(id)]
                        item['enabled'] = data['topic_enabled_{}'.format(id)]
                        item['subdashboard'] = data['topic_subdashboard_{}'.format(id)]
                        item['order'] = data['topic_order_{}'.format(id)]

                        image_url = data['topic_image_url_{}'.format(id)]

                        # Upload images for topics
                        if h.uploads_enabled():
                            image_upload = data['topic_image_upload_{}'.format(id)]

                            if isinstance(image_upload, cgi.FieldStorage):
                                upload = uploader.get_uploader('portal', image_url)
                                upload.update_data_dict(data, 'topic_image_url_{}'.format(id), 'topic_image_upload_{}'.format(id), 'topic_clear_upload_{}'.format(id))
                                upload.upload(uploader.get_max_image_size())
                                image_url = upload.filename

                        item['image_url'] = image_url

                        topics.append(item)

                _page['topics'] = json.dumps(topics)

            _page.update(data)
            _page['org_name'] = org_name
            _page['page_name'] = page
            _page['image_url'] = image_url

            try:
                junk = p.toolkit.get_action('orgportals_pages_update')(
                    data_dict=_page
                )
            except p.toolkit.ValidationError, e:

                errors = e.error_dict
                error_summary = e.error_summary
                return self.orgportals_pages_edit(org_name,'/' + page, data,
                                       errors, error_summary)
            p.toolkit.redirect_to(p.toolkit.url_for('orgportals_pages_index', org_name=org_name))

        try:
            p.toolkit.check_access('orgportals_pages_update', {'user': p.toolkit.c.user or p.toolkit.c.author})
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Unauthorized to create or edit a page'))

        if not data:
            data = _page

        errors = errors or {}
        error_summary = error_summary or {}

        if 'topics' in data and len(data['topics']) > 0:
            data['topics'] = json.loads(data['topics'])
            data['topics'].sort(key=itemgetter('order'))

        if _page:
            data_dict = {'org_name': org_name}
            subdashboards = p.toolkit.get_action('orgportals_subdashboards_list')({}, data_dict)
            subdashboards = [{'value': subdashboard['name'], 'text': subdashboard['name']} for subdashboard in subdashboards]
            subdashboards.insert(0, {'value': '$none$', 'text':'None'})
            data['subdashboards'] = subdashboards

        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'page': _page}

        c.group_dict = self._get_group_dict(org_name)

        return p.toolkit.render('organization/pages_edit.html', extra_vars=vars)

    def orgportals_pages_delete(self, org_name, page):

        page = page[1:]

        data_dict = {
            'org_name': org_name,
            'page_name': page
        }

        try:
            if p.toolkit.request.method == 'POST':
                p.toolkit.get_action('orgportals_pages_delete')({}, data_dict)
                p.toolkit.redirect_to(controller=self.ctrl, action='orgportals_pages_index', org_name=org_name)
            else:
                p.toolkit.abort(404, _('Page Not Found'))
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Unauthorized to delete page'))
        except p.toolkit.ObjectNotFound:
            p.toolkit.abort(404, _('Group not found'))
        return p.toolkit.render('organization/confirm_delete.html', {'page': page})

    def orgportals_nav_bar(self, org_name):
        data_dict = {'org_name': org_name}
        pages = get_action('orgportals_pages_list')({}, data_dict)
        menu = []

        for page in pages:
            data = {
                'page_title': page['page_title'],
                'order': page['order'],
                'name': page['name']
            }
            menu.append(data)

        extra_vars = {
            'menu': menu
        }

        c.group_dict = self._get_group_dict(org_name)

        if p.toolkit.request.method == 'POST':
            data = dict(p.toolkit.request.POST)

            for k, v in data.items():
                if k.startswith('menu_item_name'):
                    page_name = k.split('_')[-1]

                    data_dict = {
                        'org_name': org_name,
                        'page_name': page_name
                    }

                    page = get_action('orgportals_pages_show')({}, data_dict)

                    page['order'] = int(v)
                    page['org_name'] = org_name
                    page['page_name'] = page_name

                    p.toolkit.get_action('orgportals_pages_update')({}, data_dict=page)

            p.toolkit.redirect_to(p.toolkit.url_for('orgportals_pages_index', org_name=org_name))

        return p.toolkit.render('organization/nav_bar.html', extra_vars=extra_vars)

    def view_portal(self, org_name):

        if not _is_portal_active(org_name):
            extra_vars = {'type': 'portal'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        data_dict = {
            'org_name': org_name,
            'page_name': 'home'
        }
        page = p.toolkit.get_action('orgportals_pages_show')({}, data_dict)

        is_upload = page['image_url'] and not page['image_url'].startswith('http')

        if is_upload:
            page['image_url'] = '{0}/uploads/portal/{1}'.format(p.toolkit.request.host_url, page['image_url'])

        extra_vars = {
            'page': page
        }
        c.org_name = org_name
        c.page_name = 'home'

        return p.toolkit.render('portals/pages/home.html', extra_vars=extra_vars)

    def datapage_show(self, org_name):
        data_dict = {'id': org_name, 'include_extras': True}
        org = get_action('organization_show')({}, data_dict)

        if not _is_portal_active(org_name):
            extra_vars = {'type': 'portal'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        package_type = 'dataset'

        c.page_name = 'data'
        c.org_name = org_name

        try:
            context = {
                'model': model,
                'user': c.user or c.author,
                'auth_user_obj': c.userobj
            }

            check_access('site_read', context)
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Not authorized to see this page'))

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
        c.query_error = False
        page = self._get_page_number(request.params)

        try:
            limit = int(org['orgportals_datasets_per_page'])
        except KeyError, ValueError:
            limit = int(config.get('ckanext.orgportals.datasets_per_page',
                                   '6'))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='package', action='search')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', None)
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))

            return search_url(params, package_type)

        c.sort_by = _sort_by

        if not sort_by:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))

            return search_url(params, package_type)

        c.search_url_params = urlencode(_encode_params(params_nopage))

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            search_extras = {}
            fq = ''
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'for_view': True,
                       'auth_user_obj': c.userobj}

            if package_type and package_type != 'dataset':
                # Only show datasets of this particular type
                fq += ' +dataset_type:{type}'.format(type=package_type)
            else:
                # Unless changed via config options, don't show non standard
                # dataset types on the default search page
                if not asbool(
                        config.get('ckan.search.show_all_types', 'False')):
                    fq += ' +dataset_type:dataset'

            facets = OrderedDict()

            default_facet_titles = {
                'organization': _('Organizations'),
                'groups': _('Groups'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'license_id': _('Licenses'),
            }

            for facet in g.facets:
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Add 'author' facet
            facets['author'] = _('Authors')

            # Facet titles
            for plugin in p.PluginImplementations(p.IFacets):
                facets = plugin.dataset_facets(facets, package_type)

            c.facet_titles = facets

            fq += ' +organization:"{}"'.format(org_name)

            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }

            query = get_action('package_search')(context, data_dict)

            # Override the "author" list, to include full name authors
            query['search_facets']['author']['items'] =\
                self._get_full_name_authors(context, org_name)

            c.sort_by_selected = query['sort']

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            c.facets = query['facets']
            c.search_facets = query['search_facets']
            c.page.items = query['results']
        except SearchError, se:
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.search_facets = {}
            c.page = h.Page(collection=[])
        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
            except ValueError:
                p.toolkit.abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                    parameter_name='_%s_limit' % facet))
            c.search_facets_limits[facet] = limit

        maintain.deprecate_context_item(
            'facets',
            'Use `c.search_facets` instead.')

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        data_dict = {
            'org_name': org['name'],
            'page_name': 'data'
        }
        data_page = p.toolkit.get_action('orgportals_pages_show')({}, data_dict)

        if len(data_page['topics']) > 0:
            data_page['topics'] = json.loads(data_page['topics'])
            data_page['topics'].sort(key=itemgetter('order'))
        else:
            data_page['topics'] = []

        subdashboards_list = p.toolkit.get_action('orgportals_subdashboards_list')(context, {'org_name': org['name']})
        subdashboards_dict = {x['name']: x for x in subdashboards_list}
        for topic in data_page['topics']:
            is_upload = topic['image_url'] and not topic['image_url'].startswith('http')

            if is_upload:
                topic['image_url'] = '{0}/uploads/portal/{1}'.format(p.toolkit.request.host_url, topic['image_url'])

            topic['full_attributes'] = subdashboards_dict[topic['subdashboard']]

        extra_vars = {
            'organization': org,
            'data_page': data_page
        }

        return p.toolkit.render('portals/pages/data.html',
                                extra_vars=extra_vars)

    def contentpage_show(self, org_name, page_name):
        if not _is_portal_active(org_name):
            extra_vars = {'type': 'portal'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        data_dict = {
            'org_name': org_name,
            'page_name': page_name
        }

        page = p.toolkit.get_action('orgportals_pages_show')({}, data_dict)

        is_upload = page['image_url'] and not page['image_url'].startswith('http')

        if is_upload:
            page['image_url'] = '{0}/uploads/portal/{1}'.format(p.toolkit.request.host_url, page['image_url'])

        if page_name == 'contact' and p.toolkit.request.method == 'POST':
            data = dict(p.toolkit.request.POST)
            content = data['contact_message']
            subject = data['contact_message'][:10] + '...'
            to = data['contact_email']

            response_message = emailer.send_email(content, subject, to)
            page['contact_response_message'] = response_message

        extra_vars = {
            'page': page
        }
        c.org_name = org_name

        return p.toolkit.render('portals/pages/{0}.html'.format(page_name), extra_vars=extra_vars)

    def custompage_show(self, org_name, page_name):
        if not _is_portal_active(org_name):
            extra_vars = {'type': 'portal'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        data_dict = {
            'org_name': org_name,
            'page_name': page_name
        }
        data = p.toolkit.get_action('orgportals_pages_show')({}, data_dict)

        is_upload = data['image_url'] and not data['image_url'].startswith('http')

        if is_upload:
            data['image_url'] = '{0}/uploads/portal/{1}'.format(p.toolkit.request.host_url, data['image_url'])

        extra_vars = {
            'data': data
        }
        c.org_name = org_name

        return p.toolkit.render('portals/pages/custom.html', extra_vars=extra_vars)

    def _get_full_name_authors(self, context, org_name):

        # "rows" is set to a big number because by default Solr will
        # return only 10 rows, and we need all datasets
        all_packages_dict = {
            'fq': '+dataset_type:dataset +organization:' + org_name,
            'rows': 10000000
        }

        # Find all datasets for the current organization
        datasets_query = get_action('package_search')(context,
                                                      all_packages_dict)

        full_name_authors = set()
        authors_list = []

        for dataset in datasets_query['results']:
            full_name_authors.add(dataset['author'])

        for author in full_name_authors:
            authors_list.append({
                'name': author,
                'display_name': author,
                'count': 1
            })

        return authors_list

    def orgportals_subdashboards_index(self, org_name):
        data_dict = {'org_name': org_name}
        subdashboards = get_action('orgportals_subdashboards_list')({}, data_dict)

        c.subdashboards = subdashboards
        c.group_dict = self._get_group_dict(org_name)

        return p.toolkit.render('organization/subdashboards_list.html')

    def orgportals_subdashboards_edit(self, org_name, subdashboard=None, data=None, errors=None, error_summary=None):

        if subdashboard:
            subdashboard = subdashboard[1:]

        data_dict = {
            'org_name': org_name,
            'subdashboard_name': subdashboard
        }
        _subdashboard = get_action('orgportals_subdashboards_show')({}, data_dict)

        if _subdashboard is None and len(subdashboard) > 0:
            p.toolkit.abort(404, _('Subdashboard not found.'))

        if _subdashboard is None:
            _subdashboard = {}

        if p.toolkit.request.method == 'POST' and not data:
            data = dict(p.toolkit.request.POST)

            media_items = []
            for k, v in data.items():
                item = {}

                if k.startswith('media_type'):

                    id = k[-1]
                    if data['media_type_{}'.format(id)] == 'chart':

                        item['order'] = id
                        item['media_type'] = data['media_type_{}'.format(id)]
                        item['media_size'] = data['media_size_{}'.format(id)]
                        item['chart_resourceview'] = data['chart_resourceview_{}'.format(id)]
                        item['chart_subheader'] = data['chart_subheader_{}'.format(id)]

                        media_items.append(item)
                    elif data['media_type_{}'.format(id)] == 'youtube_video':

                        item['order'] = id
                        item['media_type'] = data['media_type_{}'.format(id)]
                        item['video_source'] = data['video_source_{}'.format(id)]

                        media_items.append(item)
                    elif data['media_type_{}'.format(id)] == 'image':

                        item['order'] = id
                        item['media_type'] = data['media_type_{}'.format(id)]
                        item['image_title'] = data['media_image_title_{}'.format(id)]
                        item['image_size'] = data['media_image_size_{}'.format(id)]

                        image_url = data['media_image_url_{}'.format(id)]

                        # Upload images for topics
                        if h.uploads_enabled():
                            image_upload = data['media_image_upload_{}'.format(id)]

                            if isinstance(image_upload, cgi.FieldStorage):
                                upload = uploader.get_uploader('portal', image_url)
                                upload.update_data_dict(data, 'media_image_url_{}'.format(id), 'media_image_upload_{}'.format(id), 'image_clear_upload_{}'.format(id))
                                upload.upload(uploader.get_max_image_size())
                                image_url = upload.filename

                        item['image_url'] = image_url
                        media_items.append(item)

            _subdashboard['media'] = json.dumps(media_items)
            _subdashboard['map'] = []
            _subdashboard['map_main_property'] = []

            for k, v in data.items():
                if k.startswith('map_main_property'):
                    _subdashboard['map_main_property'].append(v)
                elif k.startswith('map_') and not k.startswith('map_enabled'):
                    _subdashboard['map'].append(v)

            _subdashboard['map'] = ';'.join(_subdashboard['map'])
            _subdashboard['map_main_property'] = ';'.join(_subdashboard['map_main_property'])

            _subdashboard.update(data)
            _subdashboard['org_name'] = org_name
            _subdashboard['subdashboard_name'] = subdashboard

            try:
                junk = p.toolkit.get_action('orgportals_subdashboards_update')(
                    data_dict=_subdashboard
                )
            except p.toolkit.ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.orgportals_subdashboards_edit(org_name,'/' + subdashboard, data,
                                       errors, error_summary)

            p.toolkit.redirect_to(p.toolkit.url_for('orgportals_subdashboards_index', org_name=org_name))

        try:
            p.toolkit.check_access('orgportals_subdashboards_update', {'user': p.toolkit.c.user or p.toolkit.c.author})
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Unauthorized to create or edit a subdashboard'))

        if not data:
            data = _subdashboard

        errors = errors or {}
        error_summary = error_summary or {}

        if 'media' in data and len(data['media']) > 0:
            data['media'] = json.loads(data['media'])
            data['media'].sort(key=itemgetter('order'))

        groups = p.toolkit.get_action('group_list')({}, {})
        groups = [{'value': group, 'text': group} for group in groups]
        groups.insert(0, {'value': '$none$', 'text':'None'})
        data['groups'] = groups

        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'subdashboard': _subdashboard}

        c.group_dict = self._get_group_dict(org_name)

        return p.toolkit.render('organization/subdashboards_edit.html', extra_vars=vars)

    def orgportals_subdashboards_delete(self, org_name, subdashboard):

        subdashboard = subdashboard[1:]

        data_dict = {
            'org_name': org_name,
            'subdashboard_name': subdashboard
        }

        try:
            if p.toolkit.request.method == 'POST':
                p.toolkit.get_action('orgportals_subdashboards_delete')({}, data_dict)

                data_dict = {
                    'org_name': org_name,
                    'page_name': 'data'
                }

                page = get_action('orgportals_pages_show')({}, data_dict)

                topics = page['topics']

                if len(topics) > 0:
                    topics = json.loads(topics)
                    topics = [item for item in topics if item['subdashboard'] != subdashboard]

                    page['topics'] = json.dumps(topics)
                    page['page_name'] = 'data'

                    p.toolkit.get_action('orgportals_pages_update')({}, page)

                p.toolkit.redirect_to(controller=self.ctrl, action='orgportals_subdashboards_index', org_name=org_name)
            else:
                p.toolkit.abort(404, _('Subdashboard Not Found'))
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Unauthorized to delete subdashboard'))
        except p.toolkit.ObjectNotFound:
            p.toolkit.abort(404, _('Group not found'))
        return p.toolkit.render('organization/confirm_delete.html', {'subdashboard': subdashboard})

    def subdashboardpage_show(self, org_name, subdashboard_name):
        data_dict = {'id': org_name, 'include_extras': True}
        org = get_action('organization_show')({}, data_dict)

        subdashboards_list = get_action('orgportals_pages_show')({}, {'org_name': org_name, 'page_name': 'data'})
        subdashboards_topics = json.loads(subdashboards_list['topics'])
        subdashboards_dict = {x['subdashboard']: x for x in subdashboards_topics}

        data_dict = {'org_name': org_name, 'subdashboard_name': subdashboard_name}
        subdashboard = get_action('orgportals_subdashboards_show')({}, data_dict)
        subdashboard['subdashboard_title'] = subdashboards_dict[subdashboard['name']]['title']
        org['subdashboards'] = subdashboards_topics

        if not _is_portal_active(org_name):
            extra_vars = {'type': 'portal'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        if 'is_active' in subdashboard and subdashboard['is_active'] == False:
            extra_vars = {'type': 'subdashboard'}

            return p.toolkit.render('portals/snippets/not_active.html', extra_vars=extra_vars)

        package_type = 'dataset'

        try:
            context = {
                'model': model,
                'user': c.user or c.author,
                'auth_user_obj': c.userobj
            }

            check_access('site_read', context)
        except p.toolkit.NotAuthorized:
            p.toolkit.abort(401, _('Not authorized to see this page'))

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', u'')
        c.query_error = False
        page = self._get_page_number(request.params)

        try:
            limit = int(org['orgportals_datasets_per_page'])
        except KeyError, ValueError:
            limit = int(config.get('ckanext.orgportals.datasets_per_page',
                                   '6'))

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']

        def drill_down_url(alternative_url=None, **by):
            return h.add_url_param(alternative_url=alternative_url,
                                   controller='package', action='search',
                                   new_params=by)

        c.drill_down_url = drill_down_url

        def remove_field(key, value=None, replace=None):
            return h.remove_url_param(key, value=value, replace=replace,
                                      controller='package', action='search')

        c.remove_field = remove_field

        sort_by = request.params.get('sort', None)
        params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

        def _sort_by(fields):
            """
            Sort by the given list of fields.

            Each entry in the list is a 2-tuple: (fieldname, sort_order)

            eg - [('metadata_modified', 'desc'), ('name', 'asc')]

            If fields is empty, then the default ordering is used.
            """
            params = params_nosort[:]

            if fields:
                sort_string = ', '.join('%s %s' % f for f in fields)
                params.append(('sort', sort_string))

            return search_url(params, package_type)

        c.sort_by = _sort_by

        if not sort_by:
            c.sort_by_fields = []
        else:
            c.sort_by_fields = [field.split()[0]
                                for field in sort_by.split(',')]

        def pager_url(q=None, page=None):
            params = list(params_nopage)
            params.append(('page', page))

            return search_url(params, package_type)

        c.search_url_params = urlencode(_encode_params(params_nopage))

        try:
            c.fields = []
            # c.fields_grouped will contain a dict of params containing
            # a list of values eg {'tags':['tag1', 'tag2']}
            c.fields_grouped = {}
            search_extras = {}
            fq = ''
            for (param, value) in request.params.items():
                if param not in ['q', 'page', 'sort'] \
                        and len(value) and not param.startswith('_'):
                    if not param.startswith('ext_'):
                        c.fields.append((param, value))
                        fq += ' %s:"%s"' % (param, value)
                        if param not in c.fields_grouped:
                            c.fields_grouped[param] = [value]
                        else:
                            c.fields_grouped[param].append(value)
                    else:
                        search_extras[param] = value

            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author, 'for_view': True,
                       'auth_user_obj': c.userobj}

            if package_type and package_type != 'dataset':
                # Only show datasets of this particular type
                fq += ' +dataset_type:{type}'.format(type=package_type)
            else:
                # Unless changed via config options, don't show non standard
                # dataset types on the default search page
                if not asbool(
                        config.get('ckan.search.show_all_types', 'False')):
                    fq += ' +dataset_type:dataset'

            facets = OrderedDict()

            default_facet_titles = {
                'organization': _('Organizations'),
                'groups': _('Groups'),
                'tags': _('Tags'),
                'res_format': _('Formats'),
                'license_id': _('Licenses'),
            }

            for facet in g.facets:
                if facet in default_facet_titles:
                    facets[facet] = default_facet_titles[facet]
                else:
                    facets[facet] = facet

            # Add 'author' facet
            facets['author'] = _('Authors')

            # Facet titles
            for plugin in p.PluginImplementations(p.IFacets):
                facets = plugin.dataset_facets(facets, package_type)

            c.facet_titles = facets

            fq += ' +organization:"{0}"+groups:{1}'.format(org_name, subdashboard['group'])

            data_dict = {
                'q': q,
                'fq': fq.strip(),
                'facet.field': facets.keys(),
                'rows': limit,
                'start': (page - 1) * limit,
                'sort': sort_by,
                'extras': search_extras
            }

            query = get_action('package_search')(context, data_dict)

            # Override the "author" list, to include full name authors
            query['search_facets']['author']['items'] =\
                self._get_full_name_authors(context, org_name)

            c.sort_by_selected = query['sort']

            c.page = h.Page(
                collection=query['results'],
                page=page,
                url=pager_url,
                item_count=query['count'],
                items_per_page=limit
            )
            c.facets = query['facets']
            c.search_facets = query['search_facets']
            c.page.items = query['results']
        except SearchError, se:
            log.error('Dataset search error: %r', se.args)
            c.query_error = True
            c.facets = {}
            c.search_facets = {}
            c.page = h.Page(collection=[])
        c.search_facets_limits = {}
        for facet in c.search_facets.keys():
            try:
                limit = int(request.params.get('_%s_limit' % facet,
                                               g.facets_default_number))
            except ValueError:
                p.toolkit.abort(400, _('Parameter "{parameter_name}" is not '
                             'an integer').format(
                    parameter_name='_%s_limit' % facet))
            c.search_facets_limits[facet] = limit

        maintain.deprecate_context_item(
            'facets',
            'Use `c.search_facets` instead.')

        self._setup_template_variables(context, {},
                                       package_type=package_type)

        if 'media' in subdashboard and len(subdashboard['media']) > 0:
            subdashboard['media'] = json.loads(subdashboard['media'])
            subdashboard['media'].sort(key=itemgetter('order'))

            for item in subdashboard['media']:
                is_upload = 'image_url' in item and item['image_url'] and not item['image_url'].startswith('http')

                if is_upload:
                    item['image_url'] = '{0}/uploads/portal/{1}'.format(p.toolkit.request.host_url, item['image_url'])

        extra_vars = {
            'organization': org,
            'subdashboard': subdashboard
        }
        c.org_name = org_name

        return p.toolkit.render('portals/pages/subdashboard.html', extra_vars=extra_vars)

    def show_portal_homepage(self):
        return self._get_portal_page(self.view_portal)

    def show_portal_datapage(self):
        return self._get_portal_page(self.datapage_show)

    def show_portal_contentpage(self, page_name):
        return self._get_portal_page(self.contentpage_show, page_name)

    def show_portal_custompage(self, page_name):
        return self._get_portal_page(self.custompage_show, page_name)

    def show_portal_subdashboardpage(self, subdashboard_name):
        return self._get_portal_page(self.subdashboardpage_show, subdashboard_name)


    def _get_portal_page(self, callback, requested_page_name=None):
        name = None
        request_url = urlparse(p.toolkit.request.url)
        ckan_base_url = urlparse(config.get('ckan.site_url'))

        if request_url.netloc != ckan_base_url.netloc:

            org_list = get_action('organization_list')({}, {'all_fields': True, 'include_extras': True})

            for org in org_list:
                if 'orgportals_portal_url' in org:
                    org_url = urlparse(org['orgportals_portal_url'])
                    if org_url.netloc == request_url.netloc:
                        name = org['name']

            if name is None:
                c.url = p.toolkit.request.url
                return p.toolkit.render('portals/snippets/domain_not_registered.html')
            else:
                if requested_page_name is None:
                    return callback(name)
                else:
                    return callback(name, requested_page_name)

        else:
            return p.toolkit.render('home/index.html')

def _is_portal_active(orgnization_name):
    data_dict = {'id': orgnization_name, 'include_extras': True}
    org = get_action('organization_show')({}, data_dict)

    if 'orgportals_is_active' in org and org['orgportals_is_active'] == '1':
        return True
    else:
        return False




