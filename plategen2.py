#=================================#
#        Plate Generator 2        #
#=================================#

# By ai03
# Credits to
# Amtra5, Mxblue, Bakingpy,
# Senter, Pwner, Kevinplus, 
# Peioris, Deskthority Wiki,
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

		# Cutout type: mx, alps
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

		# The debug_log flag makes the script spit out debug info and NOT write out the plate file. 
		self.debug_log = arg_db

		# Other variables
		self.cutout_width = Decimal("0");
		self.cutout_height = Decimal("0");
		
	#=================================#
	#            Classes              #
	#=================================#

	class Switch:
		
		def __init__(self, x_var, y_var):
			# These fields correspond to the respective kle data
			self.pos_x = x_var	# Implied coord X (Does not have a field in KLE)
			self.pos_y = y_var	# Implied coord Y (Does not have a field in KLE)
			self.w = 1		# Width
			self.h = 1		# Height
			self.w2 = 1		# Width2: For oddly sized keys such as ISO, stepped
			self.h2 = 1		# Height2: For oddly sized keys such as ISO, stepped
			self.rx = 0		# RotationX: Rotation anchor
			self.ry = 0		# RotationY: Rotation anchor
			self.r = 0		# Rotation: Angle
			self.x = 0		# x: X offset from either previous key or anchor
			self.y = 0		# y: Y offset from either previous key or anchor
		
			self.cutout_angle = 0	# Custom field for switch-independent cutout rotation
			self.stab_angle = 0		# Custom field for switch-independent stabilizer rotation
			
		def calculate_center_coords(self):
			
	
	#=================================#
	#           DXF Blocks            #
	#=================================#
	
	# These basically act as stamps.
	# Saves from having to write each and every entity individually, as was done before.
	
	def build_blocks(self):
		
		# Switch cutout
		block_switch_cutout = self.plate.blocks.new(name='SWITCH_CUTOUT')
		switch_half_width = self.cutout_width / 2
		switch_half_height = self.cutout_height / 2
		block_switch_cutout.add_line((-switch_half_width + self.cutout_radius, -switch_half_height), (switch_half_width - self.cutout_radius, -switch_half_height)) # Top
		block_switch_cutout.add_line((-switch_half_width + self.cutout_radius, switch_half_height), (switch_half_width - self.cutout_radius, switch_half_height)) # Bottom
		block_switch_cutout.add_line((-switch_half_width, -switch_half_height + self.cutout_radius), (-switch_half_width, switch_half_height - self.cutout_radius)) # Left
		block_switch_cutout.add_line((switch_half_width, -switch_half_height + self.cutout_radius), (switch_half_width, switch_half_height - self.cutout_radius)) # Right
		block_switch_cutout.add_arc((switch_half_width - self.cutout_radius, -switch_half_height + self.cutout_radius), self.cutout_radius, 0, 90) # Top right
		block_switch_cutout.add_arc((-switch_half_width + self.cutout_radius, -switch_half_height + self.cutout_radius), self.cutout_radius, 90, 180) # Top left
		block_switch_cutout.add_arc((-switch_half_width + self.cutout_radius, switch_half_height - self.cutout_radius), self.cutout_radius, 180, 270) # Bottom left
		block_switch_cutout.add_arc((switch_half_width - self.cutout_radius, switch_half_height - self.cutout_radius), self.cutout_radius, 270, 360) # Bottom right
		
		# Stab cutout for mx-simple 
		# Fairly tight rectangles with width based on official spec
		stab_mx_simple_cutout = self.plate.blocks.new(name='STAB_MX_SIMPLE_CUTOUT')
		stab_mx_simple_cutout.add_line((Decimal('-3.375') + self.stab_radius, Decimal('6')), (Decimal('3.375') - self.stab_radius, Decimal('6')))
		stab_mx_simple_cutout.add_line((Decimal('-3.375') + self.stab_radius, Decimal('-8')), (Decimal('3.375') - self.stab_radius, Decimal('-8')))
		stab_mx_simple_cutout.add_line((Decimal('-3.375'), Decimal('6') - self.stab_radius), (Decimal('-3.375'), Decimal('-8') + self.stab_radius))
		stab_mx_simple_cutout.add_line((Decimal('3.375'), Decimal('6') - self.stab_radius), (Decimal('3.375'), Decimal('-8') + self.stab_radius))
		stab_mx_simple_cutout.add_arc((Decimal('-3.375') + self.stab_radius, Decimal('6') - self.stab_radius), self.stab_radius, 90, 180)
		stab_mx_simple_cutout.add_arc((Decimal('3.375') - self.stab_radius, Decimal('6') - self.stab_radius), self.stab_radius, 0, 90)
		stab_mx_simple_cutout.add_arc((Decimal('-3.375') + self.stab_radius, Decimal('-8') + self.stab_radius), self.stab_radius, 180, 270)
		stab_mx_simple_cutout.add_arc((Decimal('3.375') - self.stab_radius, Decimal('-8') + self.stab_radius), self.stab_radius, 270, 360)
		
		# Stab cutout for large-cuts
		# Large, spacious 15x7 cutouts, the recommended standard
		stab_large_cuts_cutout = self.plate.blocks.new(name='STAB_LARGE_CUTS_CUTOUT')
		stab_large_cuts_cutout.add_line((Decimal('-3.5') + self.stab_radius, Decimal('6')), (Decimal('3.5') - self.stab_radius, Decimal('6')))
		stab_large_cuts_cutout.add_line((Decimal('-3.5') + self.stab_radius, Decimal('-9')), (Decimal('3.5') - self.stab_radius, Decimal('-9')))
		stab_large_cuts_cutout.add_line((Decimal('-3.5'), Decimal('6') - self.stab_radius), (Decimal('-3.5'), Decimal('-9') + self.stab_radius))
		stab_large_cuts_cutout.add_line((Decimal('3.5'), Decimal('6') - self.stab_radius), (Decimal('3.5'), Decimal('-9') + self.stab_radius))
		stab_large_cuts_cutout.add_arc((Decimal('-3.5') + self.stab_radius, Decimal('6') - self.stab_radius), self.stab_radius, 90, 180)
		stab_large_cuts_cutout.add_arc((Decimal('3.5') - self.stab_radius, Decimal('6') - self.stab_radius), self.stab_radius, 0, 90)
		stab_large_cuts_cutout.add_arc((Decimal('-3.5') + self.stab_radius, Decimal('-9') + self.stab_radius), self.stab_radius, 180, 270)
		stab_large_cuts_cutout.add_arc((Decimal('3.5') - self.stab_radius, Decimal('-9') + self.stab_radius), self.stab_radius, 270, 360)
		 
	
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
	
		if (self.cutout_type == "mx" or self.cutout_type == "alps" or self.cutout_type == "omron"):
			
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
				self.draw_rotated_arc(x + Decimal(str(arc[0])), y + Decimal(str(arc[1])), anchor_x, anchor_y, self.stab_radius, arc[2], arc[3], angle)
		
		# TODO: Add switchtop removal cutouts, hardcoded radius to 0.5
		#elif (self.cutout_type == "mx-topremoval-simple"):
		#	line_segments.append((-Decimal('7.80') + self.cutout_radius, -Decimal('7')), (Decimal('7.80') - self.cutout_radius, -Decimal('7')))
		
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
		elif (self.cutout_type == "alps"):
			self.cutout_width = Decimal('15.50');
			self.cutout_height = Decimal('12.80');
		elif (self.cutout_type == "omron"):
			self.cutout_width = Decimal('13.50');
			self.cutout_height = Decimal('13.50');
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
		
		# Switch to rotation parse mode once KLE enters the rotation syntax zone
		rotate_zone = False
		
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
					
					# TODO: Write the key creation code
					
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
			print("Complete! Saving plate to specified output")

		if (file == "stdout"):
			self.plate.write(sys.stdout)
		else:
			self.plate.write(file)
		return 0
			
		
			
if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Create a plate DXF based on KLE raw data.')
	
	# Note: The args will be fed into Decimal(), which takes strings
	
	parser.add_argument("-ct", "--cutout-type", help="Switch cutout type. Supported: mx, alps, omron; Default: mx", type=str, default='mx')
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