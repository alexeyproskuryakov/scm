from flask import Flask, request, render_template, jsonify

from scm.db import ReceiptDb


app = Flask(__name__, template_folder='templates', static_folder='static')
data_base = ReceiptDb()

@app.route("/", methods = ["POST", "GET"])
def recipes_management():
    if request.method == "GET":
        q = request.args.get("q", None)
        recipe_list = data_base.get_receipt_like(q)
        return render_template("main.html", recipes = recipe_list)
    return jsonify(**{'ok':True})

@app.route("/clean")
def clean_recipes_list():
    result = data_base.clean_recipes()
    return jsonify(**{'ok':result.deleted_count != 0})

if __name__ == '__main__':
    app.run(port=7777, host='0.0.0.0')
