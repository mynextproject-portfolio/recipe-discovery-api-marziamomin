import requests
import re
from typing import List, Optional, Dict, Any
from app.models import Recipe


class MealDBClient:
    """Client for interacting with TheMealDB API."""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def search_meals_by_name(self, meal_name: str) -> List[Dict[str, Any]]:
        """
        Search for meals by name using TheMealDB API.
        
        Args:
            meal_name: The name of the meal to search for
            
        Returns:
            List of meal data dictionaries from TheMealDB API
        """
        if not meal_name or not meal_name.strip():
            return []
            
        try:
            url = f"{self.BASE_URL}/search.php"
            params = {"s": meal_name.strip()}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # TheMealDB returns {"meals": [...]} or {"meals": null}
            meals = data.get("meals", [])
            return meals if meals else []
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching meals from MealDB: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error in MealDB search: {e}")
            return []
    
    def _extract_ingredients_and_measures(self, meal_data: Dict[str, Any]) -> List[str]:
        """
        Extract ingredients and measures from MealDB meal data.
        
        Args:
            meal_data: Raw meal data from TheMealDB API
            
        Returns:
            List of formatted ingredient strings with measures
        """
        ingredients = []
        
        for i in range(1, 21):  # TheMealDB has up to 20 ingredients
            ingredient_key = f"strIngredient{i}"
            measure_key = f"strMeasure{i}"
            
            ingredient = meal_data.get(ingredient_key, "") or ""
            measure = meal_data.get(measure_key, "") or ""
            
            # Strip whitespace and skip empty ingredients
            ingredient = ingredient.strip()
            measure = measure.strip()
            
            if not ingredient:
                continue
                
            # Format ingredient with measure
            if measure:
                ingredients.append(f"{measure} {ingredient}")
            else:
                ingredients.append(ingredient)
                
        return ingredients
    
    def _clean_instructions(self, instructions: str) -> List[str]:
        """
        Clean and split instructions into steps.
        
        Args:
            instructions: Raw instructions string from TheMealDB
            
        Returns:
            List of instruction steps
        """
        if not instructions:
            return []
            
        # Clean up the instructions text
        cleaned = re.sub(r'\r\n', ' ', instructions)  # Replace line breaks
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
        cleaned = cleaned.strip()
        
        # Split by sentences or numbered steps
        # Look for common patterns like "1.", "2.", or sentence endings
        steps = []
        
        # Try to split by numbered steps first
        numbered_steps = re.split(r'\s+(?=\d+\.)', cleaned)
        if len(numbered_steps) > 1:
            for step in numbered_steps:
                step = re.sub(r'^\d+\.\s*', '', step).strip()  # Remove number prefix
                if step:
                    steps.append(step)
        else:
            # Fall back to sentence splitting
            sentences = re.split(r'[.!?]+', cleaned)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Filter out very short fragments
                    steps.append(sentence)
        
        # If we still don't have good steps, just return the cleaned text as one step
        if not steps:
            steps = [cleaned] if cleaned else []
            
        return steps
    
    def convert_mealdb_to_recipe(self, meal_data: Dict[str, Any]) -> Recipe:
        """
        Convert TheMealDB meal data to our Recipe model.
        
        Args:
            meal_data: Raw meal data from TheMealDB API
            
        Returns:
            Recipe object with standardized format
        """
        # Extract basic information
        title = meal_data.get("strMeal", "Unknown Recipe")
        category = meal_data.get("strCategory", "Unknown")
        area = meal_data.get("strArea", "Unknown")
        instructions = meal_data.get("strInstructions", "")
        
        # Convert ingredients and measures
        ingredients = self._extract_ingredients_and_measures(meal_data)
        
        # Convert instructions to steps
        steps = self._clean_instructions(instructions)
        
        # Map category/area to cuisine
        cuisine = area if area != "Unknown" else category
        
        # For MealDB recipes, we'll use string IDs and provide defaults for missing fields
        recipe_id = meal_data.get("idMeal", "unknown")
        
        return Recipe(
            id=recipe_id,
            title=title,
            ingredients=ingredients,
            steps=steps,
            prepTime="Not specified",  # MealDB doesn't provide prep time
            cookTime="Not specified",  # MealDB doesn't provide cook time
            difficulty="Not specified",  # MealDB doesn't provide difficulty
            cuisine=cuisine,
            source="mealdb"
        )
    
    def search_recipes(self, query: Optional[str]) -> List[Recipe]:
        """
        Search for recipes in TheMealDB and convert to our Recipe format.
        
        Args:
            query: Search query string
            
        Returns:
            List of Recipe objects from TheMealDB
        """
        if not query or not query.strip():
            return []
            
        # Search TheMealDB
        meal_data_list = self.search_meals_by_name(query)
        
        # Convert to Recipe objects
        recipes = []
        for meal_data in meal_data_list:
            try:
                recipe = self.convert_mealdb_to_recipe(meal_data)
                recipes.append(recipe)
            except Exception as e:
                print(f"Error converting MealDB recipe: {e}")
                continue
                
        return recipes
