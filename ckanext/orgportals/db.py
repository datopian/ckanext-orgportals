import uuid
import datetime
import json

import sqlalchemy as sa
from sqlalchemy.orm import class_mapper

import ckan.model as model

try:
    from sqlalchemy.engine.result import RowProxy
except:
    from sqlalchemy.engine.base import RowProxy

page_table = None
Page = None

menu_table = None
Menu = None

subdashboards_table = None
Subdashboards = None


def _make_uuid():
    return unicode(uuid.uuid4())


def init():
    _create_pages_table()
    _create_menu_table()
    _create_subdashboards_table()


def _create_pages_table():
    class _Page(model.DomainObject):

        @classmethod
        def get_pages_for_org(self, org_name):
            query = model.Session.query(self).autoflush(False)
            query = query.filter_by(org_name=org_name)

            return query

        @classmethod
        def get_page_for_org(self, org_name, page_name):
            query = model.Session.query(self).autoflush(False)
            query = query.filter_by(org_name=org_name, name=page_name)

            return query.first()

    global Page

    Page = _Page

    page_table = sa.Table('orgportal_pages', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column('name', sa.types.UnicodeText, default=u''),
        sa.Column('org_name', sa.types.UnicodeText, default=u''),
        sa.Column('type', sa.types.UnicodeText, default=u''),
        sa.Column('title', sa.types.UnicodeText, default=u''),
        sa.Column('image', sa.types.UnicodeText, default=u''),
        sa.Column('text_box', sa.types.UnicodeText, default=u''),
        sa.Column('content', sa.types.UnicodeText, default=u''),
        sa.Column('email_address', sa.types.UnicodeText, default=u''),
        sa.Column('map', sa.types.UnicodeText, default=u''),
        sa.Column('map_main_property', sa.types.UnicodeText, default=u''),
        sa.Column('map_enabled', sa.types.Boolean, default=False),
        sa.Column('themes', sa.types.UnicodeText, default=u''),
        sa.Column('datasets_per_page', sa.types.INT, default=5),
        sa.Column('survey_enabled', sa.types.Boolean, default=False),
        sa.Column('survey_text', sa.types.UnicodeText, default=u''),
        sa.Column('survey_link', sa.types.UnicodeText, default=u''),
        sa.Column('created', sa.types.DateTime, default=datetime.datetime.utcnow),
        sa.Column('modified', sa.types.DateTime, default=datetime.datetime.utcnow),
        extend_existing=True
    )

    page_table.create(checkfirst=True)

    model.meta.mapper(Page, page_table)


def _create_menu_table():
    class _Menu(model.DomainObject):

        @classmethod
        def get_menu_for_org(self, org_name):
            query = model.Session.query(self).autoflush(False)
            query = query.filter_by(org_name=org_name)
            query = query.order_by(self.order)

            return query

    global Menu

    Menu = _Menu

    menu_table = sa.Table('orgportal_menu', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column('org_name', sa.types.UnicodeText, default=u''),
        sa.Column('name', sa.types.UnicodeText, default=u''),
        sa.Column('title', sa.types.UnicodeText, default=u''),
        sa.Column('order', sa.types.INT, default=100000),
        sa.Column('created', sa.types.DateTime, default=datetime.datetime.utcnow),
        sa.Column('modified', sa.types.DateTime, default=datetime.datetime.utcnow),
        extend_existing=True
    )

    menu_table.create(checkfirst=True)

    model.meta.mapper(Menu, menu_table)


def _create_subdashboards_table():
    class _Subdashboards(model.DomainObject):

        @classmethod
        def get_foo(self):
            return 'foo'

    global Subdashboards

    Subdashboards = _Subdashboards

    subdashboards_table = sa.Table('orgportal_subdashboards', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column('organization_id', sa.types.UnicodeText, default=u''),
        sa.Column('is_active', sa.types.Boolean, default=False),
        sa.Column('description', sa.types.UnicodeText, default=u''),
        sa.Column('map', sa.types.UnicodeText, default=u''),
        sa.Column('map_main_property', sa.types.UnicodeText, default=u''),
        sa.Column('map_enabled', sa.types.Boolean, default=False),
        sa.Column('data_section_enabled', sa.types.Boolean, default=False),
        sa.Column('content_section_enabled', sa.types.Boolean, default=False),
        sa.Column('datasets_filter', sa.types.UnicodeText, default=u''),
        sa.Column('media', sa.types.UnicodeText, default=u''),
        sa.Column('created', sa.types.DateTime, default=datetime.datetime.utcnow),
        sa.Column('modified', sa.types.DateTime, default=datetime.datetime.utcnow),
        extend_existing=True
    )

    subdashboards_table.create(checkfirst=True)

    model.meta.mapper(Subdashboards, subdashboards_table)



def table_dictize(obj, context, **kw):
    '''Get any model object and represent it as a dict'''
    result_dict = {}

    if isinstance(obj, RowProxy):
        fields = obj.keys()
    else:
        ModelClass = obj.__class__
        table = class_mapper(ModelClass).mapped_table
        fields = [field.name for field in table.c]

    for field in fields:
        name = field
        if name in ('current', 'expired_timestamp', 'expired_id'):
            continue
        if name == 'continuity_id':
            continue
        value = getattr(obj, name)
        if name == 'extras' and value:
            result_dict.update(json.loads(value))
        elif value is None:
            result_dict[name] = value
        elif isinstance(value, dict):
            result_dict[name] = value
        elif isinstance(value, int):
            result_dict[name] = value
        elif isinstance(value, datetime.datetime):
            result_dict[name] = value.isoformat()
        elif isinstance(value, list):
            result_dict[name] = value
        else:
            result_dict[name] = unicode(value)

    result_dict.update(kw)

    ##HACK For optimisation to get metadata_modified created faster.

    context['metadata_modified'] = max(result_dict.get('revision_timestamp', ''),
                                       context.get('metadata_modified', ''))

    return result_dict
