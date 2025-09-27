from typing import List
from app.models import Recipe
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import json

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class RecipeDB(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    ingredients = Column(JSON)  # Store as JSON string
    steps = Column(JSON)  # Store as JSON string
    prepTime = Column(String)
    cookTime = Column(String)
    difficulty = Column(String)
    cuisine = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initial seed data for backward compatibility
initial_recipes: List[Recipe] = [
    Recipe(
        id=1,
        title="Spaghetti Carbonara",
        ingredients=["pasta", "eggs", "bacon", "cheese"],
        steps=["Cook pasta", "Mix eggs", "Combine all"],
        prepTime="10 minutes",
        cookTime="15 minutes",
        difficulty="Medium",
        cuisine="Italian",
    ),
    Recipe(
        id=2,
        title="Chicken Tikka Masala",
        ingredients=["chicken", "tomato", "onion", "garlic"],
        steps=["Marinate chicken", "Cook sauce", "Combine and simmer"],
        prepTime="20 minutes",
        cookTime="30 minutes",
        difficulty="Medium",
        cuisine="Indian",
    ),
]

# Initialize database with seed data if empty
def init_db():
    db = SessionLocal()
    try:
        # Check if recipes table is empty
        if db.query(RecipeDB).count() == 0:
            for recipe in initial_recipes:
                db_recipe = RecipeDB(
                    id=recipe.id,
                    title=recipe.title,
                    ingredients=recipe.ingredients,
                    steps=recipe.steps,
                    prepTime=recipe.prepTime,
                    cookTime=recipe.cookTime,
                    difficulty=recipe.difficulty,
                    cuisine=recipe.cuisine
                )
                db.add(db_recipe)
            db.commit()
    finally:
        db.close()

# Call init_db to ensure database is seeded
init_db()