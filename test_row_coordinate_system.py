import unittest
from decimal import Decimal, getcontext
import math  # for PI

from akblib.kle_reader import KLE_Reader
from akblib.coor_sys import CoorSys
from plategen import PlateGenerator


class TestRowCoordianteSystem(unittest.TestCase):

    def test_simple_init(self):
        kler = KLE_Reader()

        self.assertEqual(kler.act_x, Decimal('0'))
        self.assertEqual(kler.act_y, Decimal('0'))

        # Moving moving 3 lines
        for _ in range(3):
            kler.new_row()

        self.assertEqual(kler.act_x, Decimal('0'))
        self.assertEqual(kler.act_y, Decimal('3'))

    @unittest.skip("check this later, wrong API")
    def test_simple_rotated(self):
        # do reduced precision

        # store precisness for sin / cos check
        prec_orig = getcontext().prec
        getcontext().prec = 10

        kler = KLE_Reader()
        # sin(30deg) = 1/2
        # self.assertEqual(kler.s, Decimal('.5'))

        unmoved = kler.get_global()
        self.assertEqual(kler.s, Decimal('.5'))
        self.assertEqual(unmoved[0], Decimal('1'))
        self.assertEqual(unmoved[1], Decimal('2'))
        # reset precisness...
        getcontext().prec = prec_orig

    @unittest.skip("check this later, wrong API")
    def test_simple_ergodox(self):
        """Check last key "LK" to left thumb cluster

        [{y:-0.75,x:0.5},"","",{x:14.5},"","LastKey"],
        [{r:30,rx:6.5,ry:4.25,y:-1,x:1},"LX1","LX2"],
        [{h:2},"LY1",{h:2},"LY2","LY3"],
        LastKey = (18  , 4.375)
        LFA     = ( 7.5, 3.25 )

        Rotation point Absulte as RX, RY
        c(30) = .86
        s(30) = .5
        """
        prec_orig = getcontext().prec
        getcontext().prec = 1

        left_thumb = KLE_Reader()
        pos_LX1 = left_thumb.get_global()

        self.assertEqual(Decimal('7.5'), pos_LX1[0])
        self.assertEqual(Decimal('3.25'), pos_LX1[1])
        # [{r:-30,rx:13,y:-1,x:-3},"RX1","RX2"],
        # right_thumb = KLE_Reader()

        getcontext().prec = prec_orig

    @unittest.skip("check this later")
    def test_simple_kyra(self):
        """Check OEM R1 with keys 2,3,4

        x, y (number)
                These specify x and y values to be added to the current coordinates.
                For example, specifying x = 1 will leave a 1.0x gap between the previous key and the next one.


        start is (2.97, 0.93) r = degs  (x,y) are from last row
        "rgt" is at (15.3449, 5.45) + (2.97, -5.52)

        => Newline begins at (0, y_last + 1)
          -> check     rgt     + newl  + (x,y)
                   = (x, 5.45) + (0,1) + (2.97,-5.52) = (2.97, 0.93)
             OK

        [{x:0.66,w:1.25},"Ctrl",{w:1.25},"Super",{x:9.065},"fn",{x:0.12},"lft","dwn","rgt"],
        [{r:8,y:-5.52,x:2.97,p:"OEM R1",a:5},"@\n2","#\n3","$\n4","%\n5","^\n6"]
        """

        # start with
        # lcs = KLE_Reader('1.0', '2.0', '30')
        return

    def test_trigonometric_funcions(self):
        """Check sin and cos."""
        cs = CoorSys()
        self.assertEqual(cs.val_cos, Decimal('1'))

        cs.set_angle("30")

        self.assertEqual(cs.val_sin, Decimal('.5'))

        pass

    def test_ergodox_thumb_cluster(self):
        """Test thumb cluster for ergodox.

        [{r:30,rx:6.5,ry:4.25,y:-1,x:1},"LX1","LX2"],
        [{h:2},"LY1",{h:2},"LY2","LY3"],
        [{x:2},"LZ3"]}""
        """
        json_data = None
        try:
            import json5
            # TODO change back to 30 degrees.
            json_data = json5.loads('''[
        [{r:30,rx:6.5,ry:4.25,y:-1,x:1},"LX1","LX2"],
        [{h:2},"LY1",{h:2},"LY2","LY3"],
        [{x:2},"LZ3"]  ]''')
        except(ValueError):
            pass

        all_keys = {}
        rcs = KLE_Reader()
        for row in json_data:
            for key in row:
                sw = rcs.next(key)
                if sw:  # only append switches, not keys...
                    all_keys[sw.label] = sw
            rcs.new_row()

        return


if __name__ == '__main__':
    unittest.main()
