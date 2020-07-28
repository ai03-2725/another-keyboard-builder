import unittest
from decimal import Decimal, getcontext
import math  # for PI

from akblib.kle_reader import KLE_Reader
from plategen import PlateGenerator 

class TestRowCoordianteSystem(unittest.TestCase):

    @unittest.skip("check this later")
    def test_simple_init(self):
        lcs = KLE_Reader('1.0', '2.0', '0')

        pos = lcs.get_local()
        self.assertEqual(pos[0], Decimal('0'))
        self.assertEqual(pos[1], Decimal('0'))

        # Moving moving 3 lines
        for _ in range(3):
            lcs.set_newline()

        pos = lcs.get_local()
        self.assertEqual(pos[0], Decimal('0'))
        self.assertEqual(pos[1], Decimal('3'))

#        pos = lcs.get_global_coordinates()
#        self.assertEqual( pos[0] , Decimal('1') )
#        self.assertEqual( pos[1] , Decimal('2') )

    @unittest.skip("check this later")
    def test_simple_rotated(self):
        # do reduced precision

        # store precisness for sin / cos check        
        prec_orig = getcontext().prec
        getcontext().prec = 10

        lcs = KLE_Reader('1.0', '2.0', '30')
        # sin(30deg) = 1/2
        self.assertEqual( lcs.s, Decimal('.5'))
        
        unmoved = lcs.get_global()
        self.assertEqual( lcs.s, Decimal('.5'))
        self.assertEqual( unmoved[0] , Decimal('1') )
        self.assertEqual( unmoved[1] , Decimal('2') )
        
        # lcs.
        
        # reset precisness...
        getcontext().prec = prec_orig
    
    @unittest.skip("check this later")
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


        left_thumb = KLE_Reader(rx='6.5', ry='4.25', angle='30', x='1', y='-1')
        pos_LX1 = left_thumb.get_global()

        self.assertEqual(Decimal('7.5'), pos_LX1[0])
        self.assertEqual(Decimal('3.25'),pos_LX1[1])

        # cant check more in this thumbcluste, coridinates are given out incorrect
        #pos_LX2 = left_thumb.step()
        #self.assertEqual(Decimal('8.5'), pos_LX2[0])
        #self.assertEqual(Decimal('3.25'),pos_LX2[1])


        # [{r:-30,rx:13,y:-1,x:-3},"RX1","RX2"],
        right_thumb = KLE_Reader(rx='6.5', ry='4.25', angle='-30', x='-3', y='-1')




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
        lcs = KLE_Reader('1.0', '2.0', '30')


    def test_trigonometric_funcions(self):
        """Check sin and cos."""
        rcs = KLE_Reader()
        self.assertEqual(rcs.val_cos, Decimal('1'))

        rcs.set_angle("30")

        self.assertEqual(rcs.val_sin, Decimal('.5'))

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
