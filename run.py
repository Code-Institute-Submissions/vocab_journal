
import os
import sys 
from py_define import OxDictApi
from bson.objectid import ObjectId
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from datetime import datetime
try:
    import setup_config 
except ImportError:
    # taken from the env
    pass
DB_NAME = os.getenv("DB_NAME")
DB_URI = os.getenv("DB_URI")

# ================================ initial configuration =====================================

app = Flask(__name__)               # initiate Flask
app.secret_key = os.urandom(24)     # generate secret key randomly and safely
app.config['MONGO_DBNAME'] = DB_NAME
mongo = PyMongo(app, uri=DB_URI)

# ================================== helper functions ========================================

def check_connection():
    """ return users if the connection has been established """
    users = mongo.db.users
    return users


def get_users_count():
    """ count the number of users """
    count = mongo.db.users.find().count()
    return count


def get_vocabs_count():
    """ count the number of vocabs """
    count = mongo.db.vocabs.find().count()
    return count


def get_sources_count():
    """ count the number of sources """
    count = mongo.db.sources.find().count()
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
        new_user["name"] = request.form["first_name"].lower().strip() + " " + request.form["last_name"].lower().strip()
        new_user["username"] = request.form["username"].lower().replace(" ", "")  # no spaces in usernames
        new_user["vocab_count"] = 0 # setup_counts as integer
        new_user["dob"] = request.form["dob"]
        new_user["admin"] = False
        new_user["likes"] = []
        
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
    return now.strftime("%Y/%m/%d")
    
    
def process_likes(vocab):
    """ check to see if user has already liked the vocab if the vocab is already liked 
    by the user, then dislike (retract the like)"""
    
    # fetch db data
    users = mongo.db.users
    vocabs = mongo.db.vocabs
    
    # find the current user
    user = users.find_one({"username": session['username']})
    
    # get the list of the vocabs the user has liked!
    all_likes = user["likes"]
    
    liked_before = False    # initialising flag
    if vocab["vocab"] in all_likes:
        liked_before = True

    if liked_before:
        # if already liked, go ahead and retract the like 
        users.update({"username": session['username']}, { "$pull": { "likes": vocab["vocab"] }})
        vocabs.update({"vocab": vocab["vocab"] }, { "$inc": { "likes": -1 }})
    else:
        # add the vocab to the user likes list, and increment vocab likes
        users.update({"username": session['username']}, { "$push": { "likes": vocab["vocab"] }})
        vocabs.update({"vocab": vocab["vocab"] }, { "$inc": { "likes": 1 }})


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
    """ attempts to log the user in, if the user is registered (record in the database), 
    redirect back to index (didnt redirect to register since they might have had a typo """
    
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
    """ attempts to register the user if the user is not already registered! """

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
    """ logs user out by clearing all session """
    session.clear()
    return redirect(url_for('index'))


@app.route("/dash")
def dash():
    """ the first page the user sees after logging in. 
    shows all vocabs in the db."""

    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        return redirect( url_for("index"))

    # dictionary created for the sole purpose of saving the filter settings upon selections
    filter_options = {}
    filter_options["user_vocabs_only"] =  False
    filter_options["order_by"] =  {"views": False, "lookup count": True, "likes": False, "difficulty": False, "publish date": False, "modified date": False  }
    filter_options["order"] =  { "descending": True, "ascending": False }
    filter_options["source"] =  ""
    
    # user identified
    return render_template("dash.html", vocabs=mongo.db.vocabs.find(), sources=mongo.db.sources.find(), current_user=current_user, filter_options=filter_options)


@app.route("/get_filtered")
def get_filtered():
    """ Apply filters to vocabs
        vocab filters:
            toggle between vocabs added by user and ALL vocabs in db.
            show vocabs asigned to a specific source.
        sort by:
            views, lookup count, likes, difficulty, publish date, modified date
        order:
            ascending, descending.
        """
    
    jdebug = 0  # debugging flag

    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session["username"]})
    except KeyError:
        # no session - redirect back to index view
        return redirect( url_for("index"))
    
    # dictionary allows saving of the filter settings upon 
    # selections and sorting of the vocabs screened through the filter.  
    filter_options = {}
    filter_options["user_vocabs_only"] =  False
    filter_options["order_by"] =  {"views": False, "lookup count": True, "likes": False, "difficulty": False, "publish date": False, "modified date": False }
    filter_options["order"] =  { "descending": True, "ascending": False }
    filter_options["source"] =  ""

    # "filter_dict" is used as a normal dictionary containing only two vocabs, "source" and "user" which will
    # ultimately limit the numbers of vocabs show on the screen and nothing else.  "filter_options" wasnt used here because of its
    # complexity which cannot be used with mongodb's .find() feature which requires a simple key, value structure. 
    filter_dict = {} 
    
    # Setting up filter logic
    if request.args.get("source"):
        filter_dict["source"] = filter_options["source"] = request.args.get("source")   # updating filter options 
    if request.args.get("vocab_only"):
        filter_options["user_vocabs_only"] = True   # updating filter options 
        filter_dict["user"] = current_user["username"]
    
    # Applying filters - will affect the quanity of the returning vocabs only at this level.
    vocabs = mongo.db.vocabs.find(filter_dict)

    # Setting up "order" logic to sort the returned vocabs!
    order_by = request.args.get("order_by")
    for k in filter_options["order_by"]:
        # updating filter options 
        if order_by == k:
            filter_options["order_by"][k] = True
        else:
            filter_options["order_by"][k] = False
    

    # readjusting sorting data before passing it into db (entities listed below are stored differently in db)
    # entities were changed since they're being used to populate the "select" inputs within the filter options
    # of the dash.
    if order_by == "lookup count":
        order_by = "lookup_count"
    elif order_by == "publish date":
        order_by = "pub_date"
    elif order_by == "modified date":
        order_by = "mod_date"
    else:
        pass

    # Applying sorts
    if request.args.get("order") == "ascending":
        # updating filter options 
        filter_options["order"]["ascending"] = True
        filter_options["order"]["descending"] = False
        vocabs.sort(order_by, 1) 
    else:
        # updating filter options 
        filter_options["order"]["ascending"] = False
        filter_options["order"]["descending"] = True
        vocabs.sort(order_by, -1) 
    
    # Custom flash msg for no results 
    if vocabs.count() == 0:
        flash("No vocabs found!")
        # custom flash msg for user not having added any vocabs
        if mongo.db.vocabs.find({"user": current_user["username"]}).count() == 0:
            flash("'{}' has not added any vocabs.".format( current_user["username"].title()))
    
    # Debug
    if jdebug > 0:
        print("filter_options = ", filter_options)
        print("filter_dict = ", filter_dict)
        print("vocabs.count()  = ", vocabs.count() )
      
    return render_template("dash.html", vocabs=vocabs, sources=mongo.db.sources.find(), current_user=current_user, filter_options=filter_options)

    


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
    """ ADMIN ONLY! - delete a source from the db
    NOTE: sources in use CANNOT BE DELETED BY DESIGN!
    check to see if the logged in user is an admin.
    if not an admin, redirect back to dash.
    if admin, check to see if the source is already in use
    by any vocabs within the db.
    if so, fetch the vocabs, push to template along the custom
    flash message.
    if source not in use, then go ahead and remove from db.
    """
    
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
            # fetch vocabs using this specific source!
            vocabs = list(mongo.db.vocabs.find({"source": source["name"]}) ) # to be passed into the template with custom flash msg.
            # custom message to let the user know that the source he/she wished to delete is currently in use!
            flash("Could NOT delete source '{}' as it is currently in used by the following vocabs!".format(source["name"]))
        else:
            flash("Source '{}' was successfully DELETED!".format(source["name"])) # custom flash message to confirm deletion.
            mongo.db.sources.remove({'_id': ObjectId(source_id)}) # remove source after locating it by its id "source_id"
        
        return render_template("manage_sources.html", sources = mongo.db.sources.find(), vocabs=vocabs )

    
    # redirect back to index screen if there sint any users logged in   
    return redirect(url_for("dash"))


@app.route("/insert_source", methods=["POST"])
def insert_source():
    """ ADMIN ONLY! - creates a new source.
        fetch new source from the input off the screen. 
        insert into db if it DOESNT  already exist! """

    sources = mongo.db.sources
    data = {}
    data["name"] = request.form["new_source"].lower().strip()

    # checks  to see if the source already exists!
    if sources.find_one({"name": data["name"]}) is None:
        sources.insert_one(data)
    else:
        # should redirect to the full screen description of the vocab
        flash("Source '{}' already exists!".format(data["name"]))
    
    return redirect( url_for("manage_sources") )


@app.route("/delete_vocab/<vocab_id>")
def delete_vocab(vocab_id):
    """ attempts to remove a vocab from the database.
    get vocab to be deleted via its id "vocab_id".
    remove vocab from db.
    update "vocabs_count" of the user it was added by.
    remove vocab from the liked(favourited) list of users."""
    
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
    
    # update user vocab_count 
    vocabs_count =  mongo.db.vocabs.find({"user": to_del_vocab["user"]}).count() # count the remaining vocabs added by the user
    mongo.db.users.update({'username': to_del_vocab["user"]}, { "$set": { "vocab_count": vocabs_count }})
    
    # update likes for users
    mongo.db.users.update({ "likes": {"$in": [ to_del_vocab["vocab"] ] } }, { "$pull": { "likes": to_del_vocab["vocab"] }}, upsert=False, multi=True )

    # custom flash message as confirmation 
    flash("'{}' was successfully DELETED!".format( to_del_vocab["vocab"].title() ))
    
    return redirect(url_for('dash'))



@app.route("/view_vocab/<vocab_id>")
def view_vocab(vocab_id):
    """" view a vocab details using the dedicated vocab template.
    get vocab through its "vocab_id" and view it full screen in a 
    dedicated template "vocab.html".
    update vocab view count!"""
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Your session has Expired!")
        return redirect( url_for("index"))    
    
    # vocab view counter
    mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$inc": { "views": 1 }})
    
    # fetch the existing vocab out of the db
    vocab = mongo.db.vocabs.find_one({'_id': ObjectId(vocab_id)})

    return render_template("vocab.html", vocab=vocab, current_user=current_user)


@app.route("/user_likes/<vocab>")
def user_likes(vocab):
    """" alternative version of "view_vocab" created as a fudge factor to
        handle the favourite vocabs of the user within the view_user template, 
        since user liked vocabs are just a list of strings(vocabs).
        also allows the removal of the view buttons since the vocabs are
        now links."""
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Your session has Expired!")
        return redirect( url_for("index"))    
    
    # identify vocab
    vocab = mongo.db.vocabs.find_one({'vocab': vocab})
    
    # get vocab _id and redurect to view_vocab
    return redirect( url_for("view_vocab", vocab_id=vocab["_id"]) )



@app.route("/check_vocab")
def check_vocab():
    """ render check_vocab template """
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))
        
    return render_template("check_vocab.html")


@app.route("/add_vocab", methods=["POST"])
def add_vocab():
    """ checks to see the vocabs already exists.ArithmeticError
        if the vocab exists, it will load the vocab and update its lookup_count
        otherwise, it runs the vocab through the API for definitions, synonyms and examples."""
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))
    
    vocab_in = request.form.get("vocab").lower().strip()

    # if the vocab already exists then load its page with maybe the definintion
    if mongo.db.vocabs.find_one({"vocab": vocab_in}) is not None:    
        # issue custom flash message
        flash("Vocab '{}' already exists. Lookup count was updated!".format(vocab_in))
        
        # fetch the existing vocab out of the db
        vocab = mongo.db.vocabs.find_one({'vocab': vocab_in })  # fetch the existing vocab out of the db

        # update db
        mongo.db.vocabs.update({'vocab': vocab_in}, {"$inc": { "lookup_count": 1 } })
        mongo.db.vocabs.update({'vocab': vocab_in}, { "$set": {"last_lookup_date": get_today_date()} })
                
        # view the existing vocab by redirecting to view_vocab
        return redirect( url_for("view_vocab", vocab_id=vocab['_id']) )

    ###############################  DEFINITION EXTRACTION (API) ################################################
    # instantiate class with vocab_in
    local_dictionary = OxDictApi(vocab_in)
    
    # using our instance's 3 methods:
    #   get_definitions():  to extract vocab "definitions"
    #      get_synonyms():  to extract vocab "synonyms"
    #      get_examples():  to extract vocab "examples"
    def_stat, def_data = local_dictionary.get_definitions()     # get definitions
    syn_stat, syn_data = local_dictionary.get_synonyms()        # get synonyms
    exa_stat, exa_data = local_dictionary.get_examples()        # get examples
    
    # merge all extracted data into one object
    data = {"definitions": def_data, "synonyms": syn_data, "examples": exa_data }

    return render_template("add_vocab.html", sources = mongo.db.sources.find(), vocab=vocab_in.lower(), data=data )



@app.route("/insert_vocab/<vocab>", methods=["POST"])
def insert_vocab(vocab):
    """ fetch new vocab off the screen from the form and insert into db
        update user vocab_count."""
    
    # initialisations
    data = {}
    vocabs = mongo.db.vocabs
    
    # fetch from form
    data["tags"] = request.form.get("tags") 
    data["pub_date"] = get_today_date() 
    data["last_lookup_date"] = get_today_date() 
    data["mod_date"] = get_today_date() 
    data["vocab"] = vocab 
    data["user_definition"] = request.form["user_definition"].lower()
    data["source"] = request.form.get("source") 
    data["context"] = request.form["context"].lower()
    data["misc"] = request.form["misc"].lower()
    data["difficulty"] = int(request.form["difficulty"])
    data["ref"] = request.form["ref"].lower()
    data["user"] = session['username'] 
    data["lookup_count"] = 0
    data["likes"] = 0
    data["views"] = 1
    
    # insert data
    vocabs.insert_one(data)
        
    # keep track of vocabs added by the the user - update user vocab_count 
    user = mongo.db.users.find_one({"username": data["user"]})
    vocabs_count =  mongo.db.vocabs.find({"user": data["user"]}).count()
    mongo.db.users.update({'username': data["user"]}, { "$set": { "vocab_count": vocabs_count }})
    
    flash("'{}' was successfully ADDED!".format(vocab.title()))
    
    return redirect(url_for('dash'))


@app.route("/edit_vocab/<vocab_id>")
def edit_vocab(vocab_id):
    """ render the edit_vocab template for the vocab with id "vocab_id" """
    
    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))
    
    # show all the vocab details on the screen
    vocab = mongo.db.vocabs.find_one({'_id': ObjectId(vocab_id)})
    sources = mongo.db.sources.find()

    return render_template("edit_vocab.html", vocab=vocab, sources=sources, current_user=current_user)
    # the submit should pass everything to the update_vocab
    
    

@app.route("/update_vocab/<vocab_id>", methods=["POST"])
def update_vocab(vocab_id):
    """ update the vocab in the db if any changes made! """
    
    # fetch vocab
    vocab = mongo.db.vocabs.find_one({'_id': ObjectId(vocab_id)})
    
    change_flag = False   # flag to indicate a change was made!
    track_change = { "user_definition": False,"source": False,"context": False,
                    "misc": False,"difficulty": False,"ref": False, "tags": False }
    
    # fetch items from the from and update "track_change" if a change was made
    if request.form.get("user_definition") != vocab["user_definition"]:
        track_change["user_definition"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "user_definition": request.form.get("user_definition") } })
    
    if request.form.get("source") != vocab["source"]:
        track_change["source"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "source": request.form.get("source") } })
    
    if request.form.get("context") != vocab["context"]:
        track_change["context"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "context": request.form.get("context") } })
    
    if request.form.get("misc") != vocab["misc"]:
        track_change["misc"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "misc": request.form.get("misc") } })
    
    if request.form.get("difficulty") != vocab["difficulty"]:
        track_change["difficulty"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "difficulty": request.form.get("difficulty") } })
    
    if request.form.get("ref") != vocab["ref"]:
        track_change["ref"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "ref": request.form.get("ref") } })
        
    if request.form.get("tags") != vocab["tags"]:
        track_change["tags"] = True
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "tags": request.form.get("tags") } })
    
    # check to see a changed was made, if so set flag to True
    for k,v in  track_change.items():
        if v:
            change_flag = True
    
    # update db if there was a change - also, update the modified time.
    if change_flag:
        mongo.db.vocabs.update({'_id': ObjectId(vocab_id)}, { "$set": { "mod_date": get_today_date()} })
        flash( "'{}' vocab was successfully MODIFIED!".format(vocab["vocab"].title()) )
    else:
        flash( "No changes were made to '{}' vocab!".format(vocab["vocab"].title() ) )
        
    return redirect( url_for('dash') )



@app.route("/view_user/<username>")
def view_user(username):
    """ render user profile template "view_user" """

    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))

    user=mongo.db.users.find_one({'username': username}) 
    vocabs= list(mongo.db.vocabs.find({"user": username}))
    
    return render_template("view_user.html", user=user,  vocabs=vocabs )


@app.route("/toggle_like/<vocab>")
def toggle_like(vocab):
    """ Apply like to the vocab - on view_vocab template only!
        if the vocab is already liked! then retract.
        logic from "process_likes" function """

    # DEFENSIVE redirecting
    try:
        # identify the logged in user 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        flash("Please log in first")
        return redirect( url_for("index"))

    vocab = mongo.db.vocabs.find_one({"vocab": vocab})
    
    # if vocab is already liked by user, then dislike
    process_likes( vocab )
    
    return redirect( url_for("view_vocab", vocab_id=vocab["_id"] ) )

@app.route("/access_api/<item>/<vocab_in>")
def access_api(item, vocab_in):
    
    print("vocab_in = ", vocab_in)
    print("item = ", item)
    
    # instantiate class with vocab_in
    local_dictionary = OxDictApi(vocab_in)
    
    
    
    exa_stat, exa_data = local_dictionary.get_examples()        # get examples
    
    outt = ""
    
    if item.upper() == "DEFS":
        def_stat, def_data = local_dictionary.get_definitions()     # get definitions
        def_data_list = list(def_data.keys())[0]
        outt += '<span class="card-title">Definitions</span>'
        for key in def_data:
            if key == def_data_list[0]:
                outt += "<p><strong>{}</strong><p>\n".format(key)
            else:
                outt += "<br><p><strong>{}</strong><p>\n".format(key)
            for x in range(len(def_data[key])):
                if x < 7:
                    defs = def_data[key][x].encode("utf-8")
                    outt += "{})&nbsp; {}<br>".format(x+1, defs)
                
    if item.upper() == "SYNS":
        syn_stat, syn_data = local_dictionary.get_synonyms()        # get synonyms
        syn_data_list = list(syn_data.keys())[0]
        outt += '<span class="card-title">Synonyms</span>'
        for key in syn_data:
            if key == syn_data_list[0]:
                outt += "<p><strong>{}</strong><p>\n".format(key)
            else:
                outt += "<br><p><strong>{}</strong><p>\n".format(key)
            for x in range(len(syn_data[key])):
                if x < 7:
                    syns = syn_data[key][x].encode("utf-8")
                    outt += "{})&nbsp; {}<br>".format(x+1, syns)  
                    
    if item.upper() == "EXAMS":
        exa_stat, exa_data = local_dictionary.get_examples()        # get examples
        exa_data_list = list(exa_data.keys())[0]
        outt += '<span class="card-title">Examples</span>'
        for key in exa_data:
            if key == exa_data_list[0]:
                outt += "<p><strong>{}</strong><p>\n".format(key)
            else:
                outt += "<br><p><strong>{}</strong><p>\n".format(key)
            for x in range(len(exa_data[key])):
                if x < 7:
                    exams = exa_data[key][x].encode("utf-8")
                    outt += "{})&nbsp; {}<br>".format(x+1, exams)
            
    return outt


if __name__ == '__main__':
    port = int( os.getenv("PORT") )
    host = os.getenv("IP")
    app.run(host=host, port=port, debug=True)
