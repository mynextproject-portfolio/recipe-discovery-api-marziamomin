from typing import List, Protocol, Optional
from app.models import Recipe, RecipeCreate


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


