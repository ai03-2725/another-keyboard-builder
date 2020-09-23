#=================================#
#        Plate Generator          #
#=================================#

# By ai03
# Credits to
# Amtra5, Mxblue, Bakingpy,
# Senter, Pwner, Kevinplus, Deskthority Wiki,
# and any others I may have missed

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
import argparse

from mpmath import *
from decimal import *

class PlateGenerator(object):

	#init
	def __init__(self, arg_ct, arg_cr, arg_st, arg_sr, arg_at, arg_ar, arg_uw, arg_uh, arg_db):

		# Set up decimal and mpmath
		getcontext().prec = 50
		mp.dps = 50
		mp.pretty = True

		# Create blank dxf workspace
		self.plate = ezdxf.new(dxfversion='AC1024')
		self.modelspace = self.plate.modelspace()

		# Cutout type: mx, mx-slightly-wider, alps
		self.cutout_type = arg_ct

		# Cutout radius: The fillet radius ( 0 <= x <= 1/2 cutout width or height )
		try:
			self.cutout_radius = Decimal(arg_cr)
		except:
			raise ValueError

		# Stab type: mx-simple, large-cuts, alps-aek, alps-at101
		self.stab_type = arg_st

		# Stab radius: The fillet radius for stab cutouts ( 0 <= x <= 1 )
		try:
			self.stab_radius = Decimal(arg_sr)
		except:
			raise ValueError

		# Acoustic cuts: The cutouts typically found on high end plates beside the switches.
		# This script only handles the thin short cuts vertically beside each switch cut, not the large ones, i.e. between fn row and alphas.
		# none = disabled, typical = 1.5-1.75U only, extreme = On 1.5-2.75U
		self.acoustics_type = arg_at

		# Acoustic radius: Fillet radius for cuts mentioned above.
		try:
			self.acoustics_radius = Decimal(arg_ar)
		except:
			raise ValueError

		# Unit size (i.e. 1U = 19.05mm). ( 0 <= x <= inf, cap at 1000 for now )
		try:
			self.unit_width = Decimal(arg_uw)
		except:
			raise ValueError
		try:
			self.unit_height = Decimal(arg_uh)
		except:
			raise ValueError
		

		#== Debug parameters ==#

		# Tell user everything about what's going on and spam the console?
		self.debug_log = arg_db

		# Runtime vars that are often systematically changed or reset

		# Current x/y coordinates
		self.current_x = Decimal('0')
		self.current_y = Decimal('0')
		self.max_width = Decimal('0')
		self.max_height = Decimal('0')

		# Cutout sizes
		self.cutout_width = Decimal('0')
		self.cutout_height = Decimal('0')

		# Used for parsing
		self.reset_key_parameters()
		self.current_rotx = "NONE"
		self.current_roty = "NONE"
		self.current_angle = "NONE"
		
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
		self.current_stab_angle = Decimal('0')
		self.current_cutout_angle = Decimal('0')
		self.current_offset_x = Decimal('0')
		self.current_offset_y = Decimal('0')
		self.current_deco = False
		
	# Reset key default parameters for rotated zone
	def reset_rotated_key_parameters(self):
		
		self.current_width = Decimal('1')
		self.current_height = Decimal('1')
		self.current_width_secondary = Decimal('1')
		self.current_height_secondary = Decimal('1')
		self.current_stab_angle = Decimal('0')
		self.current_cutout_angle = Decimal('0')
		self.current_deco = False
		self.current_rotx = "UNCHANGED"
		self.current_roty = "UNCHANGED"
		self.current_angle = "UNCHANGED"
				
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
		elif (self.stab_type == "none"):
			pass

		else:
			print("Unsupported stab type.", file=sys.stderr)
			print("Stab types: mx-simple, large-cuts, alps-aek, alps-at101, none", file=sys.stderr)
			#exit(1)
			return(2)
			
		for line in line_segments:
			self.draw_rotated_line(x + Decimal(str(line[0])), y + Decimal(str(line[1])), x + Decimal(str(line[2])), y + Decimal(str(line[3])), anchor_x, anchor_y, angle)
			
		for arc in corners:
			self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.stab_radius, arc[2], arc[3], angle)
			
	# Acoustics cuts maker

	def make_acoustic_cutout(self, x, y, anchor_x, anchor_y, angle):
			
		line_segments = []
		corners = []
		
		if (self.cutout_type == "mx" or self.cutout_type == "alps"):
			
			line_segments.append((Decimal('-1') + self.acoustics_radius, (self.cutout_height / Decimal('2')), Decimal('1') - self.acoustics_radius, (self.cutout_height / Decimal('2'))))
			line_segments.append((Decimal('-1') + self.acoustics_radius, (self.cutout_height / -Decimal('2')), Decimal('1') - self.acoustics_radius, (self.cutout_height / -Decimal('2'))))
			line_segments.append((Decimal('-1'), (self.cutout_height / Decimal('2')) - self.acoustics_radius, Decimal('-1'), (self.cutout_height / -Decimal('2')) + self.acoustics_radius))
			line_segments.append((Decimal('1'), (self.cutout_height / Decimal('2')) - self.acoustics_radius, Decimal('1'), (self.cutout_height / -Decimal('2')) + self.acoustics_radius))
			
			corners.append((Decimal('-1') + self.acoustics_radius, (self.cutout_height / Decimal('2')) - self.acoustics_radius, 90, 180))
			corners.append((Decimal('1') - self.acoustics_radius, (self.cutout_height / Decimal('2')) - self.acoustics_radius, 0, 90))
			corners.append((Decimal('-1') + self.acoustics_radius, (self.cutout_height / -Decimal('2')) + self.acoustics_radius, 180, 270))
			corners.append((Decimal('1') - self.acoustics_radius, (self.cutout_height / -Decimal('2')) + self.acoustics_radius, 270, 360))
			
		for line in line_segments:
			self.draw_rotated_line(x + Decimal(str(line[0])), y + Decimal(str(line[1])), x + Decimal(str(line[2])), y + Decimal(str(line[3])), anchor_x, anchor_y, angle)
			
		for arc in corners:
			self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.acoustics_radius, arc[2], arc[3], angle)
		
			
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
				if (self.acoustics_type == "extreme"):
					self.make_acoustic_cutout(center_x + Decimal('18.25'), center_y, center_x, center_y, angle)
					self.make_acoustic_cutout(center_x - Decimal('18.25'), center_y, center_x, center_y, angle)
			elif (unitwidth >= 1.5):
				if (self.acoustics_type == "typical" or (self.acoustics_type == "extreme")):
					self.make_acoustic_cutout(center_x + Decimal('11.6'), center_y, center_x, center_y, angle)
					self.make_acoustic_cutout(center_x - Decimal('11.6'), center_y, center_x, center_y, angle)
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
		

	# Draw switch cutout
	def draw_switch_cutout(self, x, y, angle):
	
		line_segments = []
		corners = []
		
		anchor_x = x;
		anchor_y = y;

		standard_cutout_types = ["mx", "mx-slightly-wider", "alps", "omron", "kailh-choc-CPG1350", "kailh-choc-mini-CPG1232"]			

		if (self.cutout_type in standard_cutout_types):
			line_segments.append(((self.cutout_width / -Decimal('2')) + self.cutout_radius, (self.cutout_height / Decimal('2')), (self.cutout_width / Decimal('2')) - self.cutout_radius, (self.cutout_height / Decimal('2'))))
			line_segments.append(((self.cutout_width / -Decimal('2')) + self.cutout_radius, (self.cutout_height / -Decimal('2')), (self.cutout_width / Decimal('2')) - self.cutout_radius, (self.cutout_height / -Decimal('2'))))
			line_segments.append(((self.cutout_width / -Decimal('2')), (self.cutout_height / Decimal('2')) - self.cutout_radius, (self.cutout_width / -Decimal('2')), (self.cutout_height / -Decimal('2')) + self.cutout_radius))
			line_segments.append(((self.cutout_width / Decimal('2')), (self.cutout_height / Decimal('2')) - self.cutout_radius, (self.cutout_width / Decimal('2')), (self.cutout_height / -Decimal('2')) + self.cutout_radius))
			
			corners.append(((self.cutout_width / -Decimal('2')) + self.cutout_radius, (self.cutout_height / Decimal('2')) - self.cutout_radius, 90, 180))
			corners.append(((self.cutout_width / Decimal('2')) - self.cutout_radius, (self.cutout_height / Decimal('2')) - self.cutout_radius, 0, 90))
			corners.append(((self.cutout_width / -Decimal('2')) + self.cutout_radius, (self.cutout_height / -Decimal('2')) + self.cutout_radius, 180, 270))
			corners.append(((self.cutout_width / Decimal('2')) - self.cutout_radius, (self.cutout_height / -Decimal('2')) + self.cutout_radius, 270, 360))
			
			for line in line_segments:
				self.draw_rotated_line(x + Decimal(str(line[0])), y + Decimal(str(line[1])), x + Decimal(str(line[2])), y + Decimal(str(line[3])), anchor_x, anchor_y, angle)
				
			for arc in corners:
				self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.cutout_radius, arc[2], arc[3], angle)
		
		# TODO: Add switchtop removal cutouts, hardcoded radius to 0.5
		#elif (self.cutout_type == "mx-topremoval-simple"):
		#	line_segments.append((-Decimal('7.80') + self.cutout_radius, -Decimal('7')), (Decimal('7.80') - self.cutout_radius, -Decimal('7')))
		
	# Use the functions above to render an entire switch - Cutout, stabs, and all
	def render_switch(self, switch):
	
		mm_x = Decimal('0')
		mm_y = Decimal('0')
		
		if(self.debug_log):
			print("RX: " + str(switch.rotx))
			print("RY: " + str(switch.roty))
			print("Angle: " + str(switch.angle))
			print("Offset X: " + str(switch.offset_x))
			print("Offset Y: " + str(switch.offset_y))
			print("===")
			
		# Coord differs for regular vs rotated
		if ((switch.rotx != "NONE") and (switch.roty != "NONE") or switch.angle != "NONE"):
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
			switch.angle = Decimal("0")
			
		# Then, derive the center of the switch based on width and height
		mm_center_x = mm_x + ((switch.width / Decimal('2')) * self.unit_width)
		mm_center_y = mm_y - ((switch.height / Decimal('2')) * self.unit_height)
		
		# Then, rotate the points if angle != 0
		if (switch.angle != Decimal('0')):
		
			# This part is the issue
		
			rotated_upper_left_coords = self.rotate_point_around_anchor(mm_x, mm_y, (switch.rotx * self.unit_width), -(switch.roty * self.unit_height), switch.angle)
			rotated_central_coords = self.rotate_point_around_anchor(mm_center_x, mm_center_y, (switch.rotx * self.unit_width), -(switch.roty * self.unit_height), switch.angle)
			
			mm_x = rotated_upper_left_coords[0]
			mm_y = rotated_upper_left_coords[1]
			
			mm_center_x = rotated_central_coords[0]
			mm_center_y = rotated_central_coords[1]
			
			# Do some calculations to see if a rotated switch exceeds current max boundaries
			
			unrotated_x = (switch.rotx + switch.offset_x) * self.unit_width
			unrotated_y = (-switch.roty - switch.offset_y) * self.unit_height
			
			corners = []
			corners.append((unrotated_x, unrotated_y))
			corners.append((unrotated_x + (switch.width * self.unit_width), unrotated_y))
			corners.append((unrotated_x, unrotated_y - (switch.height * self.unit_height)))
			corners.append((unrotated_x + (switch.width * self.unit_width), unrotated_y - (switch.height * self.unit_height)))
			
			for corner in corners:
				rotated_corner = self.rotate_point_around_anchor(corner[0], corner[1], mm_center_x, mm_center_y, switch.angle)
				
				if (rotated_corner[0] > self.max_width):
					self.max_width = rotated_corner[0];
				if (rotated_corner[1] < self.max_height):
					self.max_height = rotated_corner[1];
				
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
		elif (self.cutout_type == "mx-slightly-wider"):
			self.cutout_width = Decimal('15');
			self.cutout_height = Decimal('14');
		elif (self.cutout_type == "alps"):
			self.cutout_width = Decimal('15.50');
			self.cutout_height = Decimal('12.80');
		elif (self.cutout_type == "omron"):
			self.cutout_width = Decimal('13.50');
			self.cutout_height = Decimal('13.50');
		elif (self.cutout_type == "kailh-choc-CPG1350"):
                        # Datasheet lists 13.8x13.8 with no tolerances, so
                        # using tolerances off choc-mini datasheet
			self.cutout_width = Decimal('13.82');
			self.cutout_height = Decimal('13.82');
		elif (self.cutout_type == "kailh-choc-mini-CPG1232"):
			self.cutout_width = Decimal('13.52');
			self.cutout_height = Decimal('12.52');
		else:
			print("Unsupported cutout type.", file=sys.stderr)
			print("Supported: mx, alps, omron", file=sys.stderr)
			#exit(1)
			return 3
		
		# Check if values legal

		# Cutout radius: The fillet radius ( 0 <= x <= 1/2 width or height)
		if ((self.cutout_radius < 0) or (self.cutout_radius > (self.cutout_width/2)) or (self.cutout_radius > (self.cutout_height/2))) :
			print("Radius must be between 0 and half the cutout width/height.", file=sys.stderr)
			#exit(1)
			return 4

		# Unit size ( 0 <= x <= inf, cap at 1000 for now )
		if (self.unit_width < 0 or self.unit_width > 1000):
			print("Unit size must be between 0 and 1000", file=sys.stderr)
			#exit(1)
			return 5
			
		if (self.unit_height < 0 or self.unit_height > 1000):
			print("Unit size must be between 0 and 1000", file=sys.stderr)
			#exit(1)
			return 5
			
		if (self.stab_radius < 0 or self.stab_radius > 5):
			return 6
		if (self.acoustics_radius < 0 or self.acoustics_radius > 5):
			return 7
		
			
		return 0
			
	def generate_plate(self, file, input_data=None):

		# Init vars
		init_code = self.initialize_variables()
		if (init_code != 0):
			return init_code
		
		# If debug matrix is on, make sth generic
		if not input_data:
			input_data = self.debug_matrix_data
			
		# Sanitize by removing \" (KLE's literal " for a label)
		#input_data = input_data.replace('\n', '')
		#input_data = input_data.replace(r'\"', '')

		# TODO: Filter out improper quotes from " being in a label!

		if (self.debug_log):
			print("Filtered input data:")
			print(input_data)
			print("")

		# Parse KLE data
		all_switches = []
		rotation_zone = False
		
		try:
			json_data = json5.loads('[' + input_data + ']')
		except(ValueError):
			#print("Invalid KLE data", file=sys.stderr)
			return(1)

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
				
					if (self.current_deco):
						self.reset_key_parameters()
						continue
				
					# First, we simply make the switch
					current_switch = self.Switch(self.current_x, self.current_y)
					
					# For x and y offset, check if any rotation spec is set.
					if (rotation_zone or self.current_rotx != "NONE" or self.current_roty != "NONE" or self.current_angle != "NONE"):
					
						if (not rotation_zone):
							# If first time entering rotated syntax, init values for rotation vars
							if (self.current_rotx == "NONE"):
								self.current_rotx = Decimal("0")
							if (self.current_roty == "NONE"):
								self.current_roty = Decimal("0")
							if (self.current_angle == "NONE"):
								self.current_angle = Decimal("0")
							rotation_zone = True
					
						# This means we RETAIN rx or ry from previous. How awful of a syntax. Seriously KLE?
						
						# Credits to Peioris to reverse engineering the syntax:
						
							# when parsing properties, you have to check the r, rx, ry values wrt to the previous values

							# did rx and ry change? current_x = rx; current_y = ry 
							# did rx change but not ry? current_x = rx; current_y = 0
							# did r change but rx, ry did not? current_x = current_rx
							
							# It appears that in rotation syntax, the following terrible decisions are made:
							
							# - If a y: is present, it is added to whatever existing value is present (i.e. y:0.5 drops the key and any successors down 0.5U.) 
							#   This effectively signifies the beginning of a row, since all successor keys will be placed with this y as a guideline.
							# 	Also, a y: will reset the current x offset to 0.
							# - If a x: is present without a y:, it is appended to the previous key's position (i.e. x:0.5 skips 0.5u before placing the next key in same rotated row
							# - If a rx: or ry: is updated, all previous x: and y: references are ignored.
							#   > If rx: is updated and ry is not given, ry = 0 by default.
							#   > Similarly, if ry: is updated and rx is not given, rx = 0 by default.
							# - If r: is updated, rx: and ry: are presumed 0; however, the previous x: is reset, y: offset value is not discarded (i.e. if y was at 5 before, it will be 6 now)
					
						# Check for rx or ry changes
						if (self.current_rotx != "UNCHANGED"):
							self.current_x = Decimal("0")
							self.current_offset_y = Decimal("0")
							
							if (self.current_roty == "UNCHANGED"):
								self.current_roty = Decimal("0")
						else:
							self.current_rotx = all_switches[-1].rotx
								
						if (self.current_roty != "UNCHANGED"):
							self.current_x = Decimal("0")
							self.current_offset_y = Decimal("0")
							
							if (self.current_rotx == "UNCHANGED"):
								self.current_rotx = Decimal("0")
						else:
							self.current_roty = all_switches[-1].roty
								
						# Check for r changes
						if (self.current_angle != "UNCHANGED"):
							self.current_offset_y -= Decimal("1")
							self.current_offset_x = Decimal("0")		
						else:
							self.current_angle = all_switches[-1].angle
					
						# - If a y: is present, reset x offset
						if (self.current_offset_y != 0):
							self.current_offset_x = Decimal("0")
							self.current_offset_y -= self.current_offset_y
							current_switch.offset_y -= self.current_offset_y
						# Otherwise, obtain existing offset from previous switch
						else:
							current_switch.offset_x = all_switches[-1].offset_x + Decimal("1")
							
						# Append data for x offset for current switch
						# self.current_offset_x += self.current_offset_x
						current_switch.offset_x += self.current_offset_x
						
						# Check and see if it's a y record
						if (self.max_height > -self.current_roty - self.current_offset_y):
							self.max_height = -self.current_roty - self.current_offset_y
							
						# Then, adjust the x coord for next switch
						self.current_offset_x += self.current_width
						
					else:
						# Otherwise, append
						self.current_x += self.current_offset_x
						self.current_y -= self.current_offset_y
						current_switch.x += self.current_offset_x
						current_switch.y -= self.current_offset_y
						self.current_offset_x = Decimal('0')
						self.current_offset_y = Decimal('0')
						
						# Check and see if it's a y record
						if (self.max_height > self.current_y - self.current_height):
							self.max_height = self.current_y - self.current_height
					
						# Then, adjust the x coord for next switch
						self.current_x += self.current_width
						
					# If this is a x record, update properly
					if (self.max_width < self.current_x):
						self.max_width = self.current_x
					
					
					# And we adjust the fields as necessary.
					# These default to 1, 0, etc unless edited by a data field preceding
					current_switch.width = self.current_width
					current_switch.height = self.current_height
					current_switch.width_secondary = self.current_width_secondary
					current_switch.height_secondary = self.current_height_secondary
					current_switch.stab_angle = self.current_stab_angle
					current_switch.cutout_angle = self.current_cutout_angle
					current_switch.rotx = self.current_rotx
					current_switch.roty = self.current_roty
					current_switch.angle = self.current_angle
					
					
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
					if (rotation_zone):
						self.reset_rotated_key_parameters()
					else:
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
							
						elif (str(i) == "x"):
							# x = X offset for next keys OR offset from rotation anchor (seriously kle?)
							self.current_offset_x = Decimal(str(j))
							
						elif (str(i) == "y"):
							# y = Y offset for next keys OR offset from rotation anchor (seriously kle?)
							self.current_offset_y = Decimal(str(j))
						
						elif (str(i) == "d"):
							# Key is decoration. 
							self.current_deco = True
						
			# Finished row
			if (rotation_zone):
				self.current_offset_y -= Decimal("1")
				self.current_offset_x = Decimal("0")
			else:
				self.current_y -= Decimal('1')
				self.current_x = Decimal('0')
			

		# At this point, the keys are built.
		
		# Adjust max width/height from units to mm
		
		self.max_width = self.max_width * self.unit_width
		self.max_height = self.max_height * self.unit_height
		
		# Render each one by one. 
		for switch in all_switches:
			self.render_switch(switch)

		# Draw outer bounds - top, bottom, left, right
		self.modelspace.add_line((0, 0), (self.max_width, 0))
		self.modelspace.add_line((0, self.max_height), (self.max_width, self.max_height))
		self.modelspace.add_line((0, 0), (0, self.max_height))
		self.modelspace.add_line((self.max_width, 0), (self.max_width, self.max_height))
			
		if (self.debug_log):
			print("Complete!")
			return 0
			

		if (file == "stdout"):
			self.plate.write(sys.stdout)
		else:
			self.plate.write(file)
		return 0
			
		
			
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Create a plate DXF based on KLE raw data.')
	
	# Note: The args will be fed into Decimal(), which takes strings
	
	parser.add_argument("-ct", "--cutout-type", help="Switch cutout type. Supported: mx, mx-slightly-wider, alps, omron; Default: mx", type=str, default='mx')
	parser.add_argument("-cr", "--cutout-radius", help="Switch cutout fillet radius. Default: 0.5", type=str, default='0.5')
	parser.add_argument("-st", "--stab-type", help="Stabilizer type. Supported: mx-simple, large-cuts, alps-aek, alps-at101; Default: mx-simple", type=str, default='mx-simple')
	parser.add_argument("-sr", "--stab-radius", help="Stabilizer cutout fillet radius. Default: 0.5", type=str, default='0.5')
	parser.add_argument("-at", "--acoustics-type", help="Acoustic cutouts type. Supported: none, typical, extreme; Default: none", type=str, default='none')
	parser.add_argument("-ar", "--acoustics-radius", help="Acoustic cutouts fillet radius. Default: 0.5", type=str, default='0.5')
	parser.add_argument("-uw", "--unit-width", help="Key unit width. Default: 19.05", type=str, default='19.05')
	parser.add_argument("-uh", "--unit-height", help="Key unit height. Default: 19.05", type=str, default='19.05')
	#parser.add_argument("-om", "--output-method", help="The save method for data. Supported: stdout, file; Default: stdout", type=str, default='stdout')
	#parser.add_argument("-of", "--output-file", help="Output file name if using file output-method. Default: plate.dxf", type=str, default='plate.dxf')	
	parser.add_argument("--debug-log", help="Spam output with useless info.", action="store_true", default = False)
	
	args = parser.parse_args()
	
	gen = PlateGenerator(args.cutout_type, args.cutout_radius, args.stab_type, args.stab_radius, args.acoustics_type, args.acoustics_radius, 
	args.unit_width, args.unit_height, args.debug_log)
	
	input_data = sys.stdin.read()
	gen.generate_plate("stdout", input_data)
