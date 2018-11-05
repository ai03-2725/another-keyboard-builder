from flask import Flask, render_template, flash, request, send_from_directory

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'change me'.encode('utf8')
 
@app.route('/img/<path:path>')
def static_img(path):
    return send_from_directory('img', path)

@app.route("/", methods=['GET'])
def default_route():

    return render_template('base.html')
 
if (__name__ == "__main__"):
    app.run()