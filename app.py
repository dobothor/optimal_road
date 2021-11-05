import os
import sys
import json
from flask import Flask, render_template, request, redirect, url_for
import requests
import base64
import re
from io import BytesIO, StringIO
import numpy as np
from PIL import Image
from itertools import *
from igraph import *
#https://stackoverflow.com/questions/41957490/send-canvas-image-data-uint8clampedarray-to-flask-server-via-ajax
#https://www.abeautifulsite.net/posts/postjson-for-jquery/

def to_i(y, x):
    return y * 50 + x

def to_coord(index):
    return int((index- index % 50) / 50), index % 50

r = .1

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
        
#@csrf.exempt
@app.route('/savep', methods=['GET','POST'])
def savep():
    image_b64 = request.values['imageBase64']
    print(len(image_b64))
    print(image_b64)
    #print(type(image_b64))
    image_b64 = image_b64[22:]  #image comes encoded with beginning 'data:image/png;base64,'    #[22:]
    #print(image_b64)
    image_PIL = Image.open(StringIO(base64.b64decode(image_b64)))
    img = image_PIL.resize((50,50), Image.ANTIALIAS)
    imn = np.array(img)
    imn0 = np.array(img)
    print("analyze image...")
    lim = [list(j[0:3]) for i in imn for j in i]
    lim0 = [list(j[0:3]) for i in imn0 for j in i] 
    print(lim[0:100])
    print(set(tuple(i) for i in lim))
    print(lim0[0:100])
    print(set(tuple(i) for i in lim0))
    width = len(imn[0])
    height = len(imn)
    edg=[]
    dire = list(product([0,1,-1],[0,1,-1]))
    for i in range(len(lim)):
        for y_dif, x_dif in dire:
            coord = to_coord(i)
            if coord[0] < 1 or coord[1] < 1 or coord[0] == height-1 or coord[1] == width-1 :
                continue
            #g.add_edge(i,to_i(List[i][0]+x_dif,List[i][1]+y_dif),weight=1)
            if abs(y_dif+x_dif) == 1:
                diag = 1
            else:
                diag = (1+1)**.5
            if lim[i]==[255,255,255]:
                edg.append( (i, to_i(coord[0]+x_dif,coord[1]+y_dif), 1*diag) )
            else:
                edg.append( (i, to_i(coord[0]+x_dif,coord[1]+y_dif), r*diag) )

    G = Graph.TupleList(edg, weights=True)
    weight = G.es['weight']     #check if shortest_paths produces smaller pkl
    dist = G.shortest_paths_dijkstra(weights=weight)

    dist_list = [y for x in dist for y in x]
    roads = [0 if i==[255,255,255] else 1 for i in lim]
    
    print("calculate score...")
    score = round( (22.6*len(lim)**2-sum(dist_list))/sum(dist_list)*100 - 1*sum(roads), 1)
    print("dist_list --",sum(dist_list), "-- roads --",sum(roads))
    print("Score --", score)
    
    print("upload image with name to imbgg...")
    apiKey = '4bf38efcff4ef3ef2f5557ddf69e6a6c'
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": apiKey,
        "image": image_b64,
        "name": str(score),
    }
    res = requests.post(url,payload)
    print("done")
    #print("Image received:",(image_np.shape))
    
    
    return "nothing"  #render_template("paint.html") #render_template("save.html", files = files )
    
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
