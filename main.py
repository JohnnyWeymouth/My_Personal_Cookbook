import os
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
from DAOs import RecipeDAO, PcbDAO, TryDAO
from Models import Recipe
from datetime import datetime
import base64


# Load environment variables from .env file
load_dotenv()

# Initialize the flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET")


# Home page
@app.route("/", methods=["GET"])
def home():
    # TODO add check if the user is logged in and redirect them to login/register page if not

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


# listen on port 8080
if __name__ == "__main__":
    app.run(port=8080, debug=True) # TODO: Students PLEASE remove debug=True when you deploy this for production!!!!!
