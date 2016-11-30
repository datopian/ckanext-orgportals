import datetime
import json

import ckan.plugins as p
import ckan.lib.navl.dictization_functions as df
from ckan.plugins import toolkit as tk
import ckan.logic.action.create as create_core
import ckan.logic.action.update as update_core
from ckan import model

from ckanext.orgportals import db, helpers

def organization_create(context, data_dict):
    try:
        data_dict.update({'orgportals_portal_created': u'1'})
        org = create_core.organization_create(context, data_dict)
        _create_portal(data_dict['name'])

        return org
    except p.toolkit.ValidationError:
        return create_core.organization_create(context, data_dict)


def organization_update(context, data_dict):
    try:
        org_show = tk.get_action('organization_show')({}, {'id': data_dict['name']})

        if 'orgportals_portal_created' not in org_show:
            _create_portal(data_dict['name'])

        data_dict.update({'orgportals_portal_created': u'1'})
        org = update_core.organization_update(context, data_dict)

        return org
    except p.toolkit.ValidationError:
        return update_core.organization_update(context, data_dict)


def page_name_validator(key, data, errors, context):
    session = context['session']
    page_name = context.get('page_name')
    org_name = context.get('org_name')

    if page_name and page_name == data[key]:
        return

    query = session.query(db.Page.name).filter_by(name=data[key], org_name=org_name)

    result = query.first()

    if result:
        errors[key].append(
            p.toolkit._('Page name already exists in database'))

schema = {
    'id': [p.toolkit.get_validator('ignore_empty'), unicode],
    'name': [p.toolkit.get_validator('not_empty'), unicode,
             p.toolkit.get_validator('name_validator'), page_name_validator],
    'org_name': [p.toolkit.get_validator('not_empty'), unicode],
    'type': [p.toolkit.get_validator('not_empty'), unicode],
    'page_title': [p.toolkit.get_validator('not_empty'), unicode],
    'content_title': [p.toolkit.get_validator('ignore_missing'), unicode],
    'order': [p.toolkit.get_validator('ignore_missing'), unicode],
    'image_url': [p.toolkit.get_validator('ignore_empty'), unicode],
    'text_box': [p.toolkit.get_validator('ignore_empty'), unicode],
    'content': [p.toolkit.get_validator('ignore_missing'), unicode],
    'themes': [p.toolkit.get_validator('ignore_missing'), unicode],
    'datasets_per_page': [p.toolkit.get_validator('ignore_empty'), int],
    'survey_enabled': [p.toolkit.get_validator('ignore_missing'), bool],
    'survey_text': [p.toolkit.get_validator('ignore_missing'), unicode],
    'survey_link': [p.toolkit.get_validator('ignore_missing'), unicode],
    'map': [p.toolkit.get_validator('ignore_missing'), unicode],
    'map_main_property': [p.toolkit.get_validator('ignore_missing'), unicode],
    'map_enabled': [p.toolkit.get_validator('ignore_missing'), unicode],
    'created': [p.toolkit.get_validator('ignore_missing'),
                p.toolkit.get_validator('isodate')],
    'updated': [p.toolkit.get_validator('ignore_missing'),
                p.toolkit.get_validator('isodate')]
}

def _pages_show(context, data_dict):
    org_name = data_dict['org_name']
    page_name = data_dict['page_name']
    page = db.Page.get_page_for_org(org_name, page_name)
    if page:
        page = db.table_dictize(page, context)
    return page

def _pages_list(context, data_dict):
    org_name = data_dict['org_name']
    pages = db.Page.get_pages_for_org(org_name=org_name)
    pages_dictized = []

    for page in pages:
        page = db.table_dictize(page, context)
        pages_dictized.append(page)

    return pages_dictized

def _pages_delete(context, data_dict):
    org_name = data_dict['org_name']
    page_name = data_dict['page_name']
    page = db.Page.get_page_for_org(org_name, page_name)
    if page:
        session = context['session']
        session.delete(page)
        session.commit()

def _pages_update(context, data_dict):

    org_name = data_dict.get('org_name')
    _page_name = data_dict.get('page_name')
    page_name = data_dict.get('name')
    page_title = data_dict.get('page_title')
    # we need the page in the context for name validation
    context['page_name'] = _page_name
    context['org_name'] = org_name

    session = context['session']

    data, errors = df.validate(data_dict, schema, context)

    if errors:
        raise p.toolkit.ValidationError(errors)

    out = db.Page.get_page_for_org(org_name, _page_name)

    if not out:
        out = db.Page()
        out.org_name = org_name
        out.name = page_name

    items = ['page_title', 'content_title', 'content', 'name', 'image_url',
             'type', 'text_box',
             'themes', 'datasets_per_page', 'survey_enabled',
             'survey_text', 'survey_link', 'map', 'map_main_property',
             'map_enabled', 'order']
    for item in items:
        setattr(out, item, data.get(item))

    extras = {}
    extra_keys = set(schema.keys()) - set(items + ['id', 'created'])
    for key in extra_keys:
        if key in data:
            extras[key] = data.get(key)
    out.extras = json.dumps(extras)

    out.modified = datetime.datetime.utcnow()
    out.save()
    session.add(out)
    session.commit()


def _create_portal(org_name):
    _create_pages(org_name)


def _create_pages(org_name):
    pages = [
        {'org_name': org_name, 'type': 'home', 'name': 'home', 'page_title': 'Home', 'order': 0},
        {'org_name': org_name, 'type': 'data', 'name': 'data', 'page_title': 'Data', 'order': 1},
        {'org_name': org_name, 'type': 'default', 'name': 'about', 'page_title': 'About', 'order': 2},
        {'org_name': org_name, 'type': 'default', 'name': 'help', 'page_title': 'Help', 'order': 3},
        {'org_name': org_name, 'type': 'default', 'name': 'resources', 'page_title': 'Resources', 'order': 4},
        {'org_name': org_name, 'type': 'default', 'name': 'glossary', 'page_title': 'Glossary', 'order': 5},
        {'org_name': org_name, 'type': 'default', 'name': 'contact', 'page_title': 'Contact', 'order': 6},
    ]

    for page in pages:
        out = db.Page()
        out.name = page['name']
        out.org_name = page['org_name']
        out.type = page['type']
        out.page_title = page['page_title']
        out.order = page['order']
        out.save()
        model.Session.add(out)

    model.Session.commit()


@tk.side_effect_free
def pages_show(context, data_dict):
    try:
        p.toolkit.check_access('orgportals_pages_show', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_show(context, data_dict)


def pages_update(context, data_dict):
    try:
        p.toolkit.check_access('orgportals_pages_update', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_update(context, data_dict)


def pages_delete(context, data_dict):
    try:
        p.toolkit.check_access('orgportals_pages_delete', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_delete(context, data_dict)

@tk.side_effect_free
def pages_list(context, data_dict):
    return _pages_list(context, data_dict)

@p.toolkit.side_effect_free
def orgportals_resource_show_map_properties(context, data_dict):
    return helpers.orgportals_get_geojson_properties(data_dict.get('id'))
