import os
from dotenv import load_dotenv
import mysql.connector
from Models import User, Recipe, PcbEntry, TryEntry
import json

from flask import Flask, render_template, request, redirect, session

def get_db_connection():
    load_dotenv()
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE")
    )
    return conn

#testing User Authentication
class UserDAO():
    def authenticate_user(self, username, password):
        conn = get_db_connection()  # Create a new database connection
        cursor = conn.cursor()  # Creates a cursor for the connection, you need this to do queries

        with cursor:
            query = """
                SELECT * FROM user WHERE (username = %s OR user_email = %s) AND password_hash = %s
            """
            cursor.execute(query, (username, username, password))
            user_data = cursor.fetchone()
            if user_data:
                user = User(
                    user_id=user_data[0],
                    username=user_data[1],
                    user_email=user_data[2],
                    first_name=user_data[3],
                    last_name=user_data[4],
                    password_hash=user_data[5],
                    date_joined=user_data[6]
                )
                return user
            else:
                return None
    
    def is_username_taken(self, username):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to check if the username exists in the database
        query = "SELECT COUNT(*) FROM user WHERE username = %s"
        cursor.execute(query, (username,))
        
        # Fetch the result
        count = cursor.fetchone()[0]
        
        conn.close()
        
        # If count is greater than 0, username is taken
        return count > 0
    
    def is_email_taken(self, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to check if the email exists in the database
        query = "SELECT COUNT(*) FROM user WHERE user_email = %s"
        cursor.execute(query, (email,))
        
        # Fetch the result
        count = cursor.fetchone()[0]
        
        conn.close()
        
        # If count is greater than 0, email is taken
        return count > 0
    
    def create_user(self, username, email, first_name, last_name, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert the new user into the database
            query = "INSERT INTO user (username, user_email, first_name, last_name, password_hash, date_joined) VALUES (%s, %s, %s, %s, %s, NOW())"
            cursor.execute(query, (username, email, first_name, last_name, password))
            
            # Commit the transaction
            conn.commit()
            
            # Fetch the user ID of the newly inserted user
            user_id = cursor.lastrowid
            
            # Close the database connection
            conn.close()
            
            # Return the user ID
            return user_id
        except Exception as e:
            # Rollback the transaction if an error occurs
            conn.rollback()
            raise e
        
    def delete_user(self, user_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # SQL query to delete the user
            query = "DELETE FROM user WHERE user_id = %s"
            cursor.execute(query, (user_id,))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            return True  # Return True if deletion was successful

        except Exception as e:
            # Handle any errors
            print(f"Error deleting user: {str(e)}")
            return False  # Return False if deletion failed

    def update_email(self, user_id, new_email):
        try:
            conn = get_db_connection()  # Obtain a database connection
            cursor = conn.cursor()

            # Execute SQL query to update the user's email
            query = "UPDATE user SET user_email = %s WHERE user_id = %s"
            cursor.execute(query, (new_email, user_id))
            conn.commit()  # Commit the transaction

            # Close the cursor and connection
            cursor.close()
            conn.close()

            return True  # Return True if update was successful
        except Exception as e:
            print("Error updating email:", e)
            return False  # Return False if update failed
    
    def update_password(self, user_id, new_password):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Update the user's password in the database
            query = "UPDATE user SET password_hash = %s WHERE user_id = %s"
            cursor.execute(query, (new_password, user_id))

            # Commit the transaction
            conn.commit()

            # Close the cursor and connection
            cursor.close()
            conn.close()

            return True  # Return True if update was successful
        except Exception as e:
            # Handle any errors
            print(f"Error updating password: {str(e)}")
            return False  # Return False if update failed


class RecipeDAO():
    def create_recipe(self, recipe_name: str, date_created: str, recipe_image: str, recipe_description: str, instructions: str, tags: str, user_id: int):
        """Creates a new recipe in the database."""
        
        # Check that the arguments are strings
        assert isinstance(recipe_name, str)
        assert isinstance(date_created, str)
        assert isinstance(recipe_image, bytes)
        assert isinstance(recipe_description, str)
        assert isinstance(instructions, str)
        assert isinstance(tags, str)

        # Create a new database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create the query
        query = "INSERT INTO recipe (recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (recipe_name, date_created, recipe_image, recipe_description, instructions, tags, user_id)

        # Execute the query
        cursor.execute(query, values)

        # Commit changes and close connection
        conn.commit()
        conn.close()

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


class TryDAO():
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
        query = "SELECT * FROM to_try_entry WHERE user_id = %s"
        tup = (user_id,)
        cursor.execute(query, tup)

        # Get the response and close the connection
        response = cursor.fetchall()
        conn.close()

        # Convert to PersonalCookBookEntry Model Objects and return
        try_entries = [TryEntry(user_id=user_id, recipe_id=recipe_id) for user_id, recipe_id in response]
        return try_entries
    
    def retrieve_recipe_from_id(self, recipe_id:int): # TODO
        pass
    
    def update_recipe(self): # TODO
        pass

    def delete_recipe(self): # TODO
        pass