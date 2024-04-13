import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from DAOs import RecipeDAO, PcbDAO, UserDAO
from Models import Recipe
from datetime import datetime
import base64
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")

#Testing the Login page
user_dao = UserDAO()
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username/email and password are valid
        user = user_dao.authenticate_user(username, password)
        
        if user:
            # Store user ID and email in session
            #store the rest of the variables too later!
            session['user_id'] = user.user_id
            session['email'] = user.user_email
            session['username'] = user.username
            
            
            # Redirect to user profile page
            return redirect('/me')
        else:
            error_message = "Invalid username/email or password"
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

# Custom decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        return f(*args, **kwargs)
    return decorated_function

# Home page
@app.route("/", methods=["GET"])
@login_required
def home():
    # TODO add check if the user is logged in and redirect them to login/register page if not
    # Check if user is logged in
    #if 'user_id' not in session:
        # Redirect to login page if not logged in
    #    return redirect('/login')

    #else:
    pcb_entry_list = PcbDAO().retrieve_entries_by_user(1) # TODO Remove the hardcoded user id of 1 AND Pcb stands for Personal Cook Book
    recipe_ids = [pcb_entry.recipe_id for pcb_entry in pcb_entry_list]
    recipe_list = []
    for id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(id)
        recipe_list.append(recipe)
    return render_template("my_personal_cookbook.html", items=recipe_list) # Return the page to be rendered

# Try Recipe page
@app.route("/try_recipes", methods=["GET"])
def try_recipes():

    try_entry_list = TryDAO().retrieve_entries_by_user(1) # TODO Remove the hardcoded user id of 1
    recipe_ids = [try_entry.recipe_id for try_entry in try_entry_list]
    recipe_list = []
    for id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(id)
        recipe_list.append(recipe)
    return render_template("try_recipes.html", items=recipe_list) # Return the page to be rendered


# Search Request
@app.route("/search", methods=["GET"])
@login_required
def search():
    # Get items from the request args in the url
    recipe_name = request.args.get("recipe_name")
    description = request.args.get("description")

    # Render the page if there are no arguments
    if (recipe_name is None) and (description is None):
        return render_template('search.html')

    # Make the search
    recipes = RecipeDAO().retrieve_recipes_from_search(recipe_name, description)
    
    # Return the matching items
    return render_template('search.html', items=recipes)

# ME page Request
@app.route("/me", methods=["GET"])
@login_required
def me():
    # Return the matching items
    return render_template('me.html')

# Create Recipe Request
@app.route("/create_recipe", methods=["GET", "POST"])
def create_recipe():
    # If the request method is GET, simply render the create_recipe template
    if request.method == "GET":
        return render_template('create_recipe.html')
    
    # If the request method is POST, take the data and add it to the db
    elif request.method == "POST":
        # Get image bytes
        recipe_image = request.files["recipe_image"]
        try:
            image_blob = recipe_image.read()
            if len(image_blob) > 15.5 * 1024 * 1024: raise ValueError("Image size exceeds 16 MB")
        except:
            image_blob = None

        # Get the tags
        tags = request.form["tags"]

        user_id = 1 # TODO remove hardcoding

        # Insert recipe data into the database
        RecipeDAO().create_recipe(
            request.form["recipe_name"],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            image_blob,
            request.form["recipe_description"],
            request.form["instructions"],
            tags,
            user_id
        )

        # Send message to page
        flash("Recipe created successfully", "success")

        # Redirect to home
        return redirect(url_for("home"))

# Example of a post request
@app.route("/new-item", methods=["POST"])
@login_required
def add_item():
    try:
        # Get items from the form
        data = request.form
        item_name = data["name"] # This is defined in the input element of the HTML form on index.html
        item_quantity = data["quantity"] # This is defined in the input element of the HTML form on index.html

        # TODO: Insert this data into the database
        
        # Send message to page. There is code in index.html that checks for these messages
        flash("Item added successfully", "success")
        # Redirect to home. This works because the home route is named home in this file
        return redirect(url_for("home"))

    # If an error occurs, this code block will be called
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error") # Send the error message to the web page
        return redirect(url_for("home")) # Redirect to home

@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get registration form data
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        
        # Check if username or email already exists in the database
        if user_dao.is_username_taken(username):
            flash('Username already taken', 'error')
            return redirect('/register')
        if user_dao.is_email_taken(email):
            flash('Email already registered', 'error')
            return redirect('/register')

        # If username and email are available, create a new user
        user_id = user_dao.create_user(username, email, first_name, last_name, password)
        if user_id:
            # Store the username in the session
            session['username'] = username
            flash('Account created successfully', 'success')
            return redirect('/login')
        else:
            flash('Failed to create account', 'error')
            return redirect('/register')
    else:
        return render_template('register.html')
    
# Add the route to handle account deletion
@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        # Get the user_id from the session
        user_id = session.get('user_id')

        # Call the delete_user function
        if user_id:
            if user_dao.delete_user(user_id):
                # Clear the session after successful deletion
                session.clear()
                # Redirect to the home page or a suitable page
                return redirect('/')
            else:
                # Handle deletion failure
                flash('Failed to delete account', 'error')
                return redirect('/me')
        else:
            # Handle case when user is not logged in
            flash('User not logged in', 'error')
            return redirect('/login')
    else:
        # Render the delete account confirmation page
        return render_template('delete_account.html')
    
# Functionality to Change the email
@app.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    if request.method == "POST":
        new_email = request.form.get("new_email")

        # Update the user's email in the database
        user_dao = UserDAO()
        user_id = session["user_id"]
        success = user_dao.update_email(user_id, new_email)

        if success:
            # Update the session variable with the new email
            session["email"] = new_email

            flash("Email updated successfully", "success")
        else:
            flash("Failed to update email", "error")

    return render_template("change_email.html")





# Functionality to Change the password
@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")

        # Authenticate the user
        user_dao = UserDAO()
        user_id = session["user_id"]
        user = user_dao.authenticate_user(session["username"], current_password)

        if user:
            # Update the user's password
            success = user_dao.update_password(user_id, new_password)

            if success:
                flash("Password updated successfully", "success")
            else:
                flash("Failed to update password", "error")
        else:
            flash("Incorrect current password", "error")

    return render_template("change_password.html")






# listen on port 8080
if __name__ == "__main__":
    app.run(port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
