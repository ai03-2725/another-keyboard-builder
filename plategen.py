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
import logging
from akblib.kle_reader import KLE_Reader
from akblib.switch import Switch
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
		if self.debug_log:
			logging.basicConfig(level=logging.DEBUG)
		else:
			logging.basicConfig(level=logging.ERROR)
		# Runtime vars that are often systematically changed or reset

		# Cutout sizes
		self.cutout_width = Decimal('0')
		self.cutout_height = Decimal('0')

		self.dbg_png = False  # no generation of png by default

		
	#=================================#
	#            Classes              #
	#=================================#

		
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

		if (self.cutout_type == "mx" or self.cutout_type == "mx-slightly-wider" or self.cutout_type == "alps" or self.cutout_type == "omron"):
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
		
		# if(self.debug_log):
		#	TODO add Switch.info() method
		#   print("RX: " + str(switch.rotx))
		#	print("RY: " + str(switch.roty))
		#	print("Angle: " + str(switch.angle))
		#	print("Offset X: " + str(switch.offset_x))
		#	print("Offset Y: " + str(switch.offset_y))
		#	print("===")
				



		# Draw main switch cutout
		self.draw_switch_cutout(switch.mm_center[0], switch.mm_center[1], switch.angle + switch.cutout_angle)
		
		# Adjust width for vertically tall keys, and generate stabs
		apparent_width = switch.width;
		if (switch.width < switch.height):
			apparent_width = switch.height;
		
		self.generate_stabs(switch.mm_center[0], switch.mm_center[1], switch.angle + switch.stab_angle, apparent_width)
		

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
		
		try:
			json_data = json5.loads('[' + input_data + ']')
		except(ValueError):
			#print("Invalid KLE data", file=sys.stderr)
			return(1)
		# Object to handle parsing kle raw data data
		kle = KLE_Reader()
	
		all_switches = kle.parse(json_data)
		# end loop over rows, all_switches set 
		
		if self.dbg_png:
			kle.dbg_plot()

		# Render each one by one. 
		for switch in all_switches:
			self.render_switch(switch)

		# Draw outer bounds - top, bottom, left, right
		# 
		#   (0,0)
		#   pix------pxx    x..max   width...y-coordinate
		#    |        |     i..min   height..x-coordinate
		#    |        | 
		#   pii------pxi
		
		pix = (kle.min_width, kle.max_height)
		pxx = (kle.max_width, kle.max_height)
		pii = (kle.min_width, kle.min_height)
		pxi = (kle.max_width, kle.min_height)

		self.modelspace.add_line(pix, pxx)
		self.modelspace.add_line(pii, pxi)
		self.modelspace.add_line(pix, pii)
		self.modelspace.add_line(pxx, pxi)
			
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
