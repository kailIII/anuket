# -*- coding: utf-8 -*-
from sqlalchemy import Table, MetaData, Column, String
from sqlalchemy.orm import mapper


version_num = Column('version_num', String(32), nullable=False)
version_table = Table('alembic_version', MetaData(), version_num)


class Migration(object):
    """ Migration table and model definition.

    Reflect the default version table used by Alembic. This table is used
    by for tracking database migrations.
    """
    def __init__(self, version_num):
        self.version_num = version_num


# the primary_key is defined only at mapper level to avoid
# modifing the original alembic version_table
mapper(Migration, version_table, primary_key=version_num)
