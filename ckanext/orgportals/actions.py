import ckan.plugins as p
from ckan.plugins import toolkit as tk
import ckan.logic.action.create as create_core
import ckan.logic.action.update as update_core
from ckan import model

import db


def organization_create(context, data_dict):
    try:
        org = create_core.organization_create(context, data_dict)
        _create_portal(data_dict['name'])

        return org
    except p.toolkit.ValidationError:
        return create_core.organization_create(context, data_dict)


def page_name_validator(key, data, errors, context):
    session = context['session']
    page = context.get('page')
    group_id = context.get('group_id')
    if page and page == data[key]:
        return

    query = session.query(db.Page.name).filter_by(name=data[key], group_id=group_id)
    result = query.first()
    if result:
        errors[key].append(
            p.toolkit._('Page name already exists in database'))


def _pages_show(context, data_dict):
    """TODO get requested page from db """
    page = {}
    return page

def _pages_list(context, data_dict):
    """TODO get all pages for organisation from db"""
    pages = db.Page.get_pages()

    return pages

def _pages_delete(context, data_dict):
    """TODO delete requested page from db"""
    page = {}
    if page:
        session = context['session']
        session.delete(page)
        session.commit()

def _pages_update(context, data_dict):
    """TODO update requested page from db"""
    page = {}
    if page:
        session = context['session']
        session.delete(page)
        session.commit()


def _create_portal(org_name):
    pages = [
        {'org_name': org_name, 'type': 'home', 'name': 'home', 'title': 'Home'},
        {'org_name': org_name, 'type': 'data', 'name': 'data', 'title': 'Data'},
        {'org_name': org_name, 'type': 'default', 'name': 'contact', 'title': 'Contact'},
        {'org_name': org_name, 'type': 'default', 'name': 'help', 'title': 'Help'},
        {'org_name': org_name, 'type': 'default', 'name': 'resources', 'title': 'Resources'},
        {'org_name': org_name, 'type': 'default', 'name': 'about', 'title': 'About'},
        {'org_name': org_name, 'type': 'default', 'name': 'glossary', 'title': 'Glossary'}
    ]

    for page in pages:
        out = db.Page()
        out.name = page['name']
        out.org_name = page['org_name']
        out.type = page['type']
        out.title = page['title']
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
    try:
        p.toolkit.check_access('orgportals_pages_list', context, data_dict)
    except p.toolkit.NotAuthorized:
        p.toolkit.abort(401, p.toolkit._('Not authorized to see this page'))
    return _pages_list(context, data_dict)
