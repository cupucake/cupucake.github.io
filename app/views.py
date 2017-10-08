from flask import render_template
from app import app

@app.route('/')
def index():
	return render_template("index.htm")

@app.route('/Daphne', methods=['POST'])
def indent():
	print("cal")
