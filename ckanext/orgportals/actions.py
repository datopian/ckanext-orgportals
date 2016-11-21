import datetime
import json

import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk

import db

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
    pages_list = {}
    return pages_list

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