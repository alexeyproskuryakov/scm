import os
from flask import Flask, request, render_template, jsonify, flash, url_for
from werkzeug.utils import redirect, secure_filename

from scm.db import ReceiptDb
from scm.loader import load

app = Flask(__name__, template_folder='templates', static_folder='static')

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

data_base = ReceiptDb()


def recipe_is_valid(recipe):
    return recipe.get('title') and recipe.get('ingredients') and recipe.get('description')


def process_ingredients(ingredients_str):
    return dict(
        map(
            lambda x: (x.split('=')[0], x.split('=')[1]),
            ingredients_str.split('|')
        )
    )


def parse_ingredients(input):
    return map(
        lambda x: {'name': x[:x.index('-')].strip(), 'value': x[x.index('-'):].strip()},
        input.split(',')
    )


@app.route("/")
def recipes_ok():
    q = request.args.get("q", None)
    recipe_list = data_base.get_receipt_like(q)
    return render_template("main.html", recipes=recipe_list)


@app.route("/update_recipe", methods=['POST'])
def update_recipe():
    title = request.form.get('title')
    try:
        ingredients_value = request.form.get('ingredients')
        ingredients = parse_ingredients(ingredients_value)
    except Exception:
        return jsonify(**{'ok': False, 'error': 'Ingredients field value %s is not valid' % ingredients_value})

    description = request.form.get('description')
    decorating = request.form.get('decorating')
    if title and ingredients and description:
        save_result = data_base.save_receipt(
            {'title': title, 'description': description, 'ingredients': ingredients, 'decorating': decorating})
        return jsonify(**{'ok': True, 'updated': save_result.modified_count})

    return jsonify(**{'ok': False, 'error': 'Needed some fields value.'})


@app.route('/upload_recipes', methods=['POST'])
def upload_recipes():
    # check if the post request has the file part
    if 'cocktails_file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['cocktails_file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and file.filename:
        bad_recipes = []
        try:
            for recipe in load(file):
                if recipe_is_valid(recipe):
                    data_base.save_receipt(recipe)
                else:
                    bad_recipes.append(recipe)
            return render_template("main.html", bad_recipes=bad_recipes)
        except Exception as e:
            print e
            flash('Some error: %s' % e.message)
            return redirect(url_for('recipes_ok'))


@app.route("/clean")
def clean_recipes_list():
    result = data_base.clean_recipes()
    return jsonify(**{'ok': result.deleted_count != 0})


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.run(port=7777, debug=True)
