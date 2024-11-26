from DAOs.GetConnection import get_db_connection
from Models.PCB_Entry import PCBEntry

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
        pcb_entries = [PCBEntry(user_id=user_id, recipe_id=recipe_id) for user_id, recipe_id in response]
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
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                tup = (user_id, recipe_id)
                cursor.execute(query, tup)
                count = cursor.fetchone()[0]
                return count != 0
