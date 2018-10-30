
import os
from dbconfig import db_name, db_uri # capitalise
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
        new_user["admin"] = False
    
    if insert:
        # to avoid duplicate entries
        if users.find_one({"username": new_user["username"]}) is None:
            users.insert_one(new_user)
            # adding username and name to session to be used through out template in navbar of base.html
            session['username'] = new_user["username"]
            session['name'] = request.form["first_name"].lower()
        else:
            duplication_status = "username '{}' already exists!".format(new_user["username"])
        return duplication_status
        
    else:
        return new_user

def get_today_date():
    """ returns the current date in the selectecd format """
    now = datetime.now()
    return now.strftime("%d/%m/%Y")
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




@app.route("/register", methods=['GET', 'POST'])
def register():
    """ attempt to register the user if the user is not already registered! """

    if request.method == "POST":
        # create new user and insert into db
        flash_msg = create_user(insert=True)
        
        if flash_msg == "":
            # Log the new user in upon successfull registration!
            return redirect(url_for('dash'))
        else:
            flash(flash_msg)
        
    return render_template("register.html" )



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
    return render_template("dash.html", vocabs=mongo.db.vocabs.find(), current_user=current_user, user_vocabs_only=False)





@app.route("/get_filtered/<user_id>", methods=['POST'])
def get_filtered(user_id):
    print("i got called!")
    print("user_id = ", user_id)
    user_vocabs_only= False
    
    # current_user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session["username"]})
    except KeyError:
        # no session - redirect back to index view
        return redirect( url_for("index"))
    
    if request.form.to_dict("vocab_only"):
        user_vocabs_only = True
    
        vocabs= list(mongo.db.vocabs.find({"user": current_user["username"]}))
        if len(vocabs) == 0:
            flash("No vocabs found!")
            flash("'{}' has not added any vocabs.".format( current_user["username"].title()))
        
        return render_template("dash.html", vocabs=vocabs, current_user=current_user, user_vocabs_only=user_vocabs_only)
    return redirect( url_for("dash"))
    


@app.route("/manage_sources")
def manage_sources():
    """ render manage_sources page  """
    
    # only go forward if there's a user logged in 
    if "username" in session:
        # if the logged in user is not an admin then bail
        if session["admin"] != True:
            # deny access to "manage_sources" template if user not an admin
            return redirect(url_for("dash"))
        # if admin
        return render_template("manage_sources.html", sources = mongo.db.sources.find() )
    
    # redirect back to index screen if there sint any users logged in   
    return redirect(url_for("dash"))


@app.route("/delete_source/<source_id>")
def delete_source(source_id):
    """   """
    
    # only go forward if there's a user logged in 
    if "username" in session:
        # if the logged in user is not an admin then bail
        if session["admin"] != True:
            # deny access to "manage_sources" template if user not an admin
            return redirect(url_for("dash"))
        
        # if admin
        # fetch source by its id
        source = mongo.db.sources.find_one({'_id': ObjectId(source_id)})
        source_in_use = False
        # check to see if the source is being used!
        vocabs = mongo.db.vocabs.find()
        for vocab in vocabs:
            if vocab["source"] == source["name"]:
                source_in_use = True
        
        # delete source if not in use
        if source_in_use:
            flash("Could NOT delete source '{}' as it is currently in use!".format(source["name"]))
        else:
            flash("Source '{}' was DELETED!".format(source["name"]))
            mongo.db.sources.remove({'_id': ObjectId(source_id)})
        
        return render_template("manage_sources.html", sources = mongo.db.sources.find() )

    
    # redirect back to index screen if there sint any users logged in   
    return redirect(url_for("dash"))


@app.route("/insert_source", methods=["POST"])
def insert_source():
    """ fetch new source and insert into db """
    
    sources = mongo.db.sources
    data = {}
    data["name"] = request.form["new_source"].lower()
    
    # checks  to see if the source already exists!
    if sources.find_one({"name": data["name"]}) is None:
        sources.insert_one(data)
    else:
        # should redirect to the full screen description of the vocab
        flash("Source '{}' already exists!".format(data["name"]))
    
    return redirect( url_for("manage_sources") )


@app.route("/delete_vocab/<vocab_id>")
def delete_vocab(vocab_id):
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Your session has Expired!")
        return redirect( url_for("index"))
    
    # fetch the vocab to be deleted
    to_del_vocab = mongo.db.vocabs.find_one({'_id': ObjectId(vocab_id)})
    
    # remove vocab
    mongo.db.vocabs.remove({'_id': ObjectId(vocab_id)})
    
    # custom flash message as confirmation 
    flash("'{}' was successfully DELETED!".format(to_del_vocab["vocab"]))
    
    return redirect(url_for('dash'))



@app.route("/view_vocab/<vocab_id>")
def view_vocab(vocab_id):
    
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Your session has Expired!")
        return redirect( url_for("index"))    
    
    # vocab view counter

    # fetch the existing vocab out of the db
    vocab = mongo.db.vocabs.find_one({'_id': ObjectId(vocab_id)})

    # get total number views for the vocab
    views = vocab["views"]

    # increment the views 
    views += 1
    
    # update db
    mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "views": views }})
    # mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "mod_date": get_today_date()} })

    return render_template("vocab.html", vocab=vocab, current_user=current_user)





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



@app.route("/insert_vocab", methods=["POST"])
def insert_vocab():
    """ fetch new vocab and insert into db """
    # initialisations
    data = {}
    vocabs = mongo.db.vocabs
    
    
    data["pub_date"] = get_today_date() 
    data["last_lookup_date"] = get_today_date() 
    data["mod_date"] = get_today_date() 
    data["vocab"] = request.form["vocab"].lower()
    data["user_definition"] = request.form["user_definition"].lower()
    data["source"] = request.form.get("source","") # ATTENTION!
    data["context"] = request.form["context"].lower()
    data["misc"] = request.form["misc"].lower()
    data["difficulty"] = int(request.form["difficulty"])
    data["ref"] = request.form["ref"].lower()
    data["user"] = session['username'] # request.form["user_id"] # ?????????????
    data["lookup_count"] = 0
    data["likes"] = 0
    data["views"] = 0
    
    if vocabs.find_one({"vocab": data["vocab"]}) is None:
        # vocab doesnt exist in the db - go ahead and insert
        vocabs.insert_one(data)
        
        # keep track of vocabs added by the the user
        user = mongo.db.users.find_one({"username": data["user"] })  # get user
        vocab_count = user["vocab_count"] # get vocab_count
        vocab_count += 1 # increment the vocab_count 
        user = mongo.db.users.update({"username": data["user"] }, {"$set": {"vocab_count": vocab_count} }) # update db
    else:
        # vocab already exists in the database!
        
        # issue custom flash message
        flash("Vocab '{}' already exists. Lookup count was updated!".format(data["vocab"]))
        
        # fetch the existing vocab out of the db
        vocab = mongo.db.vocabs.find_one({'vocab': data["vocab"] })

        # get lookup_count of the vocab
        lookup_count = vocab["lookup_count"]

        # increment the lookup_count 
        lookup_count += 1
        
        # update db
        mongo.db.vocabs.update({'vocab': data["vocab"]},{ "$set": { "lookup_count": lookup_count, "last_lookup_date": get_today_date()}})
        
        # view the existing vocab by redirecting to view_vocab
        return redirect( url_for("view_vocab", vocab_id=vocab['_id']) )


    return redirect(url_for('dash'))


@app.route("/view_user/<username>")
def view_user(username):
    print("i got called!")

    user=mongo.db.users.find_one({'username': username}) 
    vocabs= list(mongo.db.vocabs.find({"user": username}))
    
    return render_template("view_user.html", user=user,  vocabs=vocabs )



if __name__ == '__main__':
    port = int( os.getenv("PORT") )
    host = os.getenv("IP")
    app.run(host=host, port=port, debug=True)
