import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import recipes, next_id
from app.models import Recipe

# Create test client
client = TestClient(app)

class TestIntegration:
    """Integration tests for Recipe Discovery API"""
    
    def setup_method(self):
        """Reset the recipes list to initial state before each test"""
        global recipes, next_id
        recipes.clear()
        recipes.extend([
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
            )
        ])
        next_id = 3

    def test_ping_endpoint(self):
        """Test GET /ping endpoint"""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.text == '"pong"'

    def test_get_all_recipes(self):
        """Test GET /recipes endpoint"""
        response = client.get("/recipes")
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 2
        assert data["recipes"][0]["title"] == "Spaghetti Carbonara"
        assert data["recipes"][1]["title"] == "Chicken Tikka Masala"

    def test_get_recipe_by_id_success(self):
        """Test GET /recipes/{id} endpoint with valid ID"""
        response = client.get("/recipes/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Spaghetti Carbonara"
        assert data["cuisine"] == "Italian"

    def test_get_recipe_by_id_not_found(self):
        """Test GET /recipes/{id} endpoint with invalid ID"""
        response = client.get("/recipes/999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Recipe not found"

    def test_search_recipes_with_query(self):
        """Test GET /recipes/search endpoint with search query"""
        response = client.get("/recipes/search?q=chicken")
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Chicken Tikka Masala"

    def test_search_recipes_without_query(self):
        """Test GET /recipes/search endpoint without query parameter"""
        response = client.get("/recipes/search")
        assert response.status_code == 200
        data = response.json()
        assert "recipes" in data
        assert len(data["recipes"]) == 0

    def test_search_recipes_case_insensitive(self):
        """Test search functionality is case insensitive"""
        response = client.get("/recipes/search?q=SPAGHETTI")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Spaghetti Carbonara"

    def test_search_recipes_partial_match(self):
        """Test search functionality with partial matches"""
        response = client.get("/recipes/search?q=tikka")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 1
        assert data["recipes"][0]["title"] == "Chicken Tikka Masala"

    def test_search_recipes_no_matches(self):
        """Test search functionality with no matches"""
        response = client.get("/recipes/search?q=nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert len(data["recipes"]) == 0

    def test_create_recipe(self):
        """Test POST /recipes endpoint"""
        new_recipe = {
            "title": "Test Recipe",
            "ingredients": ["ingredient1", "ingredient2"],
            "steps": ["step1", "step2"],
            "prepTime": "5 minutes",
            "cookTime": "10 minutes",
            "difficulty": "Easy",
            "cuisine": "Test"
        }
        
        response = client.post("/recipes", json=new_recipe)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 3  # next_id should be 3
        assert data["title"] == "Test Recipe"
        assert data["cuisine"] == "Test"

    def test_create_recipe_invalid_data(self):
        """Test POST /recipes endpoint with invalid data"""
        invalid_recipe = {
            "title": "Test Recipe",
            # Missing required fields
        }
        
        response = client.post("/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    def test_update_recipe_success(self):
        """Test PUT /recipes/{id} endpoint with valid ID"""
        updated_recipe = {
            "title": "Updated Spaghetti Carbonara",
            "ingredients": ["pasta", "eggs", "bacon", "cheese", "parsley"],
            "steps": ["Cook pasta", "Mix eggs", "Combine all", "Garnish"],
            "prepTime": "15 minutes",
            "cookTime": "20 minutes",
            "difficulty": "Hard",
            "cuisine": "Italian"
        }
        
        response = client.put("/recipes/1", json=updated_recipe)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Updated Spaghetti Carbonara"
        assert data["difficulty"] == "Hard"
        assert len(data["ingredients"]) == 5

    def test_update_recipe_not_found(self):
        """Test PUT /recipes/{id} endpoint with invalid ID"""
        updated_recipe = {
            "title": "Updated Recipe",
            "ingredients": ["ingredient1"],
            "steps": ["step1"],
            "prepTime": "5 minutes",
            "cookTime": "10 minutes",
            "difficulty": "Easy",
            "cuisine": "Test"
        }
        
        response = client.put("/recipes/999", json=updated_recipe)
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Recipe not found"

    def test_delete_recipe_success(self):
        """Test DELETE /recipes/{id} endpoint with valid ID"""
        response = client.delete("/recipes/1")
        assert response.status_code == 204
        
        # Verify recipe was deleted
        get_response = client.get("/recipes/1")
        assert get_response.status_code == 404

    def test_delete_recipe_not_found(self):
        """Test DELETE /recipes/{id} endpoint with invalid ID"""
        response = client.delete("/recipes/999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Recipe not found"

    def test_happy_path_crud_cycle(self):
        """Test complete CRUD + search cycle end-to-end"""
        # 1. Create a new recipe
        new_recipe = {
            "title": "Pasta Primavera",
            "ingredients": ["pasta", "vegetables", "olive oil", "garlic"],
            "steps": ["Cook pasta", "Sauté vegetables", "Combine"],
            "prepTime": "15 minutes",
            "cookTime": "20 minutes",
            "difficulty": "Easy",
            "cuisine": "Italian"
        }
        
        create_response = client.post("/recipes", json=new_recipe)
        assert create_response.status_code == 201
        created_recipe = create_response.json()
        recipe_id = created_recipe["id"]
        
        # 2. Get the created recipe
        get_response = client.get(f"/recipes/{recipe_id}")
        assert get_response.status_code == 200
        retrieved_recipe = get_response.json()
        assert retrieved_recipe["title"] == "Pasta Primavera"
        assert retrieved_recipe["cuisine"] == "Italian"
        
        # 3. Search for the recipe
        search_response = client.get("/recipes/search?q=pasta")
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results["recipes"]) >= 1
        found_recipe = next((r for r in search_results["recipes"] if r["id"] == recipe_id), None)
        assert found_recipe is not None
        assert found_recipe["title"] == "Pasta Primavera"
        
        # 4. Update the recipe
        updated_recipe = {
            "title": "Pasta Primavera Deluxe",
            "ingredients": ["pasta", "vegetables", "olive oil", "garlic", "parmesan"],
            "steps": ["Cook pasta", "Sauté vegetables", "Combine", "Add cheese"],
            "prepTime": "20 minutes",
            "cookTime": "25 minutes",
            "difficulty": "Medium",
            "cuisine": "Italian"
        }
        
        update_response = client.put(f"/recipes/{recipe_id}", json=updated_recipe)
        assert update_response.status_code == 200
        updated_recipe_data = update_response.json()
        assert updated_recipe_data["title"] == "Pasta Primavera Deluxe"
        assert updated_recipe_data["difficulty"] == "Medium"
        assert "parmesan" in updated_recipe_data["ingredients"]
        
        # 5. Verify the update by getting the recipe again
        verify_response = client.get(f"/recipes/{recipe_id}")
        assert verify_response.status_code == 200
        verified_recipe = verify_response.json()
        assert verified_recipe["title"] == "Pasta Primavera Deluxe"
        assert verified_recipe["difficulty"] == "Medium"
        assert len(verified_recipe["ingredients"]) == 5
        
        # 6. Search for the updated recipe
        updated_search_response = client.get("/recipes/search?q=deluxe")
        assert updated_search_response.status_code == 200
        updated_search_results = updated_search_response.json()
        found_updated_recipe = next((r for r in updated_search_results["recipes"] if r["id"] == recipe_id), None)
        assert found_updated_recipe is not None
        assert found_updated_recipe["title"] == "Pasta Primavera Deluxe"

    def test_all_endpoints_exist(self):
        """Test that all required endpoints are accessible"""
        # Test all GET endpoints
        assert client.get("/ping").status_code == 200
        assert client.get("/recipes").status_code == 200
        assert client.get("/recipes/1").status_code == 200
        assert client.get("/recipes/search").status_code == 200
        
        # Test POST endpoint
        test_recipe = {
            "title": "Test",
            "ingredients": ["test"],
            "steps": ["test"],
            "prepTime": "1 min",
            "cookTime": "1 min",
            "difficulty": "Easy",
            "cuisine": "Test"
        }
        assert client.post("/recipes", json=test_recipe).status_code == 201
        
        # Test PUT endpoint
        assert client.put("/recipes/1", json=test_recipe).status_code == 200
        
        # Test DELETE endpoint
        assert client.delete("/recipes/1").status_code == 204
