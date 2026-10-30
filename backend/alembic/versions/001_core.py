"""core tables"""
from alembic import op
import sqlalchemy as sa
revision = "001_core"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False, server_default="member"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.CheckConstraint("role IN ('member','librarian')", name="ck_user_role"), sa.UniqueConstraint("email"))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("profiles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("full_name", sa.String(120), nullable=False), sa.Column("phone", sa.String(32)))
    op.create_table("authors", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(160), nullable=False, unique=True), sa.Column("bio", sa.Text()))
    op.create_index("ix_authors_name", "authors", ["name"])
    op.create_table("genres", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(80), nullable=False, unique=True))
    op.create_table("books", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("title", sa.String(240), nullable=False), sa.Column("isbn", sa.String(20), nullable=False, unique=True), sa.Column("description", sa.Text(), nullable=False), sa.Column("year", sa.Integer(), nullable=False), sa.Column("rating", sa.Float(), nullable=False, server_default="0"), sa.Column("copies_total", sa.Integer(), nullable=False, server_default="1"), sa.Column("copies_available", sa.Integer(), nullable=False, server_default="1"), sa.Column("cover_url", sa.String(500)), sa.Column("author_id", sa.Integer(), sa.ForeignKey("authors.id", ondelete="RESTRICT"), nullable=False), sa.CheckConstraint("year >= 1450", name="ck_book_year"), sa.CheckConstraint("rating >= 0 AND rating <= 5", name="ck_book_rating"), sa.CheckConstraint("copies_total >= 0", name="ck_book_total"), sa.CheckConstraint("copies_available >= 0 AND copies_available <= copies_total", name="ck_book_available"))
    op.create_table("book_genres", sa.Column("book_id", sa.Integer(), sa.ForeignKey("books.id", ondelete="CASCADE"), primary_key=True), sa.Column("genre_id", sa.Integer(), sa.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True))

def downgrade():
    op.drop_table("book_genres"); op.drop_table("books"); op.drop_table("genres"); op.drop_table("authors"); op.drop_table("profiles"); op.drop_table("users")

