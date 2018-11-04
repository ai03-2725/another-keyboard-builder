from flask import Flask, render_template, flash, request, send_from_directory
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'change me'.encode('utf8')
 
class PlateGenFrontend(Form):
    kle_form = TextField('KLE Raw Data', validators=[validators.required()])
 
@app.route('/img/<path:path>')
def static_img(path):
    return send_from_directory('img', path)

@app.route("/", methods=['GET', 'POST'])
def hello():
    form = PlateGenFrontend(request.form)
 
    print (form.errors)
    if (request.method == 'POST'):
        kle_rawdata = request.form['kle-data']
        print (kle_rawdata)
 
        if (form.validate()):
            flash('KLE string stored')
        else:
            flash('Error: Please check the data fields.')
 
    return render_template('base.html', form=form)
 
if (__name__ == "__main__"):
    app.run()