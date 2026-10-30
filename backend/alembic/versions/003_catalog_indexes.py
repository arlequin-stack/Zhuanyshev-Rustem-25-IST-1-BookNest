"""catalog search indexes"""
from alembic import op
revision = "003_catalog_indexes"
down_revision = "002_loans"
branch_labels = None
depends_on = None

def upgrade():
    op.create_index("ix_books_title", "books", ["title"])
    op.create_index("ix_books_isbn", "books", ["isbn"], unique=True)
    op.create_index("ix_books_author_id", "books", ["author_id"])

def downgrade():
    op.drop_index("ix_books_author_id", table_name="books")
    op.drop_index("ix_books_isbn", table_name="books")
    op.drop_index("ix_books_title", table_name="books")

