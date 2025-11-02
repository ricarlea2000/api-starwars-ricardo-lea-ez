from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, UniqueConstraint, CheckConstraint, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, Dict, Any
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True)

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    posts: Mapped[List["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id, 
            "email": self.email, 
            "username": self.username,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Character(db.Model):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(30))
    birth_year: Mapped[Optional[str]] = mapped_column(String(20))
    height_cm: Mapped[Optional[int]] = mapped_column(Integer)
    mass_kg: Mapped[Optional[int]] = mapped_column(Integer)  # Added mass
    homeworld: Mapped[Optional[str]] = mapped_column(String(100))  # Added homeworld
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))  # For character images

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="character", cascade="all, delete-orphan")

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "gender": self.gender,
            "birth_year": self.birth_year,
            "height_cm": self.height_cm,
            "mass_kg": self.mass_kg,
            "homeworld": self.homeworld,
            "description": self.description,
            "image_url": self.image_url,
        }

class Planet(db.Model):
    __tablename__ = "planets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    climate: Mapped[Optional[str]] = mapped_column(String(120))
    terrain: Mapped[Optional[str]] = mapped_column(String(120))
    population: Mapped[Optional[int]] = mapped_column(Integer)
    diameter_km: Mapped[Optional[int]] = mapped_column(Integer)  # Added diameter
    orbital_period_days: Mapped[Optional[int]] = mapped_column(Integer)  # Added orbital period
    description: Mapped[Optional[str]] = mapped_column(Text)
    image_url: Mapped[Optional[str]] = mapped_column(String(255))  # For planet images

    favorites: Mapped[List["Favorite"]] = relationship(back_populates="planet", cascade="all, delete-orphan")

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "population": self.population,
            "diameter_km": self.diameter_km,
            "orbital_period_days": self.orbital_period_days,
            "description": self.description,
            "image_url": self.image_url,
        }

class Favorite(db.Model):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "character_id", name="uq_user_character_fav"),
        UniqueConstraint("user_id", "planet_id", name="uq_user_planet_fav"),
        CheckConstraint(
            "(character_id IS NOT NULL AND planet_id IS NULL) OR "
            "(character_id IS NULL AND planet_id IS NOT NULL)",
            name="ck_favorites_exactly_one_ref",
        ),
        Index("ix_fav_user", "user_id"),
        Index("ix_fav_character", "character_id"),
        Index("ix_fav_planet", "planet_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[Optional[int]] = mapped_column(ForeignKey("characters.id", ondelete="CASCADE"))
    planet_id: Mapped[Optional[int]] = mapped_column(ForeignKey("planets.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="favorites")
    character: Mapped[Optional["Character"]] = relationship(back_populates="favorites")
    planet: Mapped[Optional["Planet"]] = relationship(back_populates="favorites")

    def serialize(self) -> Dict[str, Any]:
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        
        if self.character_id:
            result["character"] = self.character.serialize() if self.character else None
        if self.planet_id:
            result["planet"] = self.planet.serialize() if self.planet else None
            
        return result

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id, 
            "title": self.title, 
            "body": self.body, 
            "author_id": self.author_id,
            "author": self.author.serialize() if self.author else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "comments_count": len(self.comments)
        }

class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    author: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments")

    def serialize(self) -> Dict[str, Any]:
        return {
            "id": self.id, 
            "body": self.body, 
            "author_id": self.author_id,
            "author": self.author.serialize() if self.author else None,
            "post_id": self.post_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }