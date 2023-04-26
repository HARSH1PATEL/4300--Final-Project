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
MYSQL_USER_PASSWORD = "gan4646"
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
    # city = query.split("; ")[0]
    # keywords = query.split("; ")[1].split()
    # query_in = f"SELECT * FROM attrs LIMIT 500"
    # like_clauses = []
    # for x in range(len(keywords)):
    #     like_clauses.append(f"LOWER(rev_text) LIKE '%%{keywords[x].lower()}%%'")
    # like_clause_str = ' OR '.join(like_clauses)
    # query_sql_city = query_init + like_clause_str
    query_sql = f"""SELECT * FROM attrs"""
    keys = ["state","attraction","description"]
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys,i)) for i in data])

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

@app.route("/attractions")
def episodes_search():
    query = request.args.get("title")
    response = json.loads(sql_search(query))
    for result in response:
        desc = result['description']
        toks = TreebankWordTokenizer().tokenize(desc)
        result['toks'] = toks
    
    inv_idx = build_inverted_index(response)
    # print(inv_idx)
    idf = compute_idf(inv_idx=inv_idx, n_docs=len(response))
    # print(idf)
    doc_norms = compute_doc_norms(inv_idx, idf, len(response))
    query_words = {}
    for word in TreebankWordTokenizer().tokenize(query):
        if word in query_words:
            query_words[word] += 1
        else:
            query_words[word] = 1
    # print(query_words)
    inv_idx = {key: val for key, val in inv_idx.items() if key in idf}
    # print(inv_idx)
    scores = accumulate_dot_scores(query_words, inv_idx, idf)
    # print(scores)
    results = index_search(query, inv_idx, idf, doc_norms, scores)
    user_results = get_responses_from_results(response, results)
    return user_results

app.run(debug=True)