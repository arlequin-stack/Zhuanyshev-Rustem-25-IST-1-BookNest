"""loans and wishlist"""
from alembic import op
import sqlalchemy as sa
revision = "002_loans"
down_revision = "001_core"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("loans", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="RESTRICT"), nullable=False), sa.Column("loaned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("due_date", sa.Date(), nullable=False), sa.Column("returned_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("user_id", "book_id", "returned_at", name="uq_active_loan"))
    op.create_table("wishlist", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True))
    op.create_index("ix_loans_user_id", "loans", ["user_id"]); op.create_index("ix_loans_book_id", "loans", ["book_id"])

def downgrade():
    op.drop_table("wishlist"); op.drop_table("loans")

