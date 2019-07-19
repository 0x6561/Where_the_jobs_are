from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from flask import jsonify 

app = Flask(__name__)
app._static_folder = '/home/me/email/static'
title = "D3 Map"
heading = "d3 maps"

@app.route('/')
def index():
    return render_template('jobs.html')
