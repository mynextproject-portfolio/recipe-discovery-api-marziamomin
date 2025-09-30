from pydantic import BaseModel
from typing import List, Optional, Union

class RecipeBase(BaseModel):
    title: str
    ingredients: List[str]
    steps: List[str]
    prepTime: str
    cookTime: str
    difficulty: str
    cuisine: str

class RecipeCreate(RecipeBase):
    pass

class Recipe(RecipeBase):
    id: Union[int, str]  # Can be int for internal recipes or str for external
    source: str = "internal"  # "internal" for local recipes, "mealdb" for external
