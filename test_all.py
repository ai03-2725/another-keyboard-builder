#!/usr/bin/env python3
import os
import codecs
import plategen
from pathlib import Path


basepath = Path(__file__).parent.absolute()
path_input = basepath / 'test-data'
path_output = basepath / 'test-writedir'

dia_exe = r"C:\data\opt\PortableApps\PortableApps\DiaPortable\DiaPortable.exe"
dia_exe = None
'''
Path to gnome dia or None if no PNG file should be created
''' 

all_file_names = path_input.glob('*')
# all_file_names = [path_input / 'ergodox']
# all_file_names = [path_input / 'atreus-min']
# all_file_names = [path_input / 'alice-urwi_red2']
# all_file_names = [path_input / 'test-full104']
# all_file_names.append(path_input / 'alice-urwi')
# all_file_names = [path_input / 'alice-urwi_red3']
# all_file_names = [path_input / 'alice-urwi']

for filename in all_file_names:
    dxf_out = path_output / (filename.stem + '.dxf')
    png_out = dxf_out.with_suffix('.png')

    gen = plategen.PlateGenerator('mx', '0.5', 'mx-simple', '0.5', 'none', '0.5', '19.05', '19.05', False)
    # gen = plategen.PlateGenerator('mx', '0.5', 'mx-simple', '0.5', 'none', '0.5', '1', '1', False)

    print(' EXECUTE {}'.format(filename.name))

    with codecs.open(filename, 'r', "utf-8") as input_file, open(dxf_out, 'w') as fout:
        input_data = input_file.read()
        gen.generate_plate(fout, input_data)

        if dia_exe is not None:
            popen_strg = r'"{}"  "{}" -e "{}"'.format(dia_exe, dxf_out, png_out)
            print(" EXECUTE " + popen_strg)
            os.popen(popen_strg)
