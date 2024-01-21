from flask import Flask, request, render_template, Markup, redirect, url_for, session, flash, jsonify
from tagsearcher import TagSearcher
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from plyer import notification

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
db = SQLAlchemy(app)
current_timers = []

class TagSearchInstances(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    html_content = db.Column(db.String(1000), nullable=False)
    link = db.Column(db.String(1000), nullable=False)
    #possible states = Created, Active, Error
    state = db.Column(db.String(20), nullable=False)
    elementString = db.Column(db.String(1000))
    content = db.Column(db.String(1000), nullable=False)
    saved_index = db.Column(db.Integer, nullable=False)
    last_run = db.Column(db.DateTime)
    last_val = db.Column(db.String(1000), default = "")

    def __repr__(self):
        return f'<Tag Watch Instance {self.id}>'

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        html_content = request.form.get('html_content')
        link = request.form.get('link')
        # Create a TagSearcher object with the provided HTML and link
        try:
            tag_searcher = TagSearcher(link, html_content)  
        except: #Add error page redirect here
            return redirect("/")
        try:
            db.session.add(TagSearchInstances(html_content=tag_searcher.getHTML(), link=tag_searcher.getLink(), 
                                              state="Created", saved_index=tag_searcher.getSavedIndex(), content = tag_searcher.getVal()))
            db.session.commit()
        except Exception as e: #Add error page redirect here
            print(str(e))
            return redirect("/")
        # Get the HTML and link from the TagSearcher object
        html = tag_searcher.getHTML()
        link = tag_searcher.getLink()
        return redirect("/")
    else:
        instances = TagSearchInstances.query.all()
        return render_template('index.html', instances = instances)  # Render a form for the user to input HTML and a link

@app.route("/start/<int:id>/", methods=['GET'])
def start(id):
    try:
        instance = TagSearchInstances.query.get_or_404(id)
        db.session.commit()
        searcher = TagSearcher(instance.link, instance.html_content)

        if(searcher.start() != 0):
            instance.state = "Error"
        else:
            instance.state = "Active"
            instance.content = searcher.getVal()
            instance.saved_index = searcher.getSavedIndex()
            instance.elementString = searcher.getElementString()
            instance.last_run = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        print(str(e))

    return redirect("/")

def checkValue(oldValue, newValue):
    if(oldValue != newValue):
        return True
    else:
        return False

#Manually checks an ItemWatch instance
@app.route("/updateValue/<int:id>/", methods=['GET'])
def updateValueManuallyInterface(id):
    try:
        updateValue(id)
    except Exception as e: 
        print(str(e))
    return redirect("/")

def updateValue(id):
    instance = TagSearchInstances.query.get_or_404(id)
    searcher = TagSearcher(instance.link, instance.html_content)
    try:
        searcher.searchWithIndexandElementString(index = instance.saved_index, elementString=instance.elementString)
    except Exception as e:
        instance.state = "Error"
        print(str(e))
        db.session.commit()
        return
    instance.state = "Active"
    oldValue = instance.content
    instance.last_val = oldValue
    if(checkValue(oldValue, searcher.getVal())):
        print("Value changed") #Display this to user
        notification.notify(
            title = "Value changed",
            message = "Value changed from " + oldValue + " to " + searcher.getVal(),
            timeout = 10
        )
    instance.content = searcher.getVal()
    instance.saved_index = searcher.getSavedIndex()
    instance.elementString = searcher.getElementString()
    instance.last_run = datetime.utcnow()
    db.session.commit()

#Check each instance
@app.route("/updateValuesScheduled/", methods=['GET'])
def updateValuesScheduled():
    instances = TagSearchInstances.query.all()
    print("Updating values")
    for instance in instances:
        if(instance.state == "Active"):
            updateValue(instance.id)
    return redirect("/")

if __name__ == "__main__":
    #Build database
    with app.test_request_context():
        db.create_all()

    app.run(debug=False)
