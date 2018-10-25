#!/usr/bin/env python3

import plategen

filename = 'test-full104'
gen = plategen.PlateGenerator()
with open(filename, 'r') as input_file:
    input_data = input_file.read()
    gen.generate_plate(input_data)
