import os
from dotenv import load_dotenv
import mysql.connector
from Models import User, Recipe, PcbEntry
import json

def get_db_connection():
    load_dotenv()
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    return conn

class RecipeDAO():
    def create_recipe(self,): # TODO
        pass

    def retrieve_recipes_from_search(self, recipe_name:str, recipe_description:str) -> list[Recipe]:
        """Retrieves the recipes the matching the search tool's query.\n        
        returns: A list of recipes"""

        # Check that the search arguments are strings
        assert isinstance(recipe_name, str)
        assert isinstance(recipe_description, str)

        # Create a new database connection for each request
        conn = get_db_connection()  # Create a new database connection
        cursor = conn.cursor()  # Creates a cursor for the connection, you need this to do queries

        # Create the query # TODO incorporate tags and make this less messy
        if recipe_description == '':
            query = "SELECT * FROM recipe WHERE recipe_name LIKE %s"
            tup = ('%' + recipe_name + '%',)
            cursor.execute(query, tup)
        elif recipe_name == '':
            query = "SELECT * FROM recipe WHERE recipe_description LIKE %s"
            tup = ('%' + recipe_description + '%',)
            cursor.execute(query, tup)
        elif (recipe_name == '') and (recipe_description == ''):
            cursor.execute("SELECT * FROM recipe where 1 = 0")
        else:
            query = "SELECT * FROM recipe WHERE recipe_name LIKE %s OR recipe_description LIKE %s"
            tup = ('%' + recipe_name + '%', '%' + recipe_description + '%')
            cursor.execute(query, tup)

        # Get the response and close the connection
        response = cursor.fetchall()
        conn.close()

        # Convert to Recipe Model Objects and return
        recipe_list = [self.__convert_data_to_recipe__(recipe_data) for recipe_data in response]
        return recipe_list
    
    def retrieve_recipe_by_id(self, recipe_id:int) -> Recipe:
        """Retrieves the recipe that matches the recipe_id.\n        
        returns: A list of recipes"""

        # Check that the search arguments are strings
        assert isinstance(recipe_id, int)

        # Create a new database connection for each request
        conn = get_db_connection()  # Create a new database connection
        cursor = conn.cursor()  # Creates a cursor for the connection, you need this to do queries

        # Create the query
        query = "SELECT * FROM recipe WHERE recipe_id = %s"
        tup = (recipe_id,)
        cursor.execute(query, tup)

        # Get the response and close the connection
        response = cursor.fetchall()
        conn.close()

        # Convert to a Recipe Model Object and return
        recipe = self.__convert_data_to_recipe__(response[0])
        return recipe

    def retrieve_recipes_by_author(self, user_id:int): # TODO
        pass
    
    def update_recipe(self, recipe_id:int): # TODO
        pass

    def delete_recipe(self, recipe_id:int): # TODO
        pass

    def __convert_data_to_recipe__(self, recipe_data) -> Recipe:
        recipe_id, recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id = recipe_data
        tags =  json.loads(tags)
        recipe = Recipe (
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

class PcbDAO():
    def create_new_entry(self): # TODO
        pass

    def retrieve_entries_by_user(self, user_id:int):
        """Retrieves the entries for a specific user.\n
        returns: A list of recipe_ids"""

        # Check that user_id is an int
        assert isinstance(user_id, int)

        # Create a new database connection for each request
        conn = get_db_connection()  # Create a new database connection
        cursor = conn.cursor()  # Creates a cursor for the connection, you need this to do queries

        # Create the query
        query = "SELECT * FROM personal_cookbook_entry WHERE user_id = %s"
        tup = (user_id,)
        cursor.execute(query, tup)

        # Get the response and close the connection
        response = cursor.fetchall()
        conn.close()

        # Convert to PersonalCookBookEntry Model Objects and return
        pcb_entries = [PcbEntry(user_id=user_id, recipe_id=recipe_id) for user_id, recipe_id in response]
        return pcb_entries
    
    def retrieve_recipe_from_id(self, recipe_id:int): # TODO
        pass
    
    def update_recipe(self): # TODO
        pass

    def delete_recipe(self): # TODO
        pass