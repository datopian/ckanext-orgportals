import uuid

import sqlalchemy as sa

import ckan.model as model

portal_table = None
Portal = None


def make_uuid():
    return unicode(uuid.uuid4())


def init():

    class _Portal(model.DomainObject):

        @classmethod
        def get_foo(self):
            return 'foo'

    global Portal

    Portal = _Portal

    portal_table = sa.Table('orgportals_page', model.meta.metadata,
        sa.Column('id', sa.types.UnicodeText, primary_key=True, default=make_uuid),
        sa.Column('foo', sa.types.UnicodeText),
        sa.Column('foo', sa.types.UnicodeText),
        extend_existing=True
    )

    portal_table.create(checkfirst=True)

    model.meta.mapper(Portal, portal_table)
