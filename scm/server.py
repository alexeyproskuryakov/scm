# coding=utf-8
import os
from flask import Flask, request, render_template, jsonify, flash, url_for
from werkzeug.utils import redirect, secure_filename

from scm import RECIPE_ID
from scm.db import ReceiptDb
from scm.loader import load

app = Flask(__name__, template_folder='templates', static_folder='static')

# aга, вот сюда будем сохранять... /папка текущего файла/static/img
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'img', 'cocktails')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
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
        lambda x: {'name': x[:x.index('-')].strip(), 'value': x[x.index('-') + 1:].strip()},
        filter(lambda x: x, input.split(','))
    )


@app.route("/")
def recipes_ok():
    q = request.args.get("q", None)
    if q:
        recipe_list = data_base.get_recipe_like(q)
    else:
        recipe_list = list(data_base.get_all_recipes())

    bad_recipe_ids = data_base.get_invalid_recipe_ids()

    return render_template("main.html", recipes=recipe_list, bad_receipe_ids=bad_recipe_ids)


@app.route("/update_recipe", methods=['POST'])
def update_recipe():
    title = request.form.get('title')
    ingredients_value = request.form.get('ingredients')
    try:
        ingredients = parse_ingredients(ingredients_value)
    except Exception:
        return jsonify(**{'ok': False, 'error': 'Ingredients field value %s is not valid' % ingredients_value})

    description = request.form.get('description')
    decorating = request.form.get('decorating')

    # вот тут значит вся магия: recipe_id будет равен тому что из формы. Но если, это говно пустоте (None, '', 0, [], {}, (), ) то берем сгенерированный.
    recipe_id = request.form.get('recipe_id') or RECIPE_ID(title, description, ingredients)
    if title and ingredients and description:
        save_result = data_base.save_recipe(
            {'title': title, 'description': description, 'ingredients': ingredients, 'decorating': decorating,
             'recipe_id': recipe_id})
        return jsonify(**{'ok': True, 'updated': save_result.modified_count})

    return jsonify(**{'ok': False, 'error': 'Needed some fields value.'})


@app.route('/upload_recipes', methods=['POST'])
def upload_recipes():
    # check if the post request has the file part
    if 'cocktails_file' not in request.files:
        flash('No file part')
        return redirect(url_for('recipes_ok'))
    file = request.files['cocktails_file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('recipes_ok'))
    if file and file.filename:
        bad_recipes = []
        try:
            for recipe in load(file):
                if not recipe_is_valid(recipe):
                    recipe['invalid'] = True

                data_base.save_recipe(recipe)

            return redirect(url_for('recipes_ok'))
        except Exception as e:
            print e
            flash('Some error: %s' % e.message)
            return redirect(url_for('recipes_ok'))


# тут, значитца проверяем, копируем картинку-с и возвращаем имя файла в статике
@app.route('/set_image', methods=['POST'])
def set_image():
    if 'file_img' not in request.files:
        return jsonify(**{'ok': False, 'error': 'No file'})
    file = request.files['file_img']
    if file.filename == '':
        return jsonify(**{'ok': False, 'error': 'No file'})
    if file.filename[-3:] not in ALLOWED_EXTENSIONS:
        return jsonify(**{'ok': False, 'error': 'Bad extension'})
    recipe_id = request.form.get('recipe_id')
    if not recipe_id:
        return jsonify(**{'ok': False, 'error': 'No file'})

    file_name = '%s.%s' % (recipe_id, file.filename[-3:])
    dest_file_name = os.path.join(UPLOAD_FOLDER, file_name)
    if file and file.filename:
        file.save(dest_file_name)

    data_base.update_recipe(recipe_id, {'img': file_name})
    return jsonify(**{'ok': True, 'result': file_name})


@app.route("/clean")
def clean_recipes_list():
    result = data_base.clean_recipes()
    return jsonify(**{'ok': result.deleted_count != 0})


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.run(port=7777, debug=True)
