import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from DAOs import RecipeDAO, PcbDAO, UserDAO, TryDAO
from Models import Recipe
from datetime import datetime
from functools import wraps

# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET')

# Custom decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        return f(*args, **kwargs)
    return decorated_function

# Home page
@app.route('/', methods=['GET'])
@login_required # TODO switch to using cookie instead of user id
def home():
    # Access the Personal Cookbook entries that match the user_id
    pcb_entry_list = PcbDAO().retrieve_entries_by_user(session['user_id'])

    # Access each recipe_id for every Personal Cookbook Entry  
    recipe_ids = [pcb_entry.recipe_id for pcb_entry in pcb_entry_list]

    # Access each recipe for every recipe_id
    recipe_list = []
    for id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(id)
        recipe_list.append(recipe)

    # Render the page with all the recipes
    return render_template('my_personal_cookbook.html', items=recipe_list)

# Recipe page that can dynamically display different recipes
@app.route('/recipe')
def recipe_page():
    recipe_id = request.args.get('recipe_id', type=int)
    if recipe_id:
        dao = RecipeDAO()
        recipe = dao.retrieve_recipe_by_id(recipe_id)
        if recipe:
            return render_template('recipe.html', recipe=recipe)
        else:
            return 'Recipe not found', 404
    else:
        return 'Invalid recipe ID', 400
    
# Routes to add recipe to either cookbook or to try list
@app.route('/add_to_personal_cookbook', methods=['POST'])
def add_to_personal_cookbook():
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = request.form.get('user_id', type=int)
    if recipe_id and user_id:
        dao = PcbDAO()
        if dao.add_new_entry(user_id, recipe_id):
            flash('Recipe added to your cookbook.')
        else:
            flash('Recipe already in your cookbook.')
        return redirect('/')
    else:
        return 'Invalid input', 400

@app.route('/add_to_try_list', methods=['POST'])
def add_to_try_list():
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = request.form.get('user_id', type=int)
    if recipe_id and user_id:
        dao = TryDAO()
        if dao.add_new_entry(user_id, recipe_id):
            flash('Recipe added to your try list.')
        else:
            flash('Recipe already in your try list.')
        return redirect('/try_recipes')
    else:
        return 'Invalid input', 400

# Try Recipe page
@app.route('/try_recipes', methods=['GET'])
def try_recipes():

    try_entry_list = TryDAO().retrieve_entries_by_user(1) # TODO Remove the hardcoded user id of 1
    recipe_ids = [try_entry.recipe_id for try_entry in try_entry_list]
    recipe_list = []
    for id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(id)
        recipe_list.append(recipe)
    return render_template('try_recipes.html', items=recipe_list) # Return the page to be rendered


# Search Request
@app.route('/search', methods=['GET'])
@login_required
def search():
    # Get items from the request args in the url
    recipe_name = request.args.get('recipe_name')
    description = request.args.get('description')

    # Render the page if there are no arguments
    if (recipe_name is None) and (description is None):
        return render_template('search.html')

    # Make the search
    recipes = RecipeDAO().retrieve_recipes_from_search(recipe_name, description)
    
    # Return the matching items
    return render_template('search.html', items=recipes)

# ME page Request
@app.route('/me', methods=['GET'])
@login_required
def me():
    # Return the matching items
    return render_template('me.html')

# Create Recipe Request
@app.route('/create_recipe', methods=['GET', 'POST'])
def create_recipe():
    # If the request method is GET, simply render the create_recipe template
    if request.method == 'GET':
        return render_template('create_recipe.html')
    
    # If the request method is POST, take the data and add it to the db
    elif request.method == 'POST':
        # Get image bytes
        recipe_image = request.files['recipe_image']
        try:
            image_blob = recipe_image.read()
            if len(image_blob) > 15.5 * 1024 * 1024: raise ValueError('Image size exceeds 16 MB')
        except:
            image_blob = None

        # Get the tags
        tags = request.form['tags']

        user_id = 1 # TODO remove hardcoding

        # Insert recipe data into the database
        RecipeDAO().create_recipe(
            request.form['recipe_name'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            image_blob,
            request.form['recipe_description'],
            request.form['instructions'],
            tags,
            user_id
        )

        # Send message to page
        flash('Recipe created successfully', 'success')

        # Redirect to home
        return redirect(url_for('home'))
    
# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get Request
    if request.method == 'GET':
        return render_template('login.html')

    # Post Request
    if request.method == 'POST':
        # Get the request data
        username = request.form.get('username')
        password = request.form.get('password')

        # Validate the request data
        if not all(isinstance(var, str) for var in [username, password]):
            flash('Bad request', 'error')
            return redirect('/login')
        
        # Check if username/email and password are valid
        user = UserDAO().authenticate_user(username, password)
        
        if user:
            # Store user ID and email in session
            # TODO store the rest of the variables too later!
            session['user_id'] = user.user_id
            session['email'] = user.user_email
            session['username'] = user.username
            
            # Redirect to user profile page
            return redirect('/me')
        else:
            error_message = 'Invalid username/email or password'
            return render_template('login.html', error_message=error_message)

@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Get Request
    if request.method == 'GET':
        return render_template('register.html')

    # Post Request
    if request.method == 'POST':
        # Access the and validate the user submitted data
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        if not all(isinstance(var, str) for var in [username, email, first_name, last_name, password]):
            flash('Bad request', 'error')
            return redirect('/register')

        # Try to register
        user_id = UserDAO().create_user(username, email, first_name, last_name, password)

        # If the registration failed, add an error message
        if not user_id:
            flash('Failed to create account', 'error')
            return redirect('/register')

        # Store the username in the session
        session['user_id'] = user_id
        session['email'] = email
        session['username'] = username
        flash('Account created successfully', 'success')
        return redirect('/me')
    
# Delete Account Page TODO change to authenticate user with their password as well
@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    # Get Request
    if request.method == 'GET':
        return render_template('delete_account.html')
    
    # Post Request
    if request.method == 'POST':
        # Try to delete the user
        success = UserDAO().delete_user(user_id=session['user_id'])

        # If successful, clear the session and redirect to register
        if success:
            flash('Account deleted', 'success')
            session.clear()
            return redirect('/register.html')
        # Otherwise, redirect to the me page
        else:
            flash('Failed to delete account', 'error')
            return redirect('/me')
    
# Change Email Page TODO change to use cookie instead of user_id
@app.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    # Get Request
    if request.method == 'GET':
        return render_template('change_email.html')
    
    # Post Request
    if request.method == 'POST':
        # Access the and validate the user submitted data
        new_email = request.form.get('new_email')
        if not isinstance(new_email, str):
            flash('Bad request', 'error')
            return render_template('login.html')

        # Update the user's email in the database
        success = UserDAO().update_email(user_id=session['user_id'], new_email=new_email)

        # If successful, clear the session and go to home
        if success:
            flash('Email updated successfully', 'success')
            session['email'] = new_email
        # Otherwise, redirect to the me page
        else:
            flash('Failed to update email', 'error')

        # Redirect to the me page
        return render_template('me.html')

# Change Password Page TODO change to use cookie instead of user_id
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Get Request
    if request.method == 'GET':
        return render_template('change_password.html')
    
    # Post Request
    if request.method == 'POST':
        # Access and validate the user submitted data
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if not all(isinstance(var, str) for var in [current_password, new_password]):
            flash('Bad request', 'error')
            return render_template('login.html')
        
        # Authenticate the user
        user = UserDAO().authenticate_user(user_id=session['username'], password=current_password)

        # If the current password does not match the session user, flash a warning and render
        if not user:
            flash('Incorrect current password', 'error')
            return render_template('change_password.html')
        
        # Try to update the user password and load the me page
        success = UserDAO().update_password(user_id=session['username'], new_password=new_password)
        if success:
            flash('Password updated successfully', 'success')
        else:
            flash('Failed to update password', 'error')
        return render_template('me.html')

# listen on port 8080
if __name__ == '__main__':
    app.run(port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
