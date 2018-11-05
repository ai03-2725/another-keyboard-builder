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
	
	try:
		gen = plategen.PlateGenerator(cutout_type, cutout_radius, stab_type, stab_radius, acoustic_type, acoustic_radius, 
		unit_width, unit_height, False)
	except(ValueError):
		flash("Enter valid integer arguments.")
		return render_template('base.html')
	
	out_code = gen.generate_plate(output_data, kle_input)
	if (out_code == 1):
		flash("Invalid KLE data.")
		return render_template('base.html')
	elif (out_code == 2):
		flash("Unsupported stabilizer cutout type.")
		return render_template('base.html')
	elif (out_code == 3):
		flash("Unsupported switch cutout type.")
		return render_template('base.html')
	elif (out_code == 4):
		flash("Switch fillet radius must be between 0 and half the cutout width/height.")
		return render_template('base.html')
	elif (out_code == 5):
		flash("Unit size must be between 0 and 1000mm.")
		return render_template('base.html')
	elif (out_code == 6):
		flash("Stablizer fillet radius must be between 0 and 5.")
		return render_template('base.html')
	elif (out_code == 7):
		flash("Acoustic cutout fillet radius must be between 0 and 5.")
		return render_template('base.html')
	elif (out_code != 0):
		flash("Unspecified error.")
		return render_template('base.html')
	
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
    app.run()