import ezdxf
import sys
import re

from decimal import *

# Set up decimal
getcontext().prec = 10;

plate = ezdxf.new(dxfversion='AC1024')
modelspace = plate.modelspace()

#== Argument variables


# Cutout parameters
cutout_type = "mx"
cutout_radius = Decimal('0.5')

# Unit size (i.e. 1U = 19.05mm)
unit_width = Decimal('19.05')
unit_height = Decimal('19.05')

# Debug parameters:
# Draw key outlines?
debug_draw_key_outline = True
# Use generic matrix?
debug_use_generic_matrix = True
# Tell user what's going on when generating?
debug_log = True
# Debug matrix data
debug_matrix_data = """["~\n`","!\n1","@\n2","#\n3","$\n4","%\n5","^\n6","&\n7","*\n8","(\n9",")\n0","_\n-","+\n=",{w:2},"Backspace"],
[{w:1.5},"Tab","Q","W","E","R","T","Y","U","I","O","P","{\n[","}\n]",{w:1.5},"|\n\\"],
[{w:1.75},"Caps Lock","A","S","D","F","G","H","J","K","L",":\n;","\"\n'",{w:2.25},"Enter"],
[{w:2.25},"Shift","Z","X","C","V","B","N","M","<\n,",">\n.","?\n/",{w:2.75},"Shift"],
[{w:1.25},"Ctrl",{w:1.25},"Win",{w:1.25},"Alt",{a:7,w:6.25},"",{a:4,w:1.25},"Alt",{w:1.25},"Win",{w:1.25},"Menu",{w:1.25},"Ctrl"]"""


#== Runtime-modified variables


# Current x/y coordinates
current_x = Decimal(0)
current_y = Decimal(0)

# Cutout sizes
cutout_width = Decimal(0)
cutout_height = Decimal(0)

# Input data
input_data = ""

#== Defined functions


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
	
#== The code

# Generate switch cutout sizes
if (cutout_type == "mx"):
	cutout_width = Decimal('14');
	cutout_height = Decimal('14');
elif (cutout_type == "alps"):
	cutout_width = Decimal('15.50');
	cutout_height = Decimal('12.80');
else:
	print("Unsupported cutout type.")
	print("Supported: mx, alps")
	exit()

# If debug matrix is on, make sth generic
if (debug_use_generic_matrix):
	input_data = debug_matrix_data
# Otherwise, take from stdin
else:
	input_data = sys.stdin.read()

# Make some variables
in_row = False
in_data = False
parsing_width = False
parsing_height = False
parsing_string = ""
in_label = False
current_width = Decimal(1)
current_height = Decimal(1)
	
# Act upon the input data
for c in input_data:

	if (c == '[' and not in_label):
		# We have entered a row!
		# If already in a row, bad formatting!
		if(in_row):
			print("Malformed input: Row in a row", file=sys.stderr)
			exit()
		
		in_row = True
		
		if (debug_log):
			print("Beginning row")
	
	elif (c == ']' and not in_label):
		# We have finished a row!
		# If not in a row, bad formatting!
		if(not in_row):
			print("Malformed input: Row ends outside a row", file=sys.stderr)
			exit()
		
		in_row = False
		# Move down a row
		current_y -= unit_height;
		current_x = Decimal('0');
		
		if (debug_log):
			print("Row end, moving down")
	
	elif (c == '{' and not in_label):
		# We have entered a switch data section!
		# If are already parsing, bad data!
		if(in_data):
			print("Malformed input: data begins in data", file=sys.stderr)
			exit()
		
		in_data = True
		
		if (debug_log):
			print("Beginning data brackets")
	
	elif (c == '}' and not in_label):
		# We have finished a switch data section!
		# If are not already parsing, bad data!
		if(not in_data):
			print("Malformed input: data ends outside of data", file=sys.stderr)
			exit()
			
		# We could have been parsing a width or height.
		# If so, apply changes.
		if (parsing_width):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: width input isn't a digit", file=sys.stderr)
				exit()
		
			current_width = Decimal(parsing_string)
			parsing_string = ""
			parsing_width = False
			
			if (debug_log):
				print("Bracket closed while parsing width. Width set to " + current_width)
		
		elif (parsing_height):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: height input isn't a digit", file=sys.stderr)
				exit()
		
			current_height = Decimal(parsing_string)
			parsing_string = ""
			parsing_height = False
			
			if (debug_log):
				print("Bracket closed while parsing height. Height set to " + current_height)
		
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
				make_cutout(current_x + (((current_width * unit_width) - cutout_width) / Decimal('2')), current_y - (((current_height * unit_height) - cutout_height) / Decimal('2')))
				# Move current coords over:
				current_x += current_width * unit_width;
				# And reset size to normal:
				current_width = Decimal(1);
				current_height = Decimal(1);
				
				if (debug_log):
					print("Ended label, drew switch")
		
	elif (c == 'w' and in_data):
		# Width data.
		# Begin parsing
		
		#But if already parsing sth else, malformed string
		if (parsing_width or parsing_height):
			print("Malformed input: width begins when already parsing size variable", file=sys.stderr)
			exit()
		
		parsing_width = True
		
		if (debug_log):
			print("Beginning width parse")
		
	elif (c == 'h' and in_data):
		# Width data.
		# Begin parsing
		
		#But if already parsing sth else, malformed string
		if (parsing_width or parsing_height):
			print("Malformed input: height begins when already parsing size variable", file=sys.stderr)
			exit()
		
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
				exit()
		
			current_width = Decimal(parsing_string)
			parsing_string = ""
			parsing_width = False
			
			if (debug_log):
				print("Width parsed, set to " + current_width)
			
		elif (parsing_height):
		
			# Verify that it is a digit
			if (not is_a_number(parsing_string)):
				print(parsing_string)
				print("Malformed input: height input isn't a digit", file=sys.stderr)
				exit()
		
			current_height = Decimal(parsing_string)
			parsing_string = ""
			parsing_height = False
			
			if (debug_log):
				print("Height parsed, set to " + current_height)
			
	else:
		# Otherwise, if we're parsing data, add it on
		if (parsing_width or parsing_height):
			parsing_string += c
			
			if (debug_log):
				print("Appending " + c + " to parsing text")
				
		else:
		
			if (debug_log):
				print("Ignoring " + c)
				
			continue
			
# At this point we should be done. Are we?
if (in_row or in_data or in_label or parsing_width or parsing_height):
	print(parsing_string, file=sys.stderr)
	print("Malformed input: Ends abruptly", file=sys.stderr)
	
	exit()
	
plate.saveas('plate.dxf')