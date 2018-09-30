
import os
from bson.objectid import ObjectId
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo

app = Flask(__name__)

# Configuration values for flask_pymongo
# Documentation at http://flask-pymongo.readthedocs.io/en/latest/#configuration

app.secret_key = os.urandom(24) # generate secret key randomly and safely

app.config['MONGO_DBNAME'] = 'rigsdb' 
app.config['MONGO_URI'] = 'mongodb://root:patriot1@ds115613.mlab.com:15613/rigsdb' # os.getenv('MONGO_URI', 'mongodb://localhost') 

mongo = PyMongo(app)


# views

@app.route("/")
def index():
    """ 
        let user login in. 
        if user has already logged in, redirect to dashboard
    """
    
    if "username" in session:
        return redirect(url_for("dash"))

    return render_template("index.html")
    

@app.route("/login", methods=["POST"])
def login():
    users = mongo.db.users
    user = users.find_one({"username": request.form["username"].lower()})
    
    if user:
        session['username'] = request.form['username']
        return redirect(url_for("dash"))
    else:
        # username isnt registered!
        flash('Invalid username!')
        return redirect(url_for("index"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/dash")
def dash():
    users = mongo.db.users.find()
    
    # DEFENSIVE redirecting
    try:
        # there is session but no score has not been defined yet. 
        current_user = mongo.db.users.find_one({"username": session['username']})
    except KeyError:
        # no session - redirect back to index view
        return redirect( url_for("index"))

    return render_template("dash.html", users = users, logged_in_user=current_user)



@app.route("/register", methods=['GET', 'POST'])
def register():
    users = mongo.db.users
    
    if request.method == "POST":
        
        registered_user = users.find_one({"username": request.form["username"].lower()})
        
        # if username entered doesnt already exist in the database
        if registered_user is None:
            newUser = dict()
            newUser["name"] = request.form["first_name"].lower() + " " + request.form["last_name"].lower()
            newUser["username"] = request.form["username"].lower()
            newUser["setup_counts"] = 0 # setup_counts as integer
            newUser["password"] = request.form["username"]
            users.insert_one(newUser)
            return redirect(url_for('index'))
        
        # username is already registered!
        flash('Username already exists!')

        
    return render_template("register.html" )


@app.route("/add_setup")
def add_setup():
    cpus = mongo.db.cpus
    newCpu = {"manufacturer": "amd", "name": "ryzen 5 2600", "cores": 6, "socket": "am4", "price": 149.99}
    cpus.insert_one(newCpu)
    return render_template("addsetup.html", cpus=cpus.find())

if __name__ == '__main__':
    app.run(host=os.environ.get('IP', '127.0.0.1'),
            port=int(os.environ.get('PORT', '8080')),
            debug=True)
