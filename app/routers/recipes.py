from fastapi import APIRouter, HTTPException, Response, status, Query, Depends
from typing import List, Optional
from app.models import Recipe, RecipeCreate
from app.repositories import RecipeRepository, SQLiteRecipeRepository
from app.database import get_db, Session
from app.mealdb_client import MealDBClient

router = APIRouter()


def get_repository(db: Session = Depends(get_db)) -> RecipeRepository:
    """Dependency provider that returns a SQLite repository instance."""
    return SQLiteRecipeRepository(db)

@router.get("/recipes")
async def get_all_recipes(repo: RecipeRepository = Depends(get_repository)):
    return {"recipes": [recipe.model_dump() for recipe in repo.list_recipes()]}

@router.get("/recipes/search")
async def search_recipes(q: Optional[str] = Query(default=None), repo: RecipeRepository = Depends(get_repository)):
    """
    Search for recipes in both internal database and TheMealDB.
    Returns combined results with source field indicating origin.
    """
    if not q or not q.strip():
        return {"recipes": []}
    
    # Search internal recipes
    internal_recipes = repo.search_recipes(q)
    
    # Search external recipes from MealDB
    mealdb_client = MealDBClient()
    external_recipes = mealdb_client.search_recipes(q)
    
    # Combine results
    all_recipes = internal_recipes + external_recipes
    
    # Convert to dict format for JSON response
    matches = [r.model_dump() for r in all_recipes]
    
    return {"recipes": matches}

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int, repo: RecipeRepository = Depends(get_repository)):
    recipe = repo.get_recipe(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.post("/recipes", status_code=status.HTTP_201_CREATED)
async def create_recipe(payload: RecipeCreate, repo: RecipeRepository = Depends(get_repository)):
    return repo.create_recipe(payload)

@router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, payload: RecipeCreate, repo: RecipeRepository = Depends(get_repository)):
    updated = repo.update_recipe(recipe_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated

@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int, repo: RecipeRepository = Depends(get_repository)):
    deleted = repo.delete_recipe(recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
