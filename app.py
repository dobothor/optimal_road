import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for
import requests
import base64
import re
from io import StringIO
import numpy as np
from PIL import Image

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def paintapp():
    if request.method == 'GET':
        return render_template("paint.html")
    if request.method == 'POST':
        filename = request.form['save_fname']
        data = request.form['save_cdata']
        canvas_image = request.form['save_image']
        conn = psycopg2.connect(database="paintmyown", user = "nidhin")
        cur = conn.cursor()
        cur.execute("INSERT INTO files (name, data, canvas_image) VALUES (%s, %s, %s)", [filename, data, canvas_image])
        conn.commit()
        conn.close()
        return redirect(url_for('save'))        
        
        
@app.route('/savep', methods=['POST'])
def savep():
    #conn = psycopg2.connect(database="paintmyown", user="nidhin")
    #cur = conn.cursor()
    #cur.execute("SELECT id, name, data, canvas_image from files")
    #files = cur.fetchall()
    #conn.close()
    
    #g = Github(login_or_token="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") 
    #repo = g.get_user("dobothor").get_repo("optimal_road")
    #content = "Hello Web!"
    #repo.create_file("images/text3.txt","commiting files", content)
    print("Hello!")
    image_b64 = request.values['imageBase64']
    #image_data = re.sub(
    image_PIL = Image.open(cStringIO.StringIO(image_b64))
    image_np = np.array(image_PIL)
    print("Image received:",(image_np.shape))
    return "nothing" #render_template("save.html", files = files )
    
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template("search.html")
    if request.method == 'POST':
        filename = request.form['fname']
        conn = psycopg2.connect(database="paintmyown", user="nidhin")
        cur = conn.cursor()
        cur.execute("select id, name, data, canvas_image from files")
        files = cur.fetchall()
        conn.close()
        return render_template("search.html", files=files, filename=filename)
    
if __name__ == '__main__':
    #port = int(os.environ.get('PORT', 5000))
    app.run(threaded=True, port=5000,debug=True)
