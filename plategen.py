#=================================#
#        Plate Generator          #
#=================================#

# By ai03
# Credits to
# Senter for stab measurements
# Pwner for large stabilizer cutouts
# Deskthority for spacebar measurements
# Mxblue, Bakingpy for assistance

#=================================#
#         Initialization          #
#=================================#

# Import necessities
import ezdxf
import sys
from decimal import *

# Set up decimal
getcontext().prec = 10;

# Create blank dxf workspace
plate = ezdxf.new(dxfversion='AC1024')
modelspace = plate.modelspace()

#=================================#
#           Parameters            #
#=================================#

#== Cutout parameters ==#

# Cutout type: mx, alps
cutout_type = "mx"

# Cutout radius: The fillet radius
cutout_radius = Decimal('0.5')

# Stab type: mx, mx-simple, ai-angled, large-cuts, alps-aek, alps-at101
stab_type = "large-cuts"

# Korean cuts: The cutouts typically found on kustoms beside the switches.
# This script only handles the thin short cuts vertically beside each switch cut, not the large ones, i.e. between fn row and alphas.
# none = disabled, typical = 1.5-1.75U only, extreme = On 1.5-2.75U
koreancuts_type = "typical"

# Unit size (i.e. 1U = 19.05mm)
unit_width = Decimal('19.05')
unit_height = Decimal('19.05')

# Output settings. Method can be file or stdout. Filename is ignored if output_method is set to stdout
output_method = "stdout"
filename = "plate"

#== Debug parameters ==#

# Draw key outlines?
debug_draw_key_outline = False
# Use generic matrix specified in debug_matrix_data below?
debug_use_generic_matrix = False
# Tell user everything about what's going on and spam the console?
debug_log = False
# Write incomplete dxf if end of input data is reached unexpectedly while parsing?
debug_write_incomplete = False
# Debug matrix data
debug_matrix_data = """
[{a:7},"","","","","","","","","","","","","",{w:2},""],
[{w:1.5},"","","","","","","","","","","","","",{w:1.5},""],
[{w:1.75},"","","","","","","","","","","","",{w:2.25},""],
[{w:2.25},"","","","","","","","","","","",{w:2.75},""],
[{w:1.25},"",{w:1.25},"",{w:1.25},"",{w:6.25},"",{w:1.25},"",{w:1.25},"",{w:1.25},"",{w:1.25},""]
"""

#=================================#
#         Runtime Vars            #
#=================================#


# Current x/y coordinates
current_x = Decimal('0')
current_y = Decimal('0')

# Cutout sizes
cutout_width = Decimal('0')
cutout_height = Decimal('0')

# Input data
input_data = ""

#=================================#
#           Functions             #
#=================================#

# Cutout maker
def make_cutout(x, y):

	# First draw corners - top left, top right, bottom left, bottom right
	modelspace.add_arc((x + cutout_radius, y - cutout_radius), cutout_radius, 90, 180)
	modelspace.add_arc((x + cutout_width - cutout_radius, y - cutout_radius), cutout_radius, 0, 90)
	modelspace.add_arc((x + cutout_radius, y - cutout_height + cutout_radius), cutout_radius, 180, 270)
	modelspace.add_arc((x + cutout_width - cutout_radius, y - cutout_height + cutout_radius), cutout_radius, 270, 360)
	
	# Then draw sides - top, bottom, left, right
	modelspace.add_line((x + cutout_radius, y), (x + cutout_width - cutout_radius, y))
	modelspace.add_line((x + cutout_radius, y - cutout_height), (x + cutout_width - cutout_radius, y - cutout_height))
	modelspace.add_line((x, y - cutout_radius), (x, y - cutout_height + cutout_radius))
	modelspace.add_line((x + cutout_width, y - cutout_radius), (x + cutout_width, y - cutout_height + cutout_radius))
	
# Key outline maker. Width and height in Units (U)
def make_key_outline(x, y, width, height):

	# Draw sides - top, bottom, left, right
	modelspace.add_line((x, y), (x + (width * unit_width), y))
	modelspace.add_line((x, y - (height * unit_height)), (x + (width * unit_width), y - (height * unit_height)))
	modelspace.add_line((x, y), (x, y - (height * unit_height)))
	modelspace.add_line((x + (width * unit_width), y), (x + (width * unit_width), y - (height * unit_height)))
	
# Check if string is valid number
# Credits to https://stackoverflow.com/questions/4138202/using-isdigit-for-floats
def is_a_number(s):
	return_value = True
	try:
		test_float = float(s)
	except ValueError:
		return_value = False
	return return_value
	
# Stab cutout maker
# The x and y are center top, like this:
#
# ---X---
# |     |
# |     |
# |     |
# |_   _|
#   |_|

def make_stab_cutout(x, y):
	if (stab_type == "mx-simple"):
		# Rectangular simplified mx cutout.
		modelspace.add_line((x - Decimal('3.3274'), y), (x + Decimal('3.3274'), y))
		modelspace.add_line((x - Decimal('3.3274'), y - Decimal('13.462')), (x + Decimal('3.3274'), y - Decimal('13.462')))
		modelspace.add_line((x - Decimal('3.3274'), y), (x - Decimal('3.3274'), y - Decimal('13.462')))
		modelspace.add_line((x + Decimal('3.3274'), y), (x + Decimal('3.3274'), y - Decimal('13.462')))
	elif (stab_type == "mx"):
		# Proper MX based on datasheet.
		# DOES NOT INCLUDE PLATE MOUNT since basically nobody uses plate mount stabs
		modelspace.add_line((x - Decimal('3.3274'), y), (x + Decimal('3.3274'), y))
		modelspace.add_line((x - Decimal('3.3274'), y - Decimal('12.2936')), (x - Decimal('1.8034'), y - Decimal('12.2936')))
		modelspace.add_line((x + Decimal('3.3274'), y - Decimal('12.2936')), (x + Decimal('1.8034'), y - Decimal('12.2936')))
		modelspace.add_line((x - Decimal('1.8034'), y - Decimal('13.462')), (x + Decimal('1.8034'), y - Decimal('13.462')))
		
		modelspace.add_line((x - Decimal('3.3274'), y), (x - Decimal('3.3274'), y - Decimal('12.2936')))
		modelspace.add_line((x + Decimal('3.3274'), y), (x + Decimal('3.3274'), y - Decimal('12.2936')))
		modelspace.add_line((x - Decimal('1.8034'), y - Decimal('12.2936')), (x - Decimal('1.8034'), y - Decimal('13.462')))
		modelspace.add_line((x + Decimal('1.8034'), y - Decimal('12.2936')), (x + Decimal('1.8034'), y - Decimal('13.462')))
	elif (stab_type == "ai-angled"):
		# A sleek cutout with diagonal cuts on bottom. Higher origin y coordinate by 0.3mm to account for a 0.5mm fillet.
		modelspace.add_line((x - Decimal('3.3274'), y + Decimal('0.3')), (x + Decimal('3.3274'), y + Decimal('0.3')))
		modelspace.add_line((x - Decimal('2.159'), y - Decimal('13.462')), (x + Decimal('2.159'), y - Decimal('13.462')))
		
		modelspace.add_line((x - Decimal('3.3274'), y - Decimal('12.2936')), (x - Decimal('2.159'), y - Decimal('13.462')))
		modelspace.add_line((x + Decimal('3.3274'), y - Decimal('12.2936')), (x + Decimal('2.159'), y - Decimal('13.462')))
		
		modelspace.add_line((x - Decimal('3.3274'), y + Decimal('0.3')), (x - Decimal('3.3274'), y - Decimal('12.2936')))
		modelspace.add_line((x + Decimal('3.3274'), y + Decimal('0.3')), (x + Decimal('3.3274'), y - Decimal('12.2936')))
	elif (stab_type == "large-cuts"):
		# Large, spacious 15x7 cutouts; 1mm from mx switch cutout top
		modelspace.add_line((x - Decimal('3.5'), y + Decimal('0.2954')), (x + Decimal('3.5'), y + Decimal('0.2954')))
		modelspace.add_line((x - Decimal('3.5'), y - Decimal('14.7046')), (x + Decimal('3.5'), y - Decimal('14.7046')))
		modelspace.add_line((x - Decimal('3.5'), y + Decimal('0.2954')), (x - Decimal('3.5'), y - Decimal('14.7046')))
		modelspace.add_line((x + Decimal('3.5'), y + Decimal('0.2954')), (x + Decimal('3.5'), y - Decimal('14.7046')))
	elif (stab_type == "alps-aek" or stab_type == "alps-at101"):
		# Rectangles 2.67 wide, 5.21 high.
		modelspace.add_line((x - Decimal('1.335'), y), (x + Decimal('1.335'), y))
		modelspace.add_line((x - Decimal('1.335'), y - Decimal('5.21')), (x + Decimal('1.335'), y - Decimal('5.21')))
		modelspace.add_line((x - Decimal('1.335'), y), (x - Decimal('5.21'), y - Decimal('5.21')))
		modelspace.add_line((x + Decimal('1.335'), y), (x + Decimal('5.21'), y - Decimal('5.21')))
	else:
		print("Unsupported stab type.", file=sys.stderr)
		print("Stab types: mx, mx-simple, ai-angled, large-cuts, alps-aek, alps-at101", file=sys.stderr)
		exit(1)
	
# Korean cuts maker
# Same dimensions method as stab cutout maker

def make_korean_cuts(x, y):
		
		modelspace.add_arc((x - Decimal('1') + cutout_radius, y - cutout_radius), cutout_radius, 90, 180)
		modelspace.add_arc((x + Decimal('1') - cutout_radius, y - cutout_radius), cutout_radius, 0, 90)
		modelspace.add_arc((x - Decimal('1') + cutout_radius, y - cutout_height + cutout_radius), cutout_radius, 180, 270)
		modelspace.add_arc((x + Decimal('1') - cutout_radius, y - cutout_height + cutout_radius), cutout_radius, 270, 360)
		modelspace.add_line((x - Decimal('1'), y - cutout_radius), (x - Decimal('1'), y - cutout_height + cutout_radius))
		modelspace.add_line((x + Decimal('1'), y - cutout_radius), (x + Decimal('1'), y - cutout_height + cutout_radius))
		modelspace.add_line((x - Decimal('1') + cutout_radius, y), (x + Decimal('1') - cutout_radius, y))
		modelspace.add_line((x - Decimal('1') + cutout_radius, y - cutout_height), (x + Decimal('1') - cutout_radius, y - cutout_height))
	
# Calls make stab cutout based on unit width and style
def generate_stabs(x, y, unitwidth):

	center_x = x + (cutout_width / Decimal('2'))

	if (debug_log):
		print("Genstabs: width " + str(unitwidth))

	if (stab_type == "mx-simple" or stab_type == "mx" or stab_type == "ai-angled" or stab_type == "large-cuts"):
		stab_y = y - Decimal('1.2954')
		# Switch based on unit width
		# These spacings are based on official mx datasheets and deskthority measurements
		if (unitwidth >= 8): 
			make_stab_cutout(center_x + Decimal('66.675'), stab_y)
			make_stab_cutout(center_x - Decimal('66.675'), stab_y)
		elif (unitwidth >= 7): 
			make_stab_cutout(center_x + Decimal('57.15'), stab_y)
			make_stab_cutout(center_x - Decimal('57.15'), stab_y)
		elif (unitwidth == 6.25): 
			make_stab_cutout(center_x + Decimal('50'), stab_y)
			make_stab_cutout(center_x - Decimal('50'), stab_y)
		elif (unitwidth == 6): 
			make_stab_cutout(center_x + Decimal('38.1'), stab_y)
			make_stab_cutout(center_x - Decimal('57.15'), stab_y)
		elif (unitwidth >= 3): 
			make_stab_cutout(center_x + Decimal('19.05'), stab_y)
			make_stab_cutout(center_x - Decimal('19.05'), stab_y)
		elif (unitwidth >= 2): 
			make_stab_cutout(center_x + Decimal('11.938'), stab_y)
			make_stab_cutout(center_x - Decimal('11.938'), stab_y)
			if (koreancuts_type == "extreme"):
				make_korean_cuts(center_x + Decimal('18.25'), y)
				make_korean_cuts(center_x - Decimal('18.25'), y)
		elif (unitwidth >= 1.5):
			if (koreancuts_type == "typical" or (koreancuts_type == "extreme")):
				make_korean_cuts(center_x + Decimal('11.6'), y)
				make_korean_cuts(center_x - Decimal('11.6'), y)
	elif (stab_type == "alps-aek"):
		# These are mostly based on measurements. 
		# If someone has datasheets, please let me know
		stab_y = y - Decimal('10.273')
		if (unitwidth >= 6.5): 
			make_stab_cutout(center_x + Decimal('45.3'), stab_y)
			make_stab_cutout(center_x - Decimal('45.3'), stab_y)
		elif (unitwidth >= 6.25): 
			make_stab_cutout(center_x + Decimal('41.86'), stab_y)
			make_stab_cutout(center_x - Decimal('41.86'), stab_y)
		elif (unitwidth >= 2): 
			make_stab_cutout(center_x + Decimal('14'), stab_y)
			make_stab_cutout(center_x - Decimal('14'), stab_y)
		elif (unitwidth >= 1.75): 
			make_stab_cutout(center_x + Decimal('12'), stab_y)
			make_stab_cutout(center_x - Decimal('12'), stab_y)
	elif (stab_type == "alps-at101"):
		# These are mostly based on measurements. 
		# If someone has datasheets, please let me know
		stab_y = y - Decimal('10.273')
		if (unitwidth >= 6.5): 
			make_stab_cutout(center_x + Decimal('45.3'), stab_y)
			make_stab_cutout(center_x - Decimal('45.3'), stab_y)
		elif (unitwidth >= 6.25): 
			make_stab_cutout(center_x + Decimal('41.86'), stab_y)
			make_stab_cutout(center_x - Decimal('41.86'), stab_y)]
		elif (unitwidth >= 2.75): 
			make_stab_cutout(center_x + Decimal('20.5'), stab_y)
			make_stab_cutout(center_x - Decimal('20.5'), stab_y)
		elif (unitwidth >= 2): 
			make_stab_cutout(center_x + Decimal('14'), stab_y)
			make_stab_cutout(center_x - Decimal('14'), stab_y)
		elif (unitwidth >= 1.75): 
			make_stab_cutout(center_x + Decimal('12'), stab_y)
			make_stab_cutout(center_x - Decimal('12'), stab_y)
			
#=================================#
#         Plate Creation          #
#=================================#

# Generate switch cutout sizes
if (cutout_type == "mx"):
	cutout_width = Decimal('14');
	cutout_height = Decimal('14');
elif (cutout_type == "alps"):
	cutout_width = Decimal('15.50');
	cutout_height = Decimal('12.80');
else:
	print("Unsupported cutout type.", file=sys.stderr)
	print("Supported: mx, alps", file=sys.stderr)
	exit(1)

# Check if output method is legal
if (output_method != "stdout" and output_method != "file"):
	print("Unsupported output method specified", file=sys.stderr)
	exit(1)
	
# If debug matrix is on, make sth generic
if (debug_use_generic_matrix):
	input_data = debug_matrix_data
# Otherwise, take from stdin
else:
	input_data = sys.stdin.read()
	
# Sanitize by removing \" (KLE's literal " for a label)
input_data = input_data.replace('\n', '')
input_data = input_data.replace(r'\"', '')

# TODO: Filter out improper quotes from " being in a label!

if (debug_log):
	print("Filtered input data:")
	print(input_data)
	print("")


# Make some variables
in_row = False
in_data = False
parsing_width = False
parsing_height = False
parsing_string = ""
in_label = False
current_width = Decimal('1')
current_height = Decimal('1')
max_width = Decimal('0')
max_height = Decimal('0')
	
# Act upon the input data
for c in input_data:

	if (c == '[' and not in_label):
		# We have entered a row!
		# If already in a row, bad formatting!
		if(in_row):
			print("Malformed input: Row in a row", file=sys.stderr)
			exit(1)
		
		in_row = True
		
		if (debug_log):
			print("Beginning row")
	
	elif (c == ']' and not in_label):
		# We have finished a row!
		# If not in a row, bad formatting!
		if(not in_row):
			print("Malformed input: Row ends outside a row", file=sys.stderr)
			exit(1)
		
		in_row = False
		
		# Move down a row
		current_y -= unit_height;
		
		# Check for max width/height for drawing outlines
		if (current_x > max_width):
			max_width = current_x
		
		if (abs(current_y) > abs(max_height)):
			max_height = current_y
		
		# Reset x to 0
		current_x = Decimal('0');
		
		if (debug_log):
			print("Row end, moving down")
	
	elif (c == '{' and not in_label):
		# We have entered a switch data section!
		# If are already parsing, bad data!
		if(in_data):
			print("Malformed input: data begins in data", file=sys.stderr)
			exit(1)
		
		in_data = True
		
		if (debug_log):
			print("Beginning data brackets")
	
	elif (c == '}' and not in_label):
		# We have finished a switch data section!
		# If are not already parsing, bad data!
		if(not in_data):
			print("Malformed input: data ends outside of data", file=sys.stderr)
			exit(1)
			
		# We could have been parsing a width or height.
		# If so, apply changes.
		if (parsing_width):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: width input isn't a digit", file=sys.stderr)
				exit(1)
		
			current_width = Decimal(parsing_string)
			parsing_string = ""
			parsing_width = False
			
			if (debug_log):
				print("Bracket closed while parsing width. Width set to " + str(current_width))
		
		elif (parsing_height):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: height input isn't a digit", file=sys.stderr)
				exit(1)
		
			current_height = Decimal(parsing_string)
			parsing_string = ""
			parsing_height = False
			
			if (debug_log):
				print("Bracket closed while parsing height. Height set to " + str(current_height))
		
		in_data = False
	
	elif (c == '"'):
		# We are in a switch label, or leaving one!
		# The label is what constitutes the existence of a key.
		
		# Occasionally it's a thing such as p:"DCS" in the data brackets, so if so, ignore.
		if (not in_data):
			if (not in_label):
				# Label begins
				in_label = True
				
				if (debug_log):
					print("Beginning label")
				
			else:
				# If a label ends, it means it's time to draw the switch.
				in_label = False
				# Draw key outline?
				if (debug_draw_key_outline):
					make_key_outline(current_x, current_y, current_width, current_height)
				# Now we draw the switch cutout
				cutout_corner_x = current_x + (((current_width * unit_width) - cutout_width) / Decimal('2'))
				cutout_corner_y = current_y - (((current_height * unit_height) - cutout_height) / Decimal('2'))
				make_cutout(cutout_corner_x, cutout_corner_y)
				
				# Generate stabs
				generate_stabs(cutout_corner_x, cutout_corner_y, current_width)
				
				# Move current coords over:
				current_x += current_width * unit_width;
				# And reset size to normal:
				current_width = Decimal(1);
				current_height = Decimal(1);
				
				if (debug_log):
					print("Ended label, drew switch.")
				
		
	elif (c == 'w' and in_data):
		# Width data.
		# Begin parsing
		
		#But if already parsing sth else, malformed string
		if (parsing_width or parsing_height):
			print("Malformed input: width begins when already parsing size variable", file=sys.stderr)
			exit(1)
		
		parsing_width = True
		
		if (debug_log):
			print("Beginning width parse")
		
	elif (c == 'h' and in_data):
		# Width data.
		# Begin parsing
		
		#But if already parsing sth else, malformed string
		if (parsing_width or parsing_height):
			print("Malformed input: height begins when already parsing size variable", file=sys.stderr)
			exit(1)
		
		parsing_height = True
		
		if (debug_log):
			print("Beginning height parse")
		
	elif (c == ':'):
		# We absolutely ignore colons, since the other filters handle the rest.
		
		if (debug_log):
			print("Ignoring colon")
		
		continue
	
	elif (c == ','):
		# Commas are used for determining end of data only.
		
		if (parsing_width):
			
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: width input isn't a digit", file=sys.stderr)
				exit(1)
		
			current_width = Decimal(parsing_string)
			parsing_string = ""
			parsing_width = False
			
			if (debug_log):
				print("Width parsed, set to " + str(current_width))
			
		elif (parsing_height):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: height input isn't a digit", file=sys.stderr)
				exit(1)
		
			current_height = Decimal(parsing_string)
			parsing_string = ""
			parsing_height = False
			
			if (debug_log):
				print("Height parsed, set to " + str(current_height))
			
	else:
		# Otherwise, if we're parsing data, add it on
		if (parsing_width or parsing_height):
			parsing_string += c
			
			if (debug_log):
				print("Appending " + c + " to parsing text")
				
		else:
		
			if (debug_log):
				if(in_label):
					print("Part of label: " + c)
				else:
					print("Ignoring " + c)
			continue
			
# At this point we should be done. Are we?
if (in_row or in_data or in_label or parsing_width or parsing_height):
	print(parsing_string, file=sys.stderr)
	print("Malformed input: Ends abruptly", file=sys.stderr)
	
	if (debug_write_incomplete):
		print("Saving incomplete plate to error-plate.dxf", file=sys.stderr)
		plate.saveas('error-plate.dxf')
	
	exit(1)
	
# Draw outer bounds - top, bottom, left, right
modelspace.add_line((0,0), (max_width, 0))
modelspace.add_line((0,max_height), (max_width, max_height))
modelspace.add_line((0,0), (0, max_height))
modelspace.add_line((max_width,0), (max_width, max_height))
	
if (debug_log):
	print("Complete! Saving plate to specified output")

if (output_method == "file"):
	plate.saveas(filename + '.dxf')
else:
	plate.write(sys.stdout)

exit()