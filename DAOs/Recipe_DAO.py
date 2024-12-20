import json

from DAOs.GetConnection import get_db_connection
from Models.Recipe import Recipe

class RecipeDAO():
    def create_recipe(self, recipe_name:str, date_created:str, recipe_image:str, recipe_description:str, instructions:str, tags:str, user_id:int) -> str:
        """Creates a new recipe in the database."""
        # Create a new database connection and cursor using a context manager
        with get_db_connection() as conn, conn.cursor() as cursor:
            # Create the query with placeholders
            query = """
            INSERT INTO recipe 
            (recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Execute the query with the data
            tup = (recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id)
            cursor.execute(query, tup)
            
            # Commit changes
            conn.commit()
            
            # Get the recipe_id of the last inserted row
            recipe_id = cursor.lastrowid
            
            # Return the recipe_id
            return str(recipe_id)

    def retrieve_recipes_from_search(self, recipe_name:str, recipe_description:str, tags:list[str]) -> list[Recipe]:
        """Retrieves recipes matching the search criteria including tags.\n        
        returns: A list of recipes"""
        # Validate input
        try:
            assert isinstance(recipe_name, str)
            assert isinstance(recipe_description, str)
            assert isinstance(tags, list)
            assert len(recipe_name) <= 255
            assert len(recipe_description) <= 3000
            assert len(str(tags)) <= 255
            assert all(isinstance(item, str) for item in tags)
        except:
            return []

        # Create a new database connection and cursor using a context manager
        with get_db_connection() as conn, conn.cursor() as cursor:

            # Build the query dynamically based on provided inputs (but not including them)
            query = "SELECT * FROM recipe WHERE 1=1"
            params = []
            if recipe_name:
                query += " AND recipe_name LIKE %s"
                params.append('%' + recipe_name + '%')
            if recipe_description:
                query += " AND recipe_description LIKE %s"
                params.append('%' + recipe_description + '%')
            cursor.execute(query, params)
            response = cursor.fetchall()
            conn.close()

            # Convert to Recipe Model Objects
            recipe_list = [self._convert_data_to_recipe__(recipe_data) for recipe_data in response]
            
            # Remove the recipes that do not have the same tags
            recipe_list = [recipe for recipe in recipe_list if all(tag in recipe.tags for tag in tags)]

            # Return the matching recipes, if any
            return recipe_list
    
    def retrieve_recipe_by_id(self, recipe_id:int) -> Recipe:
        """Retrieves the recipe that matches the recipe_id.\n        
        returns: A list of recipes"""

        # Check that the search arguments are strings
        assert isinstance(recipe_id, int)

        # Create a new database connection and cursor using a context manager
        with get_db_connection() as conn, conn.cursor() as cursor:

            # Create the query
            query = "SELECT * FROM recipe WHERE recipe_id = %s"
            tup = (recipe_id,)
            cursor.execute(query, tup)

            # Get the response and close the connection
            response = cursor.fetchall()
            conn.close()

            # Convert to a Recipe Model Object and return
            recipe = self._convert_data_to_recipe__(response[0])
            return recipe

    def retrieve_recipes_by_author(self, user_id:int): # TODO
        pass
    
    def update_recipe(self, recipe_id:int): # TODO
        pass

    def delete_recipe(self, recipe_id:int): # TODO
        pass

    def _convert_data_to_recipe__(self, recipe_data:tuple) -> Recipe:
        recipe_id, recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id = recipe_data
        tags =  json.loads(tags)
        recipe = Recipe(
            recipe_id = recipe_id,
            recipe_name = recipe_name,
            date_created = date_created,
            recipe_image = recipe_image,
            recipe_description = recipe_description,
            instructions = instructions,
            tags = tags,
            user_id = user_id
        )
        return recipe