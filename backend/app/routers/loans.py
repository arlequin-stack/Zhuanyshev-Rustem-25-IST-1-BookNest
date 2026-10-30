from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app import models, repositories, schemas, services
from app.deps import CurrentUser, Db, Librarian

router = APIRouter(prefix="/loans", tags=["loans"])

def visible_loan(db: Db, loan_id: int, user: CurrentUser) -> models.Loan:
    loan = repositories.get_loan(db, loan_id)
    if not loan or (user.role != "librarian" and loan.user_id != user.id):
        raise HTTPException(status_code=404, detail="Выдача не найдена")
    return loan

@router.get("/mine", response_model=list[schemas.LoanRead])
def my_loans(db: Db, user: CurrentUser):
    return list(db.scalars(select(models.Loan).options(selectinload(models.Loan.book).selectinload(models.Book.author), selectinload(models.Loan.book).selectinload(models.Book.genres)).where(models.Loan.user_id == user.id).order_by(models.Loan.loaned_at.desc())).all())

@router.get("", response_model=list[schemas.LoanRead])
def all_loans(db: Db, _: Librarian):
    return list(db.scalars(select(models.Loan).options(selectinload(models.Loan.book).selectinload(models.Book.author), selectinload(models.Loan.book).selectinload(models.Book.genres))).all())

@router.get("/{loan_id}", response_model=schemas.LoanRead)
def one_loan(loan_id: int, db: Db, user: CurrentUser):
    return visible_loan(db, loan_id, user)

@router.post("", response_model=schemas.LoanRead, status_code=201)
def issue(data: schemas.LoanCreate, db: Db, user: CurrentUser):
    return services.issue_book(db, user, data)

@router.post("/{loan_id}/return", response_model=schemas.LoanRead)
def return_loan(loan_id: int, db: Db, user: CurrentUser):
    return services.return_book(db, visible_loan(db, loan_id, user))

