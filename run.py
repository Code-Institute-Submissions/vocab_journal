
import os
from bson.objectid import ObjectId
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo


# ================================ initial configuration =====================================

app = Flask(__name__) # initiate Flask
app.secret_key = os.urandom(24) # generate secret key randomly and safely
app.config['MONGO_DBNAME'] = 'rigsdb' # select db
#app.config['MONGO_URI'] = 'mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb' 
#app.config['MONGO_URI'] = os.getenv('MONGO_URI') # RETURNS "None 
# PROBLEM:
#   app.config['MONGO_URI'] = os.getenv('MONGO_URI')  CANNOT BE USED! as it returns None, meaning it hasnt been set up at all!
#   os.getenv('MONGO_URI') keeps returning None! hence cant hide the code
#   even though "export MONGO_URI='mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb'" was set

#mongo = PyMongo(app)
mongo = PyMongo(app, uri='mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb')

# ================================== helper functions ========================================

def check_connection():
    """ return users if the connection has been established """
    users = mongo.db.users
    return users

def get_users_count():
    """ count the number of users """
    users = mongo.db.users.find()
    count = len(list(users))
    return count


def get_user_info(username, setup_count=False, name=False, userId=False):
    """ 
    get given user's:
        - name ................. set name to True
        - setup count .......... set setup_count to True 
        - id ................... set userId to True 
    """
    
    # get user
    user = mongo.db.users.find_one({"username": username})
    
    if name and (not setup_count) and (not userId):
        output = user["name"]
    elif setup_count and (not name) and (not userId):
        output = user["setup_count"]
    elif userId and (not name) and (not setup_count):
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
        new_user["setup_count"] = 0 # setup_counts as integer
    
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
        session['username'] = request.form['username']
        return redirect(url_for("dash"))
    else:
        # user not found! -  Not registered/typo
        flash("Username '{}' is invalid!".format(request.form["username"].lower()))
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
    
    users = mongo.db.users
    
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


# @app.route("/add_setup")
# def add_setup():
#     cpus = mongo.db.cpus
#     newCpu = {"manufacturer": "amd", "name": "ryzen 5 2600", "cores": 6, "socket": "am4", "price": 149.99}
#     cpus.insert_one(newCpu)
#     return render_template("addsetup.html", cpus=cpus.find())


if __name__ == '__main__':
    # app.run(host=os.environ.get('IP', '127.0.0.1'),
    #         port=int(os.environ.get('PORT', '8080')),
    #         debug=True)
    port = int( os.getenv("PORT") )
    host = os.getenv("IP")
    app.run(host=host, port=port, debug=True)
