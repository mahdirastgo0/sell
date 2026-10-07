from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, Boolean, DateTime, ForeignKey, Integer, Text, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase): pass

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    telegram_id: Mapped[int]=mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str|None]=mapped_column(String(255))
    first_name: Mapped[str|None]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Plan(Base):
    __tablename__='plans'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    description: Mapped[str]=mapped_column(Text, default='')
    price: Mapped[int]=mapped_column(BigInteger)
    volume_gb: Mapped[int]=mapped_column(Integer)
    duration_days: Mapped[int]=mapped_column(Integer)
    inbound_id: Mapped[int]=mapped_column(Integer)
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)
    sort_order: Mapped[int]=mapped_column(Integer, default=0)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Order(Base):
    __tablename__='orders'
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    plan_id: Mapped[int]=mapped_column(ForeignKey('plans.id'))
    status: Mapped[str]=mapped_column(String(30), default='awaiting_receipt', index=True)
    amount: Mapped[int]=mapped_column(BigInteger)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now, onupdate=now)
    user = relationship('User')
    plan = relationship('Plan')

class Payment(Base):
    __tablename__='payments'
    id: Mapped[int]=mapped_column(primary_key=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'), unique=True)
    receipt_file_id: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(30), default='pending', index=True)
    reviewed_by: Mapped[int|None]=mapped_column(BigInteger)
    review_note: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    reviewed_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))

class Service(Base):
    __tablename__='services'
    id: Mapped[int]=mapped_column(primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey('users.id'), index=True)
    order_id: Mapped[int]=mapped_column(ForeignKey('orders.id'), unique=True)
    plan_id: Mapped[int]=mapped_column(ForeignKey('plans.id'))
    inbound_id: Mapped[int]=mapped_column(Integer)
    email: Mapped[str]=mapped_column(String(255), unique=True)
    sub_id: Mapped[str]=mapped_column(String(255), unique=True)
    uuid: Mapped[str|None]=mapped_column(String(100))
    enabled: Mapped[bool]=mapped_column(Boolean, default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    user = relationship('User')
    plan = relationship('Plan')

class Setting(Base):
    __tablename__='settings'
    key: Mapped[str]=mapped_column(String(100), primary_key=True)
    value: Mapped[str]=mapped_column(Text)
