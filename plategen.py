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
import json5
import decimal

from mpmath import *
from decimal import *

# Set up decimal and mpmath
getcontext().prec = 10;
mp.dps = 50
mp.pretty = True

# Create blank dxf workspace
plate = ezdxf.new(dxfversion='AC1024')
modelspace = plate.modelspace()

#=================================#
#           Parameters            #
#=================================#

#== Cutout parameters ==#

# Cutout type: mx, alps
cutout_type = "alps"

# Cutout radius: The fillet radius
cutout_radius = Decimal('0.5')

# Stab type: mx, mx-simple, ai-angled, large-cuts, alps-aek, alps-at101
stab_type = "alps-at101"

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

# Used for parsing
current_width = Decimal('1')
current_height = Decimal('1')
current_width_secondary = Decimal('1')
current_height_secondary = Decimal('1')
current_rotx = Decimal('0')
current_roty = Decimal('0')
current_angle = Decimal('0')
current_stab_angle = Decimal('0')
current_cutout_angle = Decimal('0')

#=================================#
#            Classes              #
#=================================#

class Switch:
	
	def __init__(self, x_var, y_var):
		# These fields correspond to the respective kle data
		self.x = x_var
		self.y = y_var
		self.width = 1
		self.height = 1
		self.width_secondary = 1
		self.height_secondary = 1
		self.rotx = 0
		self.roty = 0
		self.angle = 0
		self.cutout_angle = 0
		self.stab_angle = 0
	
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
		modelspace.add_line((x - Decimal('1.335'), y), (x - Decimal('1.335'), y - Decimal('5.21')))
		modelspace.add_line((x + Decimal('1.335'), y), (x + Decimal('1.335'), y - Decimal('5.21')))
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
			make_stab_cutout(center_x - Decimal('41.86'), stab_y)
		elif (unitwidth >= 2.75): 
			make_stab_cutout(center_x + Decimal('20.5'), stab_y)
			make_stab_cutout(center_x - Decimal('20.5'), stab_y)
		elif (unitwidth >= 2): 
			make_stab_cutout(center_x + Decimal('14'), stab_y)
			make_stab_cutout(center_x - Decimal('14'), stab_y)
		elif (unitwidth >= 1.75): 
			make_stab_cutout(center_x + Decimal('12'), stab_y)
			make_stab_cutout(center_x - Decimal('12'), stab_y)
			
# Reset key default parameters
def reset_key_parameters():
	current_width = Decimal('1')
	current_height = Decimal('1')
	current_width_secondary = Decimal('1')
	current_height_secondary = Decimal('1')
	current_rotx = Decimal('0')
	current_roty = Decimal('0')
	current_angle = Decimal('0')
	current_stab_angle = Decimal('0')
	current_cutout_angle = Decimal('0')
			
# Modifies a point with rotation
def rotate_point_around_anchor(x, y, anchor_x, anchor_y, angle):
	radius_squared = decimal.power((x - anchor_x), 2) + decimal.power((y-anchor_y), 2)
	radius = decimal.sqrt(radius_squared)
	
	radian_qty = radians(float(angle))
	cos_result = cos(radian_qty)
	sin_result = sin(radian_qty)
	
	
			
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
#input_data = input_data.replace('\n', '')
#input_data = input_data.replace(r'\"', '')

# TODO: Filter out improper quotes from " being in a label!

if (debug_log):
	print("Filtered input data:")
	print(input_data)
	print("")

# REDO OF PARSER

current_x = Decimal('0')
current_y = Decimal('0')
max_width = Decimal('0')

all_switches = []

json_data = json5.loads('[' + input_data + ']')

for row in json_data:
	if (debug_log):
		print (">>> ROW BEGIN")
		print (str(row))
	
	# KLE standard supports first row being metadata.
	# If it is, ignore.
	if isinstance(row, dict):
		if (debug_log):
			print ("!!! Row is metadata. Skip.")
		continue
	for key in row:
		# The "key" can either be a legend (actual key) or dictionary of data (for succeeding key).
		
		# If it's just a string, it's just a key. Create one and add to list
		if isinstance(key, str):
		
			# First, we simply make the switch
			current_switch = Switch(current_x, current_y)
			
			# Then, adjust the x coord for next switch
			current_x += unit_width * current_width
			# If this is a record, update properly
			if (max_width < current_x):
				max_width = current_x
			
			# And we adjust the fields as necessary.
			# These default to 1 unless edited by a data field preceding
			current_switch.width = current_width
			current_switch.height = current_height
			current_switch.width_secondary = current_width_secondary
			current_switch.height_secondary = current_height_secondary
			current_switch.rotx = current_rotx
			current_switch.roty = current_roty
			current_switch.angle = current_angle
			current_switch.stab_angle = current_stab_angle
			current_switch.cutout_angle = current_cutout_angle
			
			# Deal with some certain cases
			
			# For example, vertical keys created by stretching height to be larger than width
			# The key's cutout angle and stab angle should be offset by 90 degrees to compensate.
			# This effectively transforms the key to a vertical
			# This also handles ISO
			if (current_width < current_height and current_height >= 2):
				current_cutout_angle -= Decimal('90')
				current_stab_angle -= Decimal('90')		
			
			all_switches.append(current_switch)
			
			# Reset the fields to their defaults
			reset_key_parameters()
			
		# Otherwise, it's a data dictionary. We must parse it properly
		else:
			for i in key:
				# i = The dictionary key. Not the keyboard kind of key
				# j = The corresponding value.
				j = key[i]
				
				# Large if-else chain to set params
				if (str(i) == "w"):
					# w = Width
					current_width = Decimal(str(j))
					
				elif (str(i) == "h"):
					# h = Height
					current_height = Decimal(str(j))
					
				elif (str(i) == "w2"):
					# w2 = Secondary width
					current_width_secondary = Decimal(str(j))
					
				elif (str(i) == "h2"):
					# h2 = Secondary height
					current_height_secondary = Decimal(str(j))
					
				elif (str(i) == "rx"):
					# rx = Rotation anchor x
					current_rotx = Decimal(str(j))
					
				elif (str(i) == "ry"):
					# ry = Rotation anchor y
					current_roty = Decimal(str(j))
					
				elif (str(i) == "r"):
					# r = Rotation angle OPPOSITE OF typical counterclockwise-from-xpositive
					current_roty = -Decimal(str(j))
					
				elif (str(i) == "_rs"):
					# _rs = Rotation angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
					current_stab_angle = -Decimal(str(j))
					
				elif (str(i) == "_ca"):
					# _rs = Switch cutout angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
					current_cutout_angle = -Decimal(str(j))
					
				if (str(i) == "x"):
					# x = X offset for next keys
					current_x += Decimal(str(j))
					
				elif (str(i) == "y"):
					# y = Y offset for next keys
					current_y += Decimal(str(j))
	# Finished row
	current_y -= Decimal('1')
	current_x = Decimal('0')
					
# At this point, the keys are built.

# Draw outer bounds - top, bottom, left, right
modelspace.add_line((0,0), (max_width, 0))
modelspace.add_line((0,current_y), (max_width, current_y))
modelspace.add_line((0,0), (0, current_y))
modelspace.add_line((max_width,0), (max_width, current_y))

# Now render each switch

#for current_switch in all_switches:
	

	
if (debug_log):
	print("Complete! Saving plate to specified output")

if (output_method == "file"):
	plate.saveas(filename + '.dxf')
else:
	plate.write(sys.stdout)

exit()