from flask import Flask, render_template, flash, request, send_from_directory, send_file

import plategen
import io

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
	
@app.route("/plategen", methods=['POST'])
def receive_data():
	
	cutout_type = request.form['cutout-type']
	cutout_radius = request.form['cutout-radius']
	stab_type = request.form['stab-type']
	stab_radius = request.form['stab-radius']
	acoustic_type = request.form['acoustic-type']
	acoustic_radius = request.form['acoustic-radius']
	unit_width = request.form['unit-width']
	unit_height = request.form['unit-height']
	kle_input = request.form['kle-data']
	
	output_data = io.StringIO()
	
	gen = plategen.PlateGenerator(cutout_type, cutout_radius, stab_type, stab_radius, acoustic_type, acoustic_radius, 
	unit_width, unit_height, False)
	
	gen.generate_plate(output_data, kle_input)
	
	# Convert StringIO to BytesIO
	output_file = io.BytesIO()
	output_file.write(output_data.getvalue().encode('utf-8'))
	# seeking was necessary. Python 3.5.2, Flask 0.12.2
	output_file.seek(0)
	output_data.close()
	
	return send_file(
		output_file,
		as_attachment=True,
        attachment_filename='plate.dxf',
		mimetype='application/dxf'
   )
 
if (__name__ == "__main__"):
    app.run(debug=True)