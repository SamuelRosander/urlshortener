from flask import Flask

app = Flask(__name__)

print("Hello, console!")

@app.route('/')
def index():
    return "Hello, web!"

app.run(host='0.0.0.0')