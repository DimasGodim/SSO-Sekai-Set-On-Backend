"""menambahkan relasi apikey ke apiusagelog

Revision ID: 195946b48cc1
Revises: d1464df9b3e6
Create Date: 2025-07-14 15:42:51.388225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '195946b48cc1'
down_revision: Union[str, Sequence[str], None] = 'd1464df9b3e6'
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
