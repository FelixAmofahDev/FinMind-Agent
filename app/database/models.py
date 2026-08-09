from __future__ import annotations

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    businessId: Mapped[str] = mapped_column(String(255), nullable=False)
    fullName: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phoneNumber: Mapped[str | None] = mapped_column(String(255), nullable=True)
    passwordHash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    roleTitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pendingEmail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emailVerified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    isActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    lastLoginAt: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="user")


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    ownerName: Mapped[str] = mapped_column(String(255), nullable=False)
    phoneNumber: Mapped[str] = mapped_column(String(255), nullable=False)
    locationRegion: Mapped[str] = mapped_column(String(255), nullable=False)
    locationDistrict: Mapped[str] = mapped_column(String(255), nullable=False)
    recordingMode: Mapped[str] = mapped_column(String(50), nullable=False)
    tier: Mapped[str] = mapped_column(String(50), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="GHS", nullable=False)
    isActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    onboardingComplete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    conversations: Mapped[list["Conversation"]] = relationship(back_populates="business")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    userId: Mapped[str] = mapped_column(String(255), ForeignKey("users.id"), nullable=False)
    businessId: Mapped[str | None] = mapped_column(String(255), ForeignKey("businesses.id"), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    user: Mapped[User] = relationship(back_populates="conversations")
    business: Mapped[Business | None] = relationship(back_populates="conversations")
    messages: Mapped[list["ConversationMessage"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    summary: Mapped["ConversationSummary | None"] = relationship(back_populates="conversation", cascade="all, delete-orphan")
    state: Mapped["ConversationState | None"] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    conversationId: Mapped[str] = mapped_column(String(255), ForeignKey("conversations.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    conversationId: Mapped[str] = mapped_column(String(255), ForeignKey("conversations.id"), nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    topics: Mapped[dict] = mapped_column(JSON, nullable=False)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="summary")


class ConversationState(Base):
    __tablename__ = "conversation_states"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    conversationId: Mapped[str] = mapped_column(String(255), ForeignKey("conversations.id"), nullable=False, unique=True)
    currentTopic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currentIntent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[dict] = mapped_column(JSON, nullable=False)
    lastToolUsed: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lastToolResult: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    createdAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updatedAt: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    conversation: Mapped[Conversation] = relationship(back_populates="state")
