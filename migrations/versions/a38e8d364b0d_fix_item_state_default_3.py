"""fix_item_state_default #3

Revision ID: a38e8d364b0d
Revises: 259041382532
Create Date: 2026-07-31 17:03:42.512620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a38e8d364b0d'
down_revision: Union[str, Sequence[str], None] = '259041382532'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Cria o tipo ENUM no banco de dados primeiro se ele não existir
    sa.Enum('available', 'unavailable', 'trash', name='itemstate').create(op.get_bind(), checkfirst=True)

    # ... aqui deve estar o op.create_table('items', ...) gerado pelo Alembic

    # 2. Adicione esta linha logo APÓS o op.create_table se o campo não estiver lá, 
    # ou certifique-se de que ela esteja como um sa.Column dentro do op.create_table:
    op.add_column('items', sa.Column(
        'state', 
        postgresql.ENUM('available', 'unavailable', 'trash', name='itemstate', create_type=False),
        server_default=sa.text("'available'::itemstate"),
        nullable=False
    ))

def downgrade() -> None:
    # Remove a coluna e dropa o tipo ENUM caso queira desfazer
    op.drop_column('items', 'state')
    sa.Enum(name='itemstate').drop(op.get_bind(), checkfirst=True)
