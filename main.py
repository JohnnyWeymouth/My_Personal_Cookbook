import os
import json
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session

from Models.Recipe import Recipe
from DAOs.PCB_DAO import PcbDAO
from DAOs.Recipe_DAO import RecipeDAO
from DAOs.Try_DAO import TryDAO
from DAOs.User_DAO import UserDAO

# Load env and start the flask app
load_dotenv()
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
@login_required
def home():
    # Access the Personal Cookbook entries that match the user_id
    pcb_entry_list = PcbDAO().retrieve_entries_by_user(session['user_id'])

    # Access each recipe_id for every Personal Cookbook Entry
    recipe_ids = [pcb_entry.recipe_id for pcb_entry in pcb_entry_list]

    # Access each recipe, if saved in try_list, and if saved in pcb for every recipe_id
    items = []
    for recipe_id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(recipe_id)
        saved_try = TryDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe_id)
        saved_cb = True
        tup = (recipe, saved_try, saved_cb)
        items.append(tup)

    # Render the page with all the recipes
    return render_template('my_personal_cookbook.html', items=items)

# Try Recipe page
@app.route('/try_recipes', methods=['GET'])
def try_recipes():
    # Access the Try entries that match the user_id
    try_entry_list = TryDAO().retrieve_entries_by_user(session['user_id'])

    # Access each recipe_id for every Personal Cookbook Entry
    recipe_ids = [try_entry.recipe_id for try_entry in try_entry_list]

    # Access each recipe for every recipe_id
    items = []
    for recipe_id in recipe_ids:
        recipe:Recipe = RecipeDAO().retrieve_recipe_by_id(recipe_id)
        saved_try = True
        saved_cb = PcbDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe_id)
        tup = (recipe, saved_try, saved_cb)
        items.append(tup)

    # Render the page with all the recipes
    return render_template('try_recipes.html', items=items)

# Search Request
@app.route('/search', methods=['GET'])
@login_required
def search():
    # Get items from the request args in the URL
    recipe_name = request.args.get('recipe_name', '')
    description = request.args.get('description', '')
    tags = request.args.getlist('tags')  # Gets all selected tags

    # Handle the case where the form is submitted without any criteria
    if not any([isinstance(recipe_name, str) or recipe_name is None,
                isinstance(description, str) or description is None,
                isinstance(tags, list) or tags is None]):
        flash('Please enter search criteria.', 'error')
        return render_template('search.html')

    # Make the search
    recipes:list[Recipe] = RecipeDAO().retrieve_recipes_from_search(recipe_name, description, tags)

    # Check if each recipe is saved in try_list and/or in pcb
    items = []
    for recipe in recipes:
        saved_try = TryDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe.recipe_id)
        saved_cb = PcbDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe.recipe_id)
        tup = (recipe, saved_try, saved_cb)
        items.append(tup)
    
    # Return the matching items
    return render_template('search.html', items=items)

# Recipe page that can dynamically display different recipes
@app.route('/recipe')
def recipe_page():
    recipe_id = request.args.get('recipe_id', type=int)
    if recipe_id:
        recipe = RecipeDAO().retrieve_recipe_by_id(recipe_id)
        if recipe:
            saved_try = TryDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe.recipe_id)
            saved_cb = PcbDAO().check_if_saved_recipe(user_id=session['user_id'], recipe_id=recipe.recipe_id)
            tup = (recipe, saved_try, saved_cb)
            return render_template('recipe.html', item=tup)
        else:
            return 'Recipe not found', 404
    else:
        return 'No recipe ID', 400
    
# Routes to add recipe to either cookbook or to try list
@app.route('/add_to_personal_cookbook', methods=['POST'])
def add_to_personal_cookbook():
    # Access user submitted data
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = request.form.get('user_id', type=int)

    # Attempt to add the new entry
    success = PcbDAO().add_new_entry(user_id, recipe_id)
    if success:
        flash('Recipe added to your cookbook.', 'success')
        TryDAO().delete_recipe(user_id, recipe_id)
    else:
        flash('Recipe already in your cookbook.', 'error')
    
    # Redirect back
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    else:
        return redirect('/')

@app.route('/add_to_try_list', methods=['POST'])
def add_to_try_list():
    # Access user submitted data
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = request.form.get('user_id', type=int)

    # Attempt to add the new entry
    success = TryDAO().add_new_entry(user_id, recipe_id)
    if success:
        flash('Recipe added to your try list.', 'success')
    else:
        flash('Recipe already in your try list.', 'error')

    # Redirect back
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    else:
        return redirect('/try_recipes')
    
# Route to remove a recipe from the personal cookbook    
@app.route('/remove_recipe_from_pcb', methods=['POST'])
@login_required
def remove_recipe_from_pcb():
    # Access user submitted data
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = session.get('user_id')

    # Attempt to remove the recipe
    removed_from_pcb = PcbDAO().delete_recipe(user_id, recipe_id)
    if removed_from_pcb:
        flash('Recipe removed from personal cookbook.', 'success')
    else:
        flash('Error removing recipe from personal cookbook.', 'error')

    # Redirect back
    referer = request.headers.get('Referer')
    if referer:
        return redirect(referer)
    else:
        return redirect('/my_personal_cookbook')

# Route to remove a recipe from the try list
@app.route('/remove_recipe_from_try_list', methods=['POST'])
@login_required
def remove_recipe_from_try_list():
    # Access user submitted data
    recipe_id = request.form.get('recipe_id', type=int)
    user_id = session.get('user_id')
    referer = request.headers.get('Referer')

    # Attempt to remove the recipe
    success = TryDAO().delete_recipe(user_id, recipe_id)
    if success:
        flash('Recipe removed from try list.', 'success')
    else:
        flash('Error removing recipe from try list.', 'error')

    # Redirect back
    if referer:
        return redirect(referer)
    else:
        return redirect('/my_personal_cookbook')

# ME page Request
@app.route('/me', methods=['GET'])
@login_required
def me():
    # Return the matching items
    return render_template('me.html')

@app.route('/create_recipe', methods=['GET', 'POST'])
@login_required
def create_recipe():
    if request.method == 'GET':
        return render_template('create_recipe.html')
    
    if request.method == 'POST':
        # Get image bytes
        image_file = request.files['recipe_image']
        try:
            image_bytes:bytes = image_file.read()
            if len(image_bytes) > 15.5 * 1024 * 1024:  # 16MB Limit
                raise ValueError('Image size exceeds 16 MB')
        except Exception as e:
            flash(f'Error with image upload: {str(e)}', 'error')
            image_bytes = b''

        # Handle tags
        tags = request.form.getlist('tags')  # Gets a list of checked tags
        tags_json = json.dumps(tags)  # Converts list to JSON string

        # Insert recipe data into the database
        recipe_id = RecipeDAO().create_recipe(
            request.form['recipe_name'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            image_bytes,
            request.form['recipe_description'],
            request.form['instructions'],
            tags_json,
            session['user_id']
        )

        # Add this to that users personal cookbook
        PcbDAO().add_new_entry(user_id=session['user_id'], recipe_id=recipe_id)

        # Send message to page
        flash('Recipe created successfully', 'success')

        # Redirect to home
        return redirect(f'/recipe?recipe_id={recipe_id}')
    
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
    
# Delete Account Page
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
    
# Change Email Page
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

# Change Password Page
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
        user = UserDAO().authenticate_user(session['username'], current_password)

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
    app.run(host='0.0.0.0', port=8080, debug=False)