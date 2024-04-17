import os
from dotenv import load_dotenv
import mysql.connector
from Models import User, Recipe, PcbEntry, TryEntry
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

#testing User Authentication
class UserDAO():
    def authenticate_user(self, username, password):
        # Establish the connection
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            query = "SELECT * FROM user WHERE (username = %s OR user_email = %s) AND password_hash = %s"
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
            
        except Exception as e:
            # Rollback the transaction if an error occurs
            conn.rollback()
            raise e
    
    def is_username_taken(self, username):
        # Establish the connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to check if the username exists in the database
        query = "SELECT COUNT(*) FROM user WHERE username = %s"
        tup = (username,)
        cursor.execute(query, tup)
        
        # Fetch the result
        count = cursor.fetchone()[0]
        
        # Close the connection
        conn.close()
        
        # If count is greater than 0, username is taken
        return count > 0
    
    def is_email_taken(self, email:str):
        # Validate the args
        if not isinstance(email, str):
            return False

        # Establish the connection
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
    
    def create_user(self, username:str, email:str, first_name:str, last_name:str, password:str):
        # Establish the connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username or email already exists in the database
        if (self.is_username_taken(username)) or (self.is_email_taken(email)):
            return None 
        
        try:
            # Insert the new user into the database
            query = "INSERT INTO user (username, user_email, first_name, last_name, password_hash, date_joined) VALUES (%s, %s, %s, %s, %s, NOW())"
            tup = (username, email, first_name, last_name, password)
            cursor.execute(query, tup)
            
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
        # Establish the database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Try to delete the user
        try:
            # SQL query to delete the user
            query = "DELETE FROM user WHERE user_id = %s"
            cursor.execute(query, (user_id,))

            # Commit the transaction
            conn.commit()

            # Return True only after a successful commit
            return True

        # Handle exceptions
        except Exception as e:
            print(f"Error deleting user: {str(e)}")
            conn.rollback()  # Rollback the transaction
            return False

        # Close the cursor and connection
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


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
    def create_recipe(self, recipe_name: str, date_created: str, recipe_image: str, recipe_description: str, instructions: str, tags: str, user_id: int) -> str:
        """Creates a new recipe in the database."""
        # Create a new database connection using a context manager
        with get_db_connection() as conn:
            # Create a cursor using a context manager
            with conn.cursor() as cursor:
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


    def retrieve_recipes_from_search(self, recipe_name: str, recipe_description: str, tags: list) -> list:
        """Retrieves recipes matching the search criteria including tags.\n        
        returns: A list of recipes"""

        conn = get_db_connection()
        cursor = conn.cursor()

        # Start building the query dynamically based on provided inputs
        query = "SELECT * FROM recipe WHERE 1=1"
        params = []

        if recipe_name:
            query += " AND recipe_name LIKE %s"
            params.append('%' + recipe_name + '%')

        if recipe_description:
            query += " AND recipe_description LIKE %s"
            params.append('%' + recipe_description + '%')

        if tags:
            # Adjust the following based on your database's capabilities to handle JSON
            # For MySQL, use JSON_CONTAINS or similar
            # For PostgreSQL, use the containment operator @> for JSONB fields
            tag_conditions = " OR ".join(["JSON_CONTAINS(tags, '\"%s\"')" % tag for tag in tags])
            query += " AND (" + tag_conditions + ")"

        cursor.execute(query, params)
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
    
    def add_new_entry(self, user_id, recipe_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor(buffered=True)  # Use a buffered cursor

            # Check if the entry already exists
            query = "SELECT COUNT(*) FROM personal_cookbook_entry WHERE user_id = %s AND recipe_id = %s"
            cursor.execute(query, (user_id, recipe_id))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the entry if it does not exist
                query = "INSERT INTO personal_cookbook_entry (user_id, recipe_id) VALUES (%s, %s)"
                cursor.execute(query, (user_id, recipe_id))

            cursor.close()  # Close the cursor to handle any potential unread results
            conn.commit()  # Now commit the transaction
            return count == 0  # Returns True if the entry was added, False if it was not
        finally:
            conn.close()  # Ensure the connection is closed in case of error

    def delete_recipe(self, user_id, recipe_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM personal_cookbook_entry WHERE user_id = %s AND recipe_id = %s"
            cursor.execute(query, (user_id, recipe_id))
            conn.commit()
            return cursor.rowcount > 0  # Returns True if rows were affected
        except Exception as e:
            print(f"Failed to delete recipe: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def check_if_saved_recipe(self, user_id, recipe_id) -> bool:
        query = "SELECT COUNT(*) FROM personal_cookbook_entry WHERE user_id = %s AND recipe_id = %s"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    tup = (user_id, recipe_id)
                    cursor.execute(query, tup)
                    count = cursor.fetchone()[0]
                    return count != 0
        except mysql.connector.Error as e:
            print(f"Failed to check if saved in personal cookbook: {e}")
            return False

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
    
    def add_new_entry(self, user_id, recipe_id):
        conn = get_db_connection()
        try:
            cursor = conn.cursor(buffered=True)  # Use a buffered cursor

            # Check if the entry already exists
            query = "SELECT COUNT(*) FROM to_try_entry WHERE user_id = %s AND recipe_id = %s"
            cursor.execute(query, (user_id, recipe_id))
            count = cursor.fetchone()[0]

            if count == 0:
                # Insert the entry if it does not exist
                query = "INSERT INTO to_try_entry (user_id, recipe_id) VALUES (%s, %s)"
                cursor.execute(query, (user_id, recipe_id))

            cursor.close()  # Close the cursor to handle any potential unread results
            conn.commit()  # Now commit the transaction
            return count == 0  # Returns True if the entry was added, False if it was not
        finally:
            conn.close()  # Ensure the connection is closed in case of error

    def delete_recipe(self, user_id, recipe_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM to_try_entry WHERE user_id = %s AND recipe_id = %s"
            cursor.execute(query, (user_id, recipe_id))
            conn.commit()
            return cursor.rowcount > 0  # Returns True if rows were affected
        except Exception as e:
            print(f"Failed to delete recipe: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def check_if_saved_recipe(self, user_id, recipe_id) -> bool:
        query = "SELECT COUNT(*) FROM to_try_entry WHERE user_id = %s AND recipe_id = %s"
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    tup = (user_id, recipe_id)
                    cursor.execute(query, tup)
                    count = cursor.fetchone()[0]
                    return count != 0
        except mysql.connector.Error as e:
            print(f"Failed to check if saved in try list: {e}")
            return False