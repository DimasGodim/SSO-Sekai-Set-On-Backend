"""typo name ganti title

Revision ID: adcb282f7cd0
Revises: 4505de545064
Create Date: 2025-07-14 14:16:19.766032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adcb282f7cd0'
down_revision: Union[str, Sequence[str], None] = '4505de545064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api_keys', sa.Column('title', sa.String(), nullable=False))
    op.drop_column('api_keys', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api_keys', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('api_keys', 'title')
    # ### end Alembic commands ###
