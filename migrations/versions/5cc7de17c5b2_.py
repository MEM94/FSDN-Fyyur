"""empty message

Revision ID: 5cc7de17c5b2
Revises: b35e82f5476b
Create Date: 2020-10-08 17:26:29.913915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cc7de17c5b2'
down_revision = 'b35e82f5476b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=300), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.add_column('Show', sa.Column('start_time', sa.String(), nullable=False))
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    op.drop_column('Show', 'genres')
    op.drop_column('Show', 'name')
    op.drop_column('Show', 'state')
    op.drop_column('Show', 'city')
    op.drop_column('Show', 'facebook_link')
    op.drop_column('Show', 'image_link')
    op.drop_column('Show', 'phone')
    op.add_column('Venue', sa.Column('description', sa.String(length=300), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'description')
    op.add_column('Show', sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    op.drop_column('Show', 'start_time')
    op.drop_column('Show', 'artist_id')
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
