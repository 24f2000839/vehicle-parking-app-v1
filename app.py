from flask import Flask, render_template

app = Flask(_name_)

@app.route('/')
def home():
    return "Vehicle parkign app launched"

if _name_ == '_main_':
    app.run(debug=True)
