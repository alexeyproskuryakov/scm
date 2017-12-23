from flask import Flask
app = Flask(__name__, template_folder='/templates', static_folder='/static')

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.run(port=7777, host='0.0.0.0')
