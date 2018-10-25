#=================================#
#        Plate Generator          #
#=================================#

# By ai03
# Credits to
# Amtra5, Mxblue, Bakingpy for code-side assistance
# Senter, Pwner, Kevinplus, Deskthority Wiki for measurements

# Automated production of high-end mechanical keyboard plate data
# No float rounding issues, pre-filleted corners, ready for production.

# EXTRA SUPPORTED JSON FIELDS:
# In addition to the KLE fields such as w: for width,
# _rs: Rotate the stabilizers
# _rc: Rotate switch cutout 

#=================================#
#                                 #
#=================================#

# Import necessities
import ezdxf
import sys
import json5

from mpmath import *
from decimal import *

class PlateGenerator(object):

	#init 
	def __init__(self):

		# Set up decimal and mpmath
		getcontext().prec = 50
		mp.dps = 50
		mp.pretty = True

		# Create blank dxf workspace
		self.plate = ezdxf.new(dxfversion='AC1024')
		self.modelspace = self.plate.modelspace()
		
		# Cutout type: mx, alps
		self.cutout_type = "mx"

		# Cutout radius: The fillet radius ( 0 <= x <= 1/2 cutout width or height )
		self.cutout_radius = Decimal('0.5')

		# Stab type: mx-simple, large-cuts, alps-aek, alps-at101
		self.stab_type = "mx-simple"

		# Stab radius: The fillet radius for stab cutouts ( 0 <= x <= 1 )
		self.stab_radius = Decimal('0.5')

		# Korean cuts: The cutouts typically found on kustoms beside the switches.
		# This script only handles the thin short cuts vertically beside each switch cut, not the large ones, i.e. between fn row and alphas.
		# none = disabled, typical = 1.5-1.75U only, extreme = On 1.5-2.75U
		self.koreancuts_type = "typical"

		# Unit size (i.e. 1U = 19.05mm). ( 0 <= x <= inf, cap at 1000 for now )
		self.unit_width = Decimal('19.05')
		self.unit_height = Decimal('19.05')

		# Output settings. Method can be file or stdout. self.filename is ignored if self.output_method is set to stdout
		self.output_method = "stdout"
		self.filename = "plate"

		#== Debug parameters ==#

		# Draw key outlines?
		self.debug_draw_key_outline = False
		# Use generic matrix specified in self.debug_matrix_data below?
		self.debug_use_generic_matrix = False
		# Tell user everything about what's going on and spam the console?
		self.debug_log = False
		# Write incomplete dxf if end of input data is reached unexpectedly while parsing?
		self.debug_write_incomplete = False
		# Debug matrix data
		self.debug_matrix_data = """
		[{x:1,a:7},"","","","","","","","","","","","",{w:2},""],
		[{w:1.5},"","","","","","","","","","","","","",{w:1.5},""],
		[{w:1.75},"","","","","","","","","","","","",{w:2.25},""],
		[{w:2.25},"","","","","","","","","","","",{w:2.75},""],
		[{w:1.25},"",{w:1.25},"",{w:1.25},"",{w:6.25},"",{w:1.25},"",{w:1.25},"",{w:1.25},"",{w:1.25},""],
		[{r:15,rx:0.5,ry:0.5,y:-0.5,x:-0.5},""]
		"""

		# Runtime vars that are often systematically changed or reset

		# Current x/y coordinates
		self.current_x = Decimal('0')
		self.current_y = Decimal('0')

		# Cutout sizes
		self.cutout_width = Decimal('0')
		self.cutout_height = Decimal('0')

		# Input data
		self.input_data = ""

		# Used for parsing
		self.reset_key_parameters()

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
			self.offset_x = 0
			self.offset_y = 0
		
	#=================================#
	#           Functions             #
	#=================================#


	# Key outline maker. Width and height in Units (U)
	# TODO: Fix this
	def make_key_outline(x, y, width, height):

		# Draw sides - top, bottom, left, right
		self.modelspace.add_line((x, y), (x + (width * self.unit_width), y))
		self.modelspace.add_line((x, y - (height * self.unit_height)), (x + (width * self.unit_width), y - (height * self.unit_height)))
		self.modelspace.add_line((x, y), (x, y - (height * self.unit_height)))
		self.modelspace.add_line((x + (width * self.unit_width), y), (x + (width * self.unit_width), y - (height * self.unit_height)))
		
	# Check if string is valid number
	# Credits to https://stackoverflow.com/questions/4138202/using-isdigit-for-floats
	def is_a_number(self, s):
		return_value = True
		try:
			test_float = float(s)
		except ValueError:
			return_value = False
		return return_value
				
	# Reset key default parameters
	def reset_key_parameters(self):
		
		self.current_width = Decimal('1')
		self.current_height = Decimal('1')
		self.current_width_secondary = Decimal('1')
		self.current_height_secondary = Decimal('1')
		self.current_rotx = Decimal('0')
		self.current_roty = Decimal('0')
		self.current_angle = Decimal('0')
		self.current_stab_angle = Decimal('0')
		self.current_cutout_angle = Decimal('0')
		self.current_offset_x = Decimal('0')
		self.current_offset_y = Decimal('0')
				
	# Modifies a point with rotation
	def rotate_point_around_anchor(self, x, y, anchor_x, anchor_y, angle):
		radius_squared = ((x - anchor_x) ** Decimal('2')) + ((y-anchor_y) ** Decimal('2'))
		radius = Decimal.sqrt(radius_squared)
		anglefrac = angle.as_integer_ratio()
		radian_qty = radians(anglefrac[0]/anglefrac[1])
		cos_result = Decimal(str(cos(radian_qty)))
		sin_result = Decimal(str(sin(radian_qty)))
		
		old_x = x - anchor_x
		old_y = y - anchor_y
		
		coord = matrix([float(old_x), float(old_y)])
		transform = matrix([[cos(radian_qty), -sin(radian_qty)], [sin(radian_qty), cos(radian_qty)]])
		result = transform * coord
		
		new_x = Decimal(str(result[0]))
		new_y = Decimal(str(result[1]))
		
		new_x += anchor_x
		new_y += anchor_y
		
		return (new_x, new_y)
		
	# Draw line segment rotated with respect to an anchor
	def draw_rotated_line(self, x1, y1, x2, y2, anchor_x, anchor_y, angle):
		coords_1 = self.rotate_point_around_anchor(x1, y1, anchor_x, anchor_y, angle)
		coords_2 = self.rotate_point_around_anchor(x2, y2, anchor_x, anchor_y, angle)
		
		self.modelspace.add_line((coords_1[0], coords_1[1]), (coords_2[0], coords_2[1]))
		
	# Draw arc rotated with respect to an anchor
	def draw_rotated_arc(self, x, y, anchor_x, anchor_y, radius, angle_start, angle_end, rotation):
		coords = self.rotate_point_around_anchor(x, y, anchor_x, anchor_y, rotation)
		self.modelspace.add_arc((coords[0], coords[1]), radius, float(angle_start + rotation), float(angle_end + rotation))
		
	# Stab cutout maker
	# The x and y are center, like this:
	#
	# -------
	# |     |
	# |  X  | -  -  -  Center Y of switch
	# |     |
	# |_   _|
	#   |_|

	def make_stab_cutout(self, x, y, anchor_x, anchor_y, angle):

		line_segments = []
		corners = []
		
		if (self.stab_type == "mx-simple"):
			# Rectangular simplified mx cutout.
			# A bit larger than stock to account for fillets.
			
			line_segments.append((Decimal('-3.375') + self.stab_radius, Decimal('6'), Decimal('3.375') - self.stab_radius, Decimal('6')))
			line_segments.append((Decimal('-3.375') + self.stab_radius, Decimal('-8'), Decimal('3.375') - self.stab_radius, Decimal('-8')))
			line_segments.append((Decimal('-3.375'), Decimal('6') - self.stab_radius, Decimal('-3.375'), Decimal('-8') + self.stab_radius))
			line_segments.append((Decimal('3.375'), Decimal('6') - self.stab_radius, Decimal('3.375'), Decimal('-8') + self.stab_radius))
			
			corners.append((Decimal('-3.375') + self.stab_radius, Decimal('6') - self.stab_radius, 90, 180))
			corners.append((Decimal('3.375') - self.stab_radius, Decimal('6') - self.stab_radius, 0, 90))
			corners.append((Decimal('-3.375') + self.stab_radius, Decimal('-8') + self.stab_radius, 180, 270))
			corners.append((Decimal('3.375') - self.stab_radius, Decimal('-8') + self.stab_radius, 270, 360))
			
		elif (self.stab_type == "large-cuts"):
			# Large, spacious 15x7 cutouts; 1mm from mx switch cutout top
			
			line_segments.append((Decimal('-3.5') + self.stab_radius, Decimal('6'), Decimal('3.5') - self.stab_radius, Decimal('6')))
			line_segments.append((Decimal('-3.5') + self.stab_radius, Decimal('-9'), Decimal('3.5') - self.stab_radius, Decimal('-9')))
			line_segments.append((Decimal('-3.5'), Decimal('6') - self.stab_radius, Decimal('-3.5'), Decimal('-9') + self.stab_radius))
			line_segments.append((Decimal('3.5'), Decimal('6') - self.stab_radius, Decimal('3.5'), Decimal('-9') + self.stab_radius))
			
			corners.append((Decimal('-3.5') + self.stab_radius, Decimal('6') - self.stab_radius, 90, 180))
			corners.append((Decimal('3.5') - self.stab_radius, Decimal('6') - self.stab_radius, 0, 90))
			corners.append((Decimal('-3.5') + self.stab_radius, Decimal('-9') + self.stab_radius, 180, 270))
			corners.append((Decimal('3.5') - self.stab_radius, Decimal('-9') + self.stab_radius, 270, 360))
			
		elif (self.stab_type == "alps-aek" or self.stab_type == "alps-at101"):
			# Rectangles 2.67 wide, 5.21 high.
			
			line_segments.append((Decimal('-1.335') + self.stab_radius, Decimal('-3.875'), Decimal('1.335') - self.stab_radius, Decimal('-3.875')))
			line_segments.append((Decimal('-1.335') + self.stab_radius, Decimal('-9.085'), Decimal('1.335') - self.stab_radius, Decimal('-9.085')))
			line_segments.append((Decimal('-1.335'), Decimal('-3.875') - self.stab_radius, Decimal('-1.335'), Decimal('-9.085') + self.stab_radius))
			line_segments.append((Decimal('1.335'), Decimal('-3.875') - self.stab_radius, Decimal('1.335'), Decimal('-9.085') + self.stab_radius))
			
			corners.append((Decimal('-1.335') + self.stab_radius, Decimal('-3.875') - self.stab_radius, 90, 180))
			corners.append((Decimal('1.335') - self.stab_radius, Decimal('-3.875') - self.stab_radius, 0, 90))
			corners.append((Decimal('-1.335') + self.stab_radius, Decimal('-9.085') + self.stab_radius, 180, 270))
			corners.append((Decimal('1.335') - self.stab_radius, Decimal('-9.085') + self.stab_radius, 270, 360))		
			
		else:
			print("Unsupported stab type.", file=sys.stderr)
			print("Stab types: mx-simple, large-cuts, alps-aek, alps-at101", file=sys.stderr)
			exit(1)
			
		for line in line_segments:
			self.draw_rotated_line(x + Decimal(str(line[0])), y + Decimal(str(line[1])), x + Decimal(str(line[2])), y + Decimal(str(line[3])), anchor_x, anchor_y, angle)
			
		for arc in corners:
			self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.stab_radius, arc[2], arc[3], angle)
			
	# Calls make stab cutout based on unit width and style
	def generate_stabs(self, center_x, center_y, angle, unitwidth):

		if (self.stab_type == "mx-simple" or self.stab_type == "large-cuts"):
			# Switch based on unit width
			# These spacings are based on official mx datasheets and deskthority measurements
			if (unitwidth >= 8): 
				# self.make_stab_cutout(x, y, anchor_x, anchor_y, angle)
				self.make_stab_cutout(center_x + Decimal('66.675'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('66.675'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 7): 
				self.make_stab_cutout(center_x + Decimal('57.15'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('57.15'), center_y, center_x, center_y, angle)
			elif (unitwidth == 6.25): 
				self.make_stab_cutout(center_x + Decimal('50'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('50'), center_y, center_x, center_y, angle)
			elif (unitwidth == 6): 
				self.make_stab_cutout(center_x + Decimal('38.1'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('57.15'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 3): 
				self.make_stab_cutout(center_x + Decimal('19.05'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('19.05'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 2): 
				self.make_stab_cutout(center_x + Decimal('11.938'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('11.938'), center_y, center_x, center_y, angle)
		elif (self.stab_type == "alps-aek"):
			# These are mostly based on measurements. 
			# If someone has datasheets, please let me know
			if (unitwidth >= 6.5): 
				self.make_stab_cutout(center_x + Decimal('45.3'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('45.3'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 6.25): 
				self.make_stab_cutout(center_x + Decimal('41.86'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('41.86'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 2): 
				self.make_stab_cutout(center_x + Decimal('14'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('14'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 1.75): 
				self.make_stab_cutout(center_x + Decimal('12'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('12'), center_y, center_x, center_y, angle)
		elif (self.stab_type == "alps-at101"):
			# These are mostly based on measurements. 
			# If someone has datasheets, please let me know
			if (unitwidth >= 6.5): 
				self.make_stab_cutout(center_x + Decimal('45.3'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('45.3'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 6.25): 
				self.make_stab_cutout(center_x + Decimal('41.86'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('41.86'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 2.75): 
				self.make_stab_cutout(center_x + Decimal('20.5'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('20.5'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 2): 
				self.make_stab_cutout(center_x + Decimal('14'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('14'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 1.75): 
				self.make_stab_cutout(center_x + Decimal('12'), center_y, center_x, center_y, angle)
				self.make_stab_cutout(center_x - Decimal('12'), center_y, center_x, center_y, angle)
		
	# Acoustics cuts maker

	def make_acoustic_cutout(self, x, y, angle):
			
		line_segments = []
		corners = []
		
		if (self.cutout_type == "mx" or self.cutout_type == "alps"):
			
			line_segments.append((Decimal('-1') + self.stab_radius, (self.cutout_height / Decimal('2')), Decimal('1') - self.stab_radius, (self.cutout_height / Decimal('2'))))
			line_segments.append((Decimal('-1') + self.stab_radius, (self.cutout_height / -Decimal('2')), Decimal('1') - self.stab_radius, (self.cutout_height / -Decimal('2'))))
			line_segments.append((Decimal('-1'), (self.cutout_height / Decimal('2')) - self.stab_radius, Decimal('-1'), (self.cutout_height / -Decimal('2')) + self.stab_radius))
			line_segments.append((Decimal('1'), (self.cutout_height / Decimal('2')) - self.stab_radius, Decimal('1'), (self.cutout_height / -Decimal('2')) + self.stab_radius))
			
			corners.append((Decimal('-1') + self.stab_radius, (self.cutout_height / Decimal('2')) - self.stab_radius, 90, 180))
			corners.append((Decimal('1') - self.stab_radius, (self.cutout_height / Decimal('2')) - self.stab_radius, 0, 90))
			corners.append((Decimal('-1') + self.stab_radius, (self.cutout_height / -Decimal('2')) + self.stab_radius, 180, 270))
			corners.append((Decimal('1') - self.stab_radius, (self.cutout_height / -Decimal('2')) + self.stab_radius, 270, 360))
			
		for line in line_segments:
			self.draw_rotated_line(x + Decimal(str(line[0])), y + Decimal(str(line[1])), x + Decimal(str(line[2])), y + Decimal(str(line[3])), anchor_x, anchor_y, angle)
			
		for arc in corners:
			self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.stab_radius, arc[2], arc[3], angle)
		
	# Draw switch cutout
	def draw_switch_cutout(self, mm_center_x, mm_center_y, angle):
		# Make some variables for the sake of legibility
		mm_y_top = mm_center_y + (self.cutout_height / Decimal('2'));
		mm_y_bottom = mm_center_y - (self.cutout_height / Decimal('2'));
		mm_x_left = mm_center_x - (self.cutout_width / Decimal('2'));
		mm_x_right = mm_center_x + (self.cutout_width / Decimal('2'));
		
		# First draw the line segments: top, bottom, left, right
		self.draw_rotated_line(mm_x_left + self.cutout_radius, mm_y_top, mm_x_right - self.cutout_radius, mm_y_top, 
		mm_center_x, mm_center_y, angle)
		self.draw_rotated_line(mm_x_left + self.cutout_radius, mm_y_bottom, mm_x_right - self.cutout_radius, mm_y_bottom, 
		mm_center_x, mm_center_y, angle)
		self.draw_rotated_line(mm_x_left, mm_y_top - self.cutout_radius, mm_x_left, mm_y_bottom + self.cutout_radius, 
		mm_center_x, mm_center_y, angle)
		self.draw_rotated_line(mm_x_right, mm_y_top - self.cutout_radius, mm_x_right, mm_y_bottom + self.cutout_radius, 
		mm_center_x, mm_center_y, angle)
		
		# Now render corner arcs: top left, top right, bottom left, bottom right
		self.draw_rotated_arc(mm_x_left + self.cutout_radius, mm_y_top - self.cutout_radius, mm_center_x, mm_center_y, self.cutout_radius, Decimal('90'), Decimal('180'), angle)
		self.draw_rotated_arc(mm_x_right - self.cutout_radius, mm_y_top - self.cutout_radius, mm_center_x, mm_center_y, self.cutout_radius, Decimal('0'), Decimal('90'), angle)
		self.draw_rotated_arc(mm_x_left + self.cutout_radius, mm_y_bottom + self.cutout_radius, mm_center_x, mm_center_y, self.cutout_radius, Decimal('180'), Decimal('270'), angle)
		self.draw_rotated_arc(mm_x_right - self.cutout_radius, mm_y_bottom + self.cutout_radius, mm_center_x, mm_center_y, self.cutout_radius, Decimal('270'), Decimal('360'), angle)
		
		
	# Use the functions above to render an entire switch - Cutout, stabs, and all
	def render_switch(self, switch):
	
		mm_x = Decimal('0')
		mm_y = Decimal('0')
		
		# Coord differs for regular vs rotated
		if (switch.rotx != 0 or switch.roty != 0 or switch.angle != 0):
			# rotx and roty are the raw base coords for anchor
			# Then, upper left is offset from there
			mm_x = (switch.rotx + switch.offset_x) * self.unit_width
			mm_y = (-switch.roty - switch.offset_y) * self.unit_height
			
			# Confirmed coords are correct at this point
			# Something going haywire after this
			
		else:
			# Otherwise, derive mm based on x and y in units
			mm_x = switch.x * self.unit_width
			mm_y = switch.y * self.unit_height
			
		# Then, derive the center of the switch based on width and height
		mm_center_x = mm_x + ((switch.width / Decimal('2')) * self.unit_width)
		mm_center_y = mm_y - ((switch.height / Decimal('2')) * self.unit_height)
		
		# Then, rotate the points if angle != 0
		if (switch.angle != Decimal('0')):
			rotated_upper_left_coords = self.rotate_point_around_anchor(mm_x, mm_y, switch.rotx, switch.roty, switch.angle)
			rotated_central_coords = self.rotate_point_around_anchor(mm_center_x, mm_center_y, switch.rotx, switch.roty, switch.angle)
			
			mm_x = rotated_upper_left_coords[0]
			mm_y = rotated_upper_left_coords[1]
			
			mm_center_x = rotated_central_coords[0]
			mm_center_y = rotated_central_coords[1]
		
		# Draw main switch cutout
		self.draw_switch_cutout(mm_center_x, mm_center_y, switch.angle + switch.cutout_angle)
		
		# Adjust width for vertically tall keys, and generate stabs
		apparent_width = switch.width;
		if (switch.width < switch.height):
			apparent_width = switch.height;
		
		self.generate_stabs(mm_center_x, mm_center_y, switch.angle + switch.stab_angle, apparent_width)
		

	# Generate switch cutout sizes
	def initialize_variables(self):
		if (self.cutout_type == "mx"):
			self.cutout_width = Decimal('14');
			self.cutout_height = Decimal('14');
		elif (self.cutout_type == "alps"):
			self.cutout_width = Decimal('15.50');
			self.cutout_height = Decimal('12.80');
		else:
			print("Unsupported cutout type.", file=sys.stderr)
			print("Supported: mx, alps", file=sys.stderr)
			exit(1)
		
		# Check if values legal

		# Cutout radius: The fillet radius ( 0 <= x <= 1/2 width or height)
		if (self.cutout_radius < 0 or self.cutout_radius > (self.cutout_width/2) or self.cutout_radius > (self.cutout_height/2)) :
			print("Radius must be between 0 and half the cutout width/height.", file=sys.stderr)
			exit(1)

		# Unit size ( 0 <= x <= inf, cap at 1000 for now )
		if (self.unit_width < 0 or self.unit_width > 1000):
			print("Unit size must be between 0 and 1000", file=sys.stderr)
			exit(1)
		if (self.unit_height < 0 or self.unit_height > 1000):
			print("Unit size must be between 0 and 1000", file=sys.stderr)
			exit(1)

		# Check if output method is legal
		if (self.output_method != "stdout" and self.output_method != "file"):
			print("Unsupported output method specified", file=sys.stderr)
			exit(1)

	def generate_plate(self):

		# Init vars
		self.initialize_variables()

		# If debug matrix is on, make sth generic
		if (self.debug_use_generic_matrix):
			self.input_data = self.debug_matrix_data
		# Otherwise, take from stdin
		else:
			self.input_data = sys.stdin.read()
			
		# Sanitize by removing \" (KLE's literal " for a label)
		#self.input_data = self.input_data.replace('\n', '')
		#self.input_data = self.input_data.replace(r'\"', '')

		# TODO: Filter out improper quotes from " being in a label!

		if (self.debug_log):
			print("Filtered input data:")
			print(self.input_data)
			print("")

		# Parse KLE data

		self.current_x = Decimal('0')
		self.current_y = Decimal('0')
		max_width = Decimal('0')
		max_height = Decimal('0')

		all_switches = []

		json_data = json5.loads('[' + self.input_data + ']')

		for row in json_data:
			if (self.debug_log):
				print (">>> ROW BEGIN")
				print (str(row))
			
			# KLE standard supports first row being metadata.
			# If it is, ignore.
			if isinstance(row, dict):
				if (self.debug_log):
					print ("!!! Row is metadata. Skip.")
				continue
			for key in row:
				# The "key" can either be a legend (actual key) or dictionary of data (for succeeding key).
				
				# If it's just a string, it's just a key. Create one and add to list
				if isinstance(key, str):
				
					# First, we simply make the switch
					current_switch = self.Switch(self.current_x, self.current_y)
					
					# For x and y offset, check if any rotation spec is set.
					if (self.current_rotx != 0 or self.current_roty != 0 or self.current_angle != 0):
						# If set, store the value
						current_switch.offset_x = self.current_offset_x
						current_switch.offset_y = self.current_offset_y
					else:
						# Otherwise, append
						self.current_x += self.current_offset_x
						self.current_y -= self.current_offset_y
						current_switch.x += self.current_offset_x
						current_switch.y -= self.current_offset_y
						self.current_offset_x = Decimal('0')
						self.current_offset_y = Decimal('0')
					
					# Then, adjust the x coord for next switch
					self.current_x += self.current_width
					# If this is a record, update properly
					if (max_width < self.current_x):
						max_width = self.current_x
					if (max_height > self.current_y - Decimal('1')):
						max_height = self.current_y - Decimal('1')
					
					# And we adjust the fields as necessary.
					# These default to 1 unless edited by a data field preceding
					current_switch.width = self.current_width
					current_switch.height = self.current_height
					current_switch.width_secondary = self.current_width_secondary
					current_switch.height_secondary = self.current_height_secondary
					current_switch.rotx = self.current_rotx
					current_switch.roty = self.current_roty
					current_switch.angle = self.current_angle
					current_switch.stab_angle = self.current_stab_angle
					current_switch.cutout_angle = self.current_cutout_angle
					
					# Deal with some certain cases
					
					# For example, vertical keys created by stretching height to be larger than width
					# The key's cutout angle and stab angle should be offset by 90 degrees to compensate.
					# This effectively transforms the key to a vertical
					# This also handles ISO
					if (self.current_width < self.current_height and self.current_height >= 1.75):
						current_switch.cutout_angle -= Decimal('90')
						current_switch.stab_angle -= Decimal('90')
					
					all_switches.append(current_switch)
					
					# Reset the fields to their defaults
					self.reset_key_parameters()
					
				# Otherwise, it's a data dictionary. We must parse it properly
				else:
					for i in key:
						# i = The dictionary key. Not the keyboard kind of key
						# j = The corresponding value.
						j = key[i]
						
						# Large if-else chain to set params
						if (str(i) == "w"):
							# w = Width
							self.current_width = Decimal(str(j))
							
						elif (str(i) == "h"):
							# h = Height
							self.current_height = Decimal(str(j))
							
						elif (str(i) == "w2"):
							# w2 = Secondary width
							self.current_width_secondary = Decimal(str(j))
							
						elif (str(i) == "h2"):
							# h2 = Secondary height
							self.current_height_secondary = Decimal(str(j))
							
						elif (str(i) == "rx"):
							# rx = Rotation anchor x
							self.current_rotx = Decimal(str(j))
							
						elif (str(i) == "ry"):
							# ry = Rotation anchor y
							self.current_roty = Decimal(str(j))
							
						elif (str(i) == "r"):
							# r = Rotation angle OPPOSITE OF typical counterclockwise-from-xpositive
							self.current_angle = -Decimal(str(j))
							
						elif (str(i) == "_rs"):
							# _rs = Rotation angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
							self.current_stab_angle = -Decimal(str(j))
							
						elif (str(i) == "_rc"):
							# _rs = Switch cutout angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
							self.current_cutout_angle = -Decimal(str(j))
							
						if (str(i) == "x"):
							# x = X offset for next keys OR offset from rotation anchor (seriously kle?)
							self.current_offset_x = Decimal(str(j))
							
						elif (str(i) == "y"):
							# y = Y offset for next keys OR offset from rotation anchor (seriously kle?)
							self.current_offset_y = Decimal(str(j))
			# Finished row
			self.current_y -= Decimal('1')
			self.current_x = Decimal('0')

		# At this point, the keys are built.
		# Render each one by one. 
		for switch in all_switches:
			self.render_switch(switch)

		# Draw outer bounds - top, bottom, left, right
		self.modelspace.add_line((0, 0), (max_width * self.unit_height, 0))
		self.modelspace.add_line((0, max_height * self.unit_height), (max_width * self.unit_height, max_height * self.unit_height))
		self.modelspace.add_line((0, 0), (0, max_height * self.unit_height))
		self.modelspace.add_line((max_width * self.unit_height, 0), (max_width * self.unit_height, max_height * self.unit_height))
			
		if (self.debug_log):
			print("Complete! Saving plate to specified output")

		if (self.output_method == "file"):
			self.plate.saveas(self.filename + '.dxf')
		else:
			self.plate.write(sys.stdout)
			
if __name__ == "__main__":
	gen = PlateGenerator()
	gen.generate_plate()