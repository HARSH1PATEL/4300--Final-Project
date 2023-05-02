import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from nltk.tokenize import TreebankWordTokenizer
from cosine_similarity import *

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
MYSQL_USER = "root"
MYSQL_USER_PASSWORD = "mishakka"
MYSQL_PORT = 3306
MYSQL_DATABASE = "data"

mysql_engine = MySQLDatabaseHandler(MYSQL_USER,MYSQL_USER_PASSWORD,MYSQL_PORT,MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded, 
# but if you decide to use SQLAlchemy ORM framework, 
# there's a much better and cleaner way to do this
# Dictionary ={1:'Welcome', 2:'to',
#             3:'Geeks', 4:'for',
#             5:'Geeks'}
def sql_search(query):
    query_sql = f"""SELECT * FROM attrs"""
    keys = ["state_name","attr_name","desc_text", "rating", "thumbs"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/attractions")
def episodes_search():
    query = request.args.get("title")
    response = json.loads(sql_search(query))
    rating_dict = {}
    thumbs_dict = {}
    response_arr = []

    for i in range(len(response)):
        result = response[i]
        desc = result['desc_text']
       
        toks = TreebankWordTokenizer().tokenize(desc)
        result['toks'] = toks
        rating_dict[i] = result['rating']
        thumbs_dict[i] = result['thumbs']
        response_arr.append(result)
    
    inv_idx = build_inverted_index(response)
 
    idf = compute_idf(inv_idx=inv_idx, n_docs=len(response))

    doc_norms = compute_doc_norms(inv_idx, idf, len(response))
    query_words = {}
    for word in TreebankWordTokenizer().tokenize(query):
        if word in query_words:
            query_words[word] += 1
        else:
            query_words[word] = 1

    inv_idx = {key: val for key, val in inv_idx.items() if key in idf}

    scores = accumulate_dot_scores(query_words, inv_idx, idf)
    results = index_search(query, inv_idx, idf, doc_norms, scores, rating_dict, thumbs_dict)
    for i in results:
        score = i[0]
        id = i[1]
        
        response[id]['cosine'] = score
    user_results = get_responses_from_results(response, results)
    return user_results

@app.route("/thumbsUp",methods=["POST"])
def tUP():
    attrac = request.get_json().get("attrac","error")
    query_sql = f"""UPDATE attrs SET thumbs=2*thumbs WHERE attr_name='{attrac}'"""
    mysql_engine.query_executor(query_sql)
    return "Complete",200

@app.route("/thumbsDown",methods=["POST"])
def tDown():
    attrac = request.get_json().get("attrac","error")
    query_sql = f"""UPDATE attrs SET thumbs=0 WHERE attr_name='{attrac}'"""
    mysql_engine.query_executor(query_sql)
    return "Complete",200

app.run(debug=True)