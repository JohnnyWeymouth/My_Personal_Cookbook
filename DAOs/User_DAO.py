from DAOs.GetConnection import get_db_connection
from Models.User import User

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