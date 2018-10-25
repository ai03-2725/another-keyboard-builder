#!/usr/bin/env python3

import plategen

filename = 'test-data/test-full104'
gen = plategen.PlateGenerator('mx', '0.5', 'mx-simple', '0.5', 'none', '0.5', '19.05', '19.05', 'stdout', 'plate.dxf', False)
with open(filename, 'r') as input_file:
    input_data = input_file.read()
    gen.generate_plate(input_data)
