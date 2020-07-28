"""Switch class extracted without any modifications from plategen,
because is needed in PlateGenerator and RowCoordianteSystem
"""
import re
import logging
from akblib.coor_sys import CoorSys
from decimal import Decimal

logger = logging.getLogger(__name__)


class Switch:

    def __init__(self, coor_sys=CoorSys(), x_var=Decimal('0'), y_var=Decimal('0'), width=Decimal('1'), height=Decimal('1'), label=''):

        self.coor_sys = coor_sys

        # These fields correspond to the respective kle data
        self.x = x_var    # data in global / DXF coordinate system
        self.y = y_var    # data in global / DXF coordinate system

        self.width = width
        self.height = height
        self.width_secondary = 1
        self.height_secondary = 1

        self.label = re.sub(r'[^abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_]+', '', label)


        # self.rotx = 0
        # self.roty = 0
        self.angle = coor_sys.r

        self.cutout_angle = 0
        self.stab_angle = 0
        # self.offset_x = 0
        # self.offset_y = 0

        # # data in global / DXF coordinate system
        # Upper left coner
        self.mm = self.coor_sys.get_global(x_var, y_var)

        # rotation center
        self.mm_center = self.coor_sys.get_global(x_var + self.width * Decimal('.5'), y_var + self.height * Decimal('.5'))

        # diagonal element
        _nn = self.coor_sys.get_global(x_var + self.width, y_var + self.height)

        self.corners = [self.mm,
                        (_nn[0], self.mm[1]),
                        _nn,
                        (self.mm[0], _nn[1])]

        logger.info(" New key '{}' at ({:6.3},{:6.3})".format(self.label, self.mm[0], self.mm[1]))
        return

    def to_csv(self, str_fmt="%8s"):
        """Creates an CSV string from all properties."""
        ret_str = str_fmt % str(self.x)
        for i in (self.y, self.width, self.height, self.width_secondary, self.height_secondary, self.coor_sys.rx,
                  self.coor_sys.ry, self.coor_sys.r, self.cutout_angle, self.stab_angle):
            ret_str += ", " + str_fmt % str(i)
        return ret_str
