"""revisi relasi apikey ke apiusagelog

Revision ID: e18f100f78dd
Revises: 195946b48cc1
Create Date: 2025-07-14 15:44:09.490057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e18f100f78dd'
down_revision: Union[str, Sequence[str], None] = '195946b48cc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
