from fastapi import APIRouter, HTTPException, Response, status, Query
from typing import List, Optional
from app.models import Recipe, RecipeCreate
from app.database import recipes, next_id

router = APIRouter()

@router.get("/recipes")
async def get_all_recipes():
    return {"recipes": [recipe.model_dump() for recipe in recipes]}

@router.get("/recipes/search")
async def search_recipes(q: Optional[str] = Query(default=None)):
    if not q:
        return {"recipes": []}
    q_lower = q.lower()
    matches = [
        r.model_dump() for r in recipes 
        if q_lower in r.title.lower()    
    ]
    return {"recipes": matches}

@router.get("/recipes/{recipe_id}")
async def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe.id == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")

@router.post("/recipes", status_code=status.HTTP_201_CREATED)
async def create_recipe(payload: RecipeCreate):
    global next_id
    new_recipe = Recipe(id=next_id, **payload.model_dump())
    recipes.append(new_recipe)
    next_id += 1
    return new_recipe

@router.put("/recipes/{recipe_id}")
async def update_recipe(recipe_id: int, payload: RecipeCreate):
    for index, recipe in enumerate(recipes):
        if recipe.id == recipe_id:
            updated = Recipe(id=recipe_id, **payload.model_dump())
            recipes[index] = updated
            return updated
    raise HTTPException(status_code=404, detail="Recipe not found")

@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(recipe_id: int):
    for index, recipe in enumerate(recipes):
        if recipe.id == recipe_id:
            del recipes[index]
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail="Recipe not found")
