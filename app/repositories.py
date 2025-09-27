from typing import List, Protocol, Optional
from app.models import Recipe, RecipeCreate
from sqlalchemy.orm import Session
from app.database import get_db, RecipeDB


class RecipeRepository(Protocol):
    """Abstraction for recipe data operations."""

    def list_recipes(self) -> List[Recipe]:
        ...

    def search_recipes(self, query: Optional[str]) -> List[Recipe]:
        ...

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        ...

    def create_recipe(self, payload: RecipeCreate) -> Recipe:
        ...

    def update_recipe(self, recipe_id: int, payload: RecipeCreate) -> Optional[Recipe]:
        ...

    def delete_recipe(self, recipe_id: int) -> bool:
        ...


class InMemoryRecipeRepository:
    """In-memory implementation of RecipeRepository suitable for tests and dev.

    Designed so the data source can be swapped later with minimal changes.
    """

    def __init__(self, seed: Optional[List[Recipe]] = None) -> None:
        self._recipes: List[Recipe] = list(seed) if seed else []
        if self._recipes:
            self._next_id: int = max(r.id for r in self._recipes) + 1
        else:
            self._next_id = 1

    def list_recipes(self) -> List[Recipe]:
        return list(self._recipes)

    def search_recipes(self, query: Optional[str]) -> List[Recipe]:
        if not query:
            return []
        q_lower = query.lower()
        return [r for r in self._recipes if q_lower in r.title.lower()]

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        for recipe in self._recipes:
            if recipe.id == recipe_id:
                return recipe
        return None

    def create_recipe(self, payload: RecipeCreate) -> Recipe:
        new_recipe = Recipe(id=self._next_id, **payload.model_dump())
        self._recipes.append(new_recipe)
        self._next_id += 1
        return new_recipe

    def update_recipe(self, recipe_id: int, payload: RecipeCreate) -> Optional[Recipe]:
        for index, recipe in enumerate(self._recipes):
            if recipe.id == recipe_id:
                updated = Recipe(id=recipe_id, **payload.model_dump())
                self._recipes[index] = updated
                return updated
        return None

    def delete_recipe(self, recipe_id: int) -> bool:
        for index, recipe in enumerate(self._recipes):
            if recipe.id == recipe_id:
                del self._recipes[index]
                return True
        return False


class SQLiteRecipeRepository:
    """SQLite implementation of RecipeRepository for persistent storage."""

    def __init__(self, db: Session):
        self.db = db

    def list_recipes(self) -> List[Recipe]:
        db_recipes = self.db.query(RecipeDB).all()
        return [self._db_to_model(recipe) for recipe in db_recipes]

    def search_recipes(self, query: Optional[str]) -> List[Recipe]:
        if not query:
            return []
        q_lower = query.lower()
        db_recipes = self.db.query(RecipeDB).filter(
            RecipeDB.title.ilike(f"%{q_lower}%")
        ).all()
        return [self._db_to_model(recipe) for recipe in db_recipes]

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        db_recipe = self.db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if db_recipe:
            return self._db_to_model(db_recipe)
        return None

    def create_recipe(self, payload: RecipeCreate) -> Recipe:
        # Get the next available ID
        max_id_result = self.db.query(RecipeDB.id).order_by(RecipeDB.id.desc()).first()
        next_id = (max_id_result[0] + 1) if max_id_result else 1
        
        db_recipe = RecipeDB(
            id=next_id,
            title=payload.title,
            ingredients=payload.ingredients,
            steps=payload.steps,
            prepTime=payload.prepTime,
            cookTime=payload.cookTime,
            difficulty=payload.difficulty,
            cuisine=payload.cuisine
        )
        self.db.add(db_recipe)
        self.db.commit()
        self.db.refresh(db_recipe)
        return self._db_to_model(db_recipe)

    def update_recipe(self, recipe_id: int, payload: RecipeCreate) -> Optional[Recipe]:
        db_recipe = self.db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not db_recipe:
            return None
        
        db_recipe.title = payload.title
        db_recipe.ingredients = payload.ingredients
        db_recipe.steps = payload.steps
        db_recipe.prepTime = payload.prepTime
        db_recipe.cookTime = payload.cookTime
        db_recipe.difficulty = payload.difficulty
        db_recipe.cuisine = payload.cuisine
        
        self.db.commit()
        self.db.refresh(db_recipe)
        return self._db_to_model(db_recipe)

    def delete_recipe(self, recipe_id: int) -> bool:
        db_recipe = self.db.query(RecipeDB).filter(RecipeDB.id == recipe_id).first()
        if not db_recipe:
            return False
        
        self.db.delete(db_recipe)
        self.db.commit()
        return True

    def _db_to_model(self, db_recipe: RecipeDB) -> Recipe:
        """Convert database model to Pydantic model."""
        return Recipe(
            id=db_recipe.id,
            title=db_recipe.title,
            ingredients=db_recipe.ingredients,
            steps=db_recipe.steps,
            prepTime=db_recipe.prepTime,
            cookTime=db_recipe.cookTime,
            difficulty=db_recipe.difficulty,
            cuisine=db_recipe.cuisine
        )


