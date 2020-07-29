from decimal import Decimal
import logging
from akblib.switch import Switch
from akblib.coor_sys import CoorSys

logger = logging.getLogger(__name__)


class PropAllSwitch():

	KEYS_rot_orig = ('rx', 'ry')
	"""Rotation point, handled special in update().

	rx current_rotx
	ry current_roty
	r current_angle

	TODO:
	_rs = current_stab_angle  Rotation angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
	_rc = current_cutout_angle Switch cutout angle offset for stabilizer OPPOSITE OF typical counterclockwise-from-xpositive
	"""

	KEYS_all_keycap_num = ('r', '_rs', '_rc', 'a', 'f', 'f2')
	"""properties apply only to the next keycap only. as number."""

	KEYS_all_keycap_str = ('c', 't', 'p')
	"""properties apply only to the next keycap only. as number."""

	KEYS_all_keycap_bool = ('g')
	"""properties apply only to the next keycap only. as boolean."""

	def __init__(self):
		self.reset()

	def reset(self):
		"""Reset to default values. see  reset_key_parameters()."""
		self.r = Decimal('0')  # rotation angle in deegrees
		self.rx = Decimal('0')  # rotation point x
		self.ry = Decimal('0')  # rotation point y
		self._rc = Decimal('0')  # current_cutout_angle
		self._rs = Decimal('0')  # current_stab_angle

	def parse(self, prop_dict):
		"""

		Args:
			prop_dict(dict): Properties for next key only:

		"""
		# init by origin
		for r_xy in PropAllSwitch.KEYS_rot_orig:
			if r_xy in prop_dict:
				setattr(self, r_xy, Decimal(prop_dict[r_xy]))

		# process next keys
		for prop, val in prop_dict.items():
			# ignore rotation point, because handled before
			if prop in PropAllSwitch.KEYS_rot_orig:
				continue
			elif prop in PropAllSwitch.KEYS_all_keycap_num:
				setattr(self, prop, Decimal(str(val)))
			elif prop == "r":
				self.set_angle(val)
		# TODO bool values
		return


class PropNextSwitch():

	KEYS_next_keycap_num = ('x', 'y', 'w', 'h', 'x2', 'y2', 'w2', 'h2')
	"""properties apply only to the next keycap only. as number."""

	KEYS_next_keycap_bool = ('l', 'n', 'd')
	"""properties apply only to the next keycap only. as boolean."""

	def __init__(self):
		self.reset()

	def reset(self):
		"""Reset to default values. see  reset_key_parameters()."""
		self.x = Decimal('0')  # current_offset_x x = X offset for next keys OR offset from rotation anchor (seriously kle?)
		self.y = Decimal('0')  # current_offset_y y = Y offset for next keys OR offset from rotation anchor (seriously kle?)
		self.w = Decimal('1')  # current_width
		self.h = Decimal('1')  # current_height
		self.w2 = Decimal('1')  # current_width_secondary
		self.h2 = Decimal('1')  # current_height_secondary
		self.x2 = Decimal('0')  #
		self.y2 = Decimal('0')  #

		self.d = False  # Key is decoration.
		self.ll = False
		self.n = False

	def parse(self, prop_dict):
		"""

		Args:
			prop_dict(dict): Properties for next key only:

		"""
		# process next keys
		for prop, val in prop_dict.items():
			# ignore rotation point, because handled before
			if prop in PropNextSwitch.KEYS_next_keycap_num:
				setattr(self, prop, Decimal(str(val)))

		return


class KLE_Reader(object):
	"""Handling corrdinate system and parsing raw KLE data.

	raw KLE example
	===============

		["Num Lock","/","*","-"],
		["7\\nHome","8\\n↑","9\\nPgUp",{h:2},"+"],
		["4\\n←","5","6\\n→"],
		["1\\nEnd","2\\n↓","3\\nPgDn",{h:2},"Enter"],
		[{w:2},"0\\nIns",".\\nDel"]

	Coordinate sytem
	================

	KLE Coordinate sytem
	--------------------

		* unit keylength
		* x to right
		* y down
		* after rx, ry, r is set this is an rotated koordinate system

		+---------> X
		|      )
		|     )
		|    \/  alpha
		| Y
		\/


	DXF Coordinate sytem
	--------------------

		* unit mm
		* x to right
		* y up

		/\ Y
		|
		|
		|
		|
		+---------> X


	Position of key ("X") in coordinate system is upper left corner

		X------+
		|      |
		|   A  |
		|      |
		+------+

	https://github.com/ijprest/keyboard-layout-editor/wiki/Serialized-Data-Format


		x, y (number)
				These specify x and y values to be added to the current coordinates.
				For example, specifying x = 1 will leave a 1.0x gap between the previous key and the next one.
		UNDOCUMENTED
		------------
		r       used as rotation angle glocckwise starting horizontal
		rx, ry  rotation point by default 0, 0

	"""

	def __init__(self, unit_width=Decimal('19.05'), unit_height=Decimal('19.05')):
		"""Set up all references."""
		self.prop_next = PropNextSwitch()
		self.prop_all = PropAllSwitch()
		# coordintes in (optional rotated) KLE coordinate system
		self.act_x = Decimal('0')
		self.act_y = Decimal('0')
		self.debug_log = False
		self.unit_width = unit_width
		self.unit_height = unit_height

		# self.kle_coorsys = CoorSys()

		self.all_switches = []
		"""all switches are after call of self.parse() in this list."""

		return

	def next(self, o):
		"""process the next element.

		Args:
			o(dict or str): next element in a row

		"""
		if isinstance(o, str):  # New Key

			# update local position for  next keycap
			self.act_x += self.prop_next.x
			self.act_y += self.prop_next.y

			# new coordinate system for the key...
			_coor_sys = CoorSys(r=self.prop_all.r,
								rx=self.prop_all.rx,
								ry=self.prop_all.ry,
								unit_width=self.unit_width,
								unit_height=self.unit_height)

			sw = Switch(coor_sys=_coor_sys,
						x_var=self.act_x,
						y_var=self.act_y,
						width=self.prop_next.w,
						height=self.prop_next.h, label=o)

			# additional properties not handled with constructor...
			sw.width_secondary = self.prop_next.w2
			sw.height_secondary = self.prop_next.h2
			sw.cutout_angle = self.prop_all._rc
			sw.stab_angle = self.prop_all._rs

			self.act_x += self.prop_next.w
			# reset properties for next switch only
			self.prop_next.reset()

			return sw
		elif isinstance(o, dict):
			self.update_properties(o)
		else:
			raise ValueError("RowCoordianteSystem.next() can be only str or dictObject is not a list")

	def update_properties(self, prop_dict):
		"""Update coordinate system by propertiews

		Args:
			prop_dict(dict()): Properties to parse

		"""
		self.prop_next.parse(prop_dict)
		self.prop_all.parse(prop_dict)

		if 'rx' in prop_dict or 'rx' in prop_dict:
			self.act_x = Decimal('0')
			self.act_y = Decimal('0')

		return

	def get_local(self):
		"""Returns actual position in local / rotated coorinate system.

		Returns:
			(Decimal, Decimal): x and y position in local coordinate system

		"""
		return (self.act_x, self.act_y)

	def new_row(self):
		"""Start a new row of the coor."""
		self.act_x = 0
		self.act_y += 1

	def parse(self, json_data):
		"""Parse JSON and return list of switches.

		Calculates min/max of width and height

		Args:
			json_data(json): KLE json data.

		Returns:
			List[Switch]: all switches in a list
		"""

		self.min_width = Decimal('1.e10')
		self.max_width = -self.min_width
		self.min_height = Decimal('1.e10')
		self.max_height = -self.min_height

		for row in json_data:
			if self.debug_log:
				print(">>> ROW BEGIN")
				print(str(row))

			# KLE standard supports first row being metadata.
			# If it is, ignore.
			if isinstance(row, dict):
				if (self.debug_log):
					print("!!! Row is metadata. Skip.")
				continue

			for key in row:

				current_switch = self.next(key)

				if current_switch:  # only append switches, not keys...
					self.all_switches.append(current_switch)

					# For example, vertical keys created by stretching height to be larger than width
					# The key's cutout angle and stab angle should be offset by 90 degrees to compensate.
					# This effectively transforms the key to a vertical
					# This also handles ISO
					if (current_switch.width < current_switch.height and current_switch.height >= 1.75):
						current_switch.cutout_angle -= Decimal('90')
						current_switch.stab_angle -= Decimal('90')

					for p in current_switch.corners:
						if self.max_width < p[0]:
							self.max_width = p[0]
						if self.min_width > p[0]:
							self.min_width = p[0]

						if self.max_height < p[1]:
							self.max_height = p[1]
						if self.min_height > p[1]:
							self.min_height = p[1]
			self.new_row()
		return self.all_switches

	def dbg_plot(self, gui=False):
		"""Debug plot of the corners."""
		import matplotlib.pyplot as plt
		import pathlib
		# first plot extremas
		x = [self.min_width, self.max_width, self.max_width, self.min_width, self.min_width]
		y = [self.max_height, self.max_height, self.min_height, self.min_height, self.max_height]

		plt.clf()
		plt.plot(x, y)
		for sw in self.all_switches:
			x = []
			y = []
			for c in (0, 1, 2, 3, 0, 2, 3, 1):
				x.append(sw.corners[c][0])
				y.append(sw.corners[c][1])

			plt.plot(x, y)
			plt.text(sw.mm_center[0], sw.mm_center[1], sw.label,
					horizontalalignment='center', verticalalignment='center')

		write_dir = pathlib.Path(__file__).parent.parent / 'test-writedir'
		# loop to find filename for a new file
		for i in range(999):
			file_name = write_dir / 'plt_{:03d}.png'.format(i)
			if not file_name.exists():
				break

		plt.savefig(file_name)
		print("Generated " + file_name.as_uri())
		if gui:
			plt.show()
		return
