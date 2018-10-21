
import os
from dbconfig import db_name, db_uri
from bson.objectid import ObjectId
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from datetime import datetime

# ================================ initial configuration =====================================

app = Flask(__name__) # initiate Flask
app.secret_key = os.urandom(24) # generate secret key randomly and safely
app.config['MONGO_DBNAME'] = db_name # 'vocabdb' # select db
#app.config['MONGO_URI'] = 'mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb' 
# app.config['MONGO_URI'] = os.getenv('MONGO_URI') # RETURNS "None 
# PROBLEM:
#   app.config['MONGO_URI'] = os.getenv('MONGO_URI')  CANNOT BE USED! as it returns None, meaning it hasnt been set up at all!
#   os.getenv('MONGO_URI') keeps returning None! hence cant hide the code
#   even though "export MONGO_URI='mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb'" was set

# mongo = PyMongo(app)
mongo = PyMongo(app, uri=db_uri)
# mongo = PyMongo(app, uri='mongodb://root:patriot1@ds223063.mlab.com:23063/vocabdb')

# ================================== helper functions ========================================

def check_connection():
    """ return users if the connection has been established """
    users = mongo.db.users
    return users

def get_users_count():
    """ count the number of users """
    users = mongo.db.users.find() # .count()
    count = len(list(users)) 
    return count


def get_user_info(username, vocab_count=False, name=False, userId=False):
    """ 
    get given user's:
        - name ................. set name to True
        - vocab count .......... set setup_count to True 
        - id ................... set userId to True 
    """
    
    # get user - should work with userId instead to get username, name and so on!
    user = mongo.db.users.find_one({"username": username})
    
    if name and (not vocab_count) and (not userId):
        output = user["name"]
    elif vocab_count and (not name) and (not userId):
        output = user["vocab_count"]
    elif userId and (not name) and (not vocab_count):
        output = user["_id"]
    else:
        print("get_user_info(): ONLY ONE parameter should be True")
        assert False
    
    return output


def create_user(insert=False, predefined_user=False):
    """ 
    create a new user
        - insert ............ True:   insert new user into db 
                                      - returns err_msg (duplication error message to be used with flash) 
                                      - if err_msg != "", then user already exists in the db
                              False:  return the created user 
                              
        - predefined_user.... True:   for testing purposes - insert a predefined user into db
                                      - returns err_msg (duplication error message to be used with flash) 
                                      - if err_msg != "", then user already exists in the db
    """
    
    duplication_status = ""     # existing user/duplication error message
    users = mongo.db.users      # fetch user collection
    new_user = dict()           # blank dictionary to be populated with new user details
    
    if predefined_user is not False:
        insert = True   # if a predefined user is given, go ahead and insert to db
        new_user = predefined_user
    else: 
        new_user["name"] = request.form["first_name"].lower() + " " + request.form["last_name"].lower()
        new_user["username"] = request.form["username"].lower()
        new_user["vocab_count"] = 0 # setup_counts as integer
        new_user["dob"] = request.form["dob"]
        new_user["sex"] = request.form["sex"].lower()
    
    if insert:
        # to avoid duplicate entries
        if users.find_one({"username": new_user["username"]}) is None:
            users.insert_one(new_user)
        else:
            duplication_status = "username '{}' already exists!".format(new_user["username"])
        return duplication_status
        
    else:
        return new_user
    
# ====================================== views ===============================================

@app.route("/")
def index():
    """ if user has already logged in, redirect to dashboard
    otherwise load index page for the user to login """
    
    if "username" in session:
        return redirect(url_for("dash"))

    return render_template("index.html")
    

@app.route("/login", methods=["POST"])
def login():
    """ attempts to log in the user if the user is registered (record in the database)
    otherwise, redirect back to index (didnt redirect to register since they might have had
    a typo """
    users = mongo.db.users
    user = users.find_one({"username": request.form["username"].lower()})
    
    if user:
        # user found! - log user in
        session['username'] = request.form['username'].lower()
        name = user["name"].split(" ")[0]
        session['name'] = name
        session['admin'] = user["admin"]
        return redirect(url_for("dash"))
    else:
        # user not found! -  Not registered/typo
        flash("Username '{}' is invalid. Please sign up!".format(request.form["username"].lower()))
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    """ clear all session """
    session.clear()
    return redirect(url_for('index'))


@app.route("/dash")
def dash():
    """ the first page the user sees after logging in. 
    shows all setup/users"""

    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        return redirect( url_for("index"))
    
    # user identified
    return render_template("dash.html", users = mongo.db.users.find(), logged_in_user=current_user)



@app.route("/register", methods=['GET', 'POST'])
def register():
    """ attempt to register the user if the user is not already registered! """
    
    # users = mongo.db.users
    
    if request.method == "POST":
        # create new user and insert into db
        flash_msg = create_user(insert=True)
        
        if flash_msg == "":
            # Log the new user in upon successfull registration!
            session['username'] = request.form['username'].lower()
            return redirect(url_for('dash'))
        else:
            flash(flash_msg)
        
    return render_template("register.html" )


@app.route("/add_vocab")
def add_vocab():
    """ render add_vocab page """
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))
    
    
    return render_template("add_vocab.html", sources = mongo.db.sources.find())


@app.route("/add_source")
def add_source():
    print("I GOT CALLED!!!!!!!!!!")
    return render_template("add_source.html", sources = mongo.db.sources.find())


@app.route("/insert_vocab", methods=["POST"])
def insert_vocab():
    """ fetch new vocab and insert into db """
    # initialisations
    now = datetime.now()
    data = {}
    vocabs = mongo.db.vocabs
    
    
    
    print("request.form = ", request.form)
    print("tags", request.form["tags"]) # ?????????????????????
    data["pub_date"] = now.strftime("%d/%m/%Y")
    data["vocab"] = request.form["vocab"].lower()
    data["user_definition"] = request.form["user_definition"].lower()
    data["context"] = request.form["context"].lower()
    data["difficulty"] = int(request.form["difficulty"])
    data["ref"] = request.form["ref"].lower()
    data["misc"] = request.form["misc"].lower()
    data["source"] = request.form.get("source","") # ATTENTION!
    data["user_id"] = session['username'] # request.form["user_id"] # ?????????????
    data["lookup_count"] = 0
    data["likes"] = 0
    data["comments"] = []
    
    if vocabs.find_one({"vocab": data["vocab"]}) is None:
        vocabs.insert_one(data)
    else:
        # EXPAND ON THIS! - page with dates and definition must be loaded
        # should redurect to the full screen description of the vocab
        flash("Vocab '{}' already exists!".format(data["vocab"]))
        return redirect( url_for("add_vocab") )
        
    print("data = ", data)
    return redirect(url_for('dash'))

if __name__ == '__main__':
    port = int( os.getenv("PORT") )
    host = os.getenv("IP")
    app.run(host=host, port=port, debug=True)
