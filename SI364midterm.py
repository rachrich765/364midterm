###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, IntegerField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required, Length # Here, too, 
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import re
## App setup code
app = Flask(__name__)
app.debug = True
basedir = os.path.abspath(os.path.dirname(__file__))

## All app.config values


## Statements for db setup (and manager setup if using Manager)
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:4Rocks32@localhost/rachjrMidterm" # TODO: May need to change this, Windows users. Everyone will need to have created a db with exactly this name.
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################

##################
##### MODELS #####
##################

class Name(db.Model):
    __tablename__ = "names"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return "{} (ID: {})".format(self.name, self.id)

class Confusing_Hashtag(db.Model):
    __tablename__ = "confusing_hashtags"
    id = db.Column(db.Integer,primary_key=True)
    hashtag = db.Column(db.String(64))
    user_id = db.Column(db.Integer,db.ForeignKey("confusing_users.id"))

    def __repr__(self):
        return "{}".format(self.hashtag)

class Confusing_User(db.Model):
     __tablename__ = "confusing_users"
     id = db.Column(db.Integer, primary_key=True)
     user = db.Column(db.String(64))
     confusing_hashtags = db.relationship('Confusing_Hashtag',backref='Confusing_User')

     def __repr__(self):
        return "{} (ID: {})".format(self.user, self.id)
    

###################
###### FORMS ######
###################

class NameForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    submit = SubmitField()

def validate_hashtag(form,field):
    hashtag_as_string = str(field.data) 
    if not re.match("^[a-zA-Z0-9_]*$", hashtag_as_string):
        raise ValidationError('Hashtags cannot have special symbols!')
class HashtagForm(FlaskForm):
    hashtag = StringField("Enter the hashtag that confused you *the most* (without special characters or spaces):", validators=[Required(), validate_hashtag])
    user = StringField("Enter the name of the Twitter user who confused you with this hashtag:", validators=[Required()])
    submit = SubmitField()

class MainForm(FlaskForm):
    name = StringField("Please enter your name.",validators=[Required()])
    hashtag = StringField("Enter the hashtag that confused you *the most* (without special characters or spaces):",validators=[Required(), validate_hashtag])
    user = StringField("Enter the name of the Twitter user who confused you with this hashtag:",validators=[Required()])
    submit = SubmitField()

###################################
##### Routes & view functions #####
###################################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404_error.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500_error.html'), 500
#add to database if ne
@app.route('/', methods=['GET', 'POST'])
def home():
    form = MainForm() 
    if form.validate_on_submit():
        name = form.name.data
        hashtag = form.hashtag.data
        user = form.user.data
        newname = Name(name=name)
        db.session.add(newname)
        new_user = Confusing_User.query.filter_by(user=user).first()
        if not new_user: # If None
            # Create that director object
            new_user = Confusing_User(user=user)
            # And save it
            db.session.add(new_user) # Like adding in git...
            # That's all we want to add for now, can commit
            db.session.commit()
            flash('Congrats! The hashtag and user were added to the database!')
        else:
            flash('This user already exists in the database, but the confusing hashtag was added!')
        # No matter what, in this case, should add the movie. (This does NOT check if a movie of the same name exists.)
        hashtag = Confusing_Hashtag(hashtag=hashtag,user_id=new_user.id) # Using the id from that director object above!
        # Now add and commit the movie
        db.session.add(hashtag)
        db.session.commit()
        return render_template('hashtag_home.html', form=form)

    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('hashtag_home.html',form=form)

@app.route('/hashtag_form', methods=['GET','POST'])
def hashtag_form():
    info = []
    form = HashtagForm(request.form)
    if form.validate_on_submit() and request.method=='POST':
        hashtag = form.hashtag.data
        base_url = 'https://tagdef.p.mashape.com/'
        url = base_url + str(hashtag) + '.json'
        response = requests.get(url, headers={"X-Mashape-Key": "VU8AUgehLmmshCMUdGEwWdA49txSp10aCeyjsnXi0WHAvPjz70","Accept": "application/json"})
        text=response.text
        python_obj = json.loads(text)
        for x in python_obj['defs']:
            info.append(x)
        return render_template('hashtag_results.html', objects = info, hashtag=hashtag)
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('hashtag_form.html', form=form)

@app.route('/all_hashtags_and_users', methods=['GET', 'POST'])
def see_all_hashtags_and_users():
    all_users = Confusing_User.query.all()
    num_users = len(all_users) 
    all_hashtags = []
    all_the_hashtags_and_users = Confusing_Hashtag.query.all()
    for h in all_the_hashtags_and_users:
        user1 = Confusing_User.query.filter_by(id=h.user_id).first()
        all_hashtags.append((h.hashtag, user1.user))
    return render_template('all_hashtags_and_users.html', num_users = num_users, all_h_u=all_hashtags)

@app.route('/find_hashtags_for_confuser_form', methods=['GET'])
def see_all_for_one_confuser_form():
    if request.method=='GET':
        user = request.args.get('user')
        return render_template('user_form.html', user=user)

@app.route('/find_hashtags_for_confuser', methods=['GET'])
def see_all_for_one_confuser():
    if request.method=='GET':
        user = request.args.get('user')
        u1 = Confusing_User.query.filter_by(user=user).first()
        if u1:
            h1 = Confusing_Hashtag.query.filter_by(user_id=u1.id).all()
            return render_template('confusing_user.html', user_hashtags=h1, user=user)
        else:
            flash("This user has no saved hashtags associated with them!")
            return redirect(url_for('see_all_for_one_confuser_form'))
 
@app.route('/name_form', methods=['GET','POST'])
def name_form():
    form = NameForm() 
    if form.validate_on_submit():
        name = form.name.data
        newname = Name(name=name)
        db.session.add(newname)
        db.session.commit()
        return redirect(url_for('all_names'))
    return render_template('name_form.html',form=form)

@app.route('/names')
def all_names():
    names = Name.query.all()
    return render_template('name_example.html',names=names)
        

## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True,debug=True) # The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
