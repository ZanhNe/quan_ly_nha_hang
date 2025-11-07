from app.extentions.extentions import db
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, Enum

class VaiTro(db.Model):
    __tablename__ = 'vai_tro'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column('name', String(50), nullable=False, unique=True)


class TaiKhoan(db.Model):
    __tablename__= 'tai_khoan'
    id: Mapped[int] = mapped_column('id', primary_key=True, autoincrement=True)
    account_name: Mapped[str] = mapped_column('account_name', String(500), unique=True, nullable=False)
    password: Mapped[str] = mapped_column('password', String(1500), nullable=False)



