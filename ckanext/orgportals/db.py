import uuid
import datetime

import sqlalchemy as sa

import ckan.model as model

pages_table = None
Pages = None

menu_table = None
Menu = None


def _make_uuid():
    return unicode(uuid.uuid4())


def init():
    _create_pages_table()
    _create_menu_table()


def _create_pages_table():
    class _Pages(model.DomainObject):

        @classmethod
        def get_foo(self):
            return 'foo'

    global Pages

    Pages = _Pages

    pages_table = sa.Table('orgportal_pages', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column('organization_id', sa.types.UnicodeText, default=u''),
        sa.Column('type', sa.types.UnicodeText, default=u''),
        sa.Column('hero_image', sa.types.UnicodeText, default=u''),
        sa.Column('title', sa.types.UnicodeText, default=u''),
        sa.Column('text_box', sa.types.UnicodeText, default=u''),
        sa.Column('content', sa.types.UnicodeText, default=u''),
        sa.Column('email_address', sa.types.UnicodeText, default=u''),
        sa.Column('themes', sa.types.String, default=u''),
        sa.Column('datasets_per_page', sa.types.INT, default=u''),
        sa.Column('survey_enabled', sa.types.Boolean, default=u''),
        sa.Column('survey_text', sa.types.UnicodeText, default=u''),
        sa.Column('survey_link', sa.types.UnicodeText, default=u''),
        sa.Column('subdashboards', sa.types.String, default=u''),
        sa.Column('created', sa.types.DateTime, default=datetime.datetime.utcnow),
        sa.Column('modified', sa.types.DateTime, default=datetime.datetime.utcnow),
        extend_existing=True
    )

    pages_table.create(checkfirst=True)

    model.meta.mapper(Pages, pages_table)


def _create_menu_table():
    class _Menu(model.DomainObject):

        @classmethod
        def get_foo(self):
            return 'foo'

    global Menu

    Menu = _Menu

    menu_table = sa.Table('orgportal_menu', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=_make_uuid),
        sa.Column('organization_id', sa.types.UnicodeText, default=u''),
        sa.Column('title', sa.types.UnicodeText, default=u''),
        sa.Column('order', sa.types.INT, default=u''),
        sa.Column('created', sa.types.DateTime, default=datetime.datetime.utcnow),
        sa.Column('modified', sa.types.DateTime, default=datetime.datetime.utcnow),
        extend_existing=True
    )

    menu_table.create(checkfirst=True)

    model.meta.mapper(Menu, menu_table)
