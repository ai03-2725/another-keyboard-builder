from Flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
#app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
 
class PlateGenFrontend(Form):
    kle_form = TextField('KLE Raw Data', validators=[validators.required()])
 
@app.route("/", methods=['GET', 'POST'])
def hello():
    form = PlateGenFrontend(request.form)
 
    print form.errors
    if request.method == 'POST':
        kle_rawdata = request.form['kle_form']
        print name
 
        if form.validate():
            flash('KLE string stored')
        else:
            flash('Please ')
 
    return render_template('hello.html', form=form)
 
if __name__ == "__main__":
    app.run()