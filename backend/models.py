from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CHAR, TIMESTAMP, CheckConstraint, Date, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class SubscriptionType(Base):
    __tablename__ = "types"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    label: Mapped[str | None] = mapped_column(String(255))

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="sub_type")


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        CheckConstraint("price > 0"),
        CheckConstraint("status IN ('active', 'cancelled')"),
    )

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(CHAR(3), server_default="PLN")
    type: Mapped[str] = mapped_column(String(50), ForeignKey("types.name"))
    renewal_date: Mapped[date] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(INTEGER(unsigned=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), server_default="active")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.current_timestamp())

    user: Mapped[User] = relationship(back_populates="subscriptions")
    sub_type: Mapped[SubscriptionType] = relationship(back_populates="subscriptions")
