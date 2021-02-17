"""Coordinate transformation
"""

from decimal import Decimal, getcontext
import math


class CoorSys:

	def __init__(self, r=Decimal('0'), rx=Decimal('0'), ry=Decimal('0'), unit_width=Decimal('1'), unit_height=Decimal('1')):
		"""Angle in degrees."""
		self.rx = rx
		"""Rotation point in x-coordinate."""
		self.ry = ry
		"""Rotation point in y-coordinate."""
		self.unit_width = unit_width
		self.unit_height = unit_height

		self.r = self.set_angle(Decimal('-1') * r)

	def get_global(self, x_val, y_val):
		"""Returns actual position in global coorinate system.

		since unit_width may differ from unit_height, these values must be scaled individually.

		Args:
			x_val(Decimal): x-position in (rotated) KLE coordinate system
			y_val(Decimal): y-position in (rotated) KLE coordinate system

		Returns:
			(Decimal, Decimal): x and y position in global coordinate system

		"""

		rx = self.rx * self.unit_width
		x_val *= self.unit_width
		ry = self.ry * self.unit_height
		y_val *= self.unit_height

		# do matrix rotation

		return (
			rx + self.val_cos * x_val + self.val_sin * y_val,
			-(ry - self.val_sin * x_val + self.val_cos * y_val))

	def set_angle(self, angle='0'):
		"""set sin and cosinus for angle with maximal correct values."""

		if isinstance(angle, str):
			angle = Decimal(angle)
		elif isinstance(angle, Decimal):
			angle = angle
		elif isinstance(angle, int) or isinstance(angle, float):
			angle = Decimal(str(angle))
		else:
			raise ValueError("Angle wrong defined!")

		if angle == Decimal('0'):
			self.val_cos = Decimal('1')
			self.val_sin = Decimal('0')

		elif angle == Decimal('30'):
			self.val_cos = Decimal('3').sqrt() * Decimal('.5')
			self.val_sin = Decimal('.5')

		elif angle == Decimal('45'):
			self.val_cos = Decimal('2').sqrt() * Decimal('.5')
			self.val_sin = Decimal('2').sqrt() * Decimal('.5')

		elif angle == Decimal('60'):
			self.val_cos = Decimal('.5')
			self.val_sin = Decimal('3').sqrt() * Decimal('.5')

		elif angle == Decimal('90'):
			self.val_cos = Decimal('0')
			self.val_sin = Decimal('1')

		else:
			self.val_cos = self.decimal_cos(Decimal(angle) * Decimal(math.pi) / Decimal('180'))
			self.val_sin = self.decimal_sin(Decimal(angle) * Decimal(math.pi) / Decimal('180'))
		return angle

	def decimal_cos(self, x):
		"""Return the cosine of x as measured in radians.

		>>> print cos(Decimal('0.5'))
		0.8775825618903727161162815826
		>>> print cos(0.5)
		0.87758256189
		>>> print cos(0.5+0j)
		(0.87758256189+0j)

		"""
		getcontext().prec += 4
		i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
		while s != lasts:
			lasts = s
			i += 2
			fact *= i * (i - 1)
			num *= x * x
			sign *= -1
			s += num / fact * sign
		getcontext().prec -= 4
		return +s

	def decimal_sin(self, x):
		"""Return the sine of x as measured in radians.

		>>> print sin(Decimal('0.5'))
		0.4794255386042030002732879352
		>>> print sin(0.5)
		0.479425538604
		>>> print sin(0.5+0j)
		(0.479425538604+0j)

		"""
		getcontext().prec += 4
		i, lasts, s, fact, num, sign = 1, 0, x, 1, x, 1
		while s != lasts:
			lasts = s
			i += 2
			fact *= i * (i - 1)
			num *= x * x
			sign *= -1
			s += num / fact * sign
		getcontext().prec -= 4
		return +s
