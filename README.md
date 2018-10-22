# Another Keyboard Builder
An exact mechanical keyboard plate creator that doesn't result in 13.99999mm cutouts

### Why?
Alternate generators don't have either the features or exactness that designers need.

### Features
- Filleting. Fillet all corners during generation so Fusion 360 doesn't have to crash 50 times later attempting it.
- A variety of cutout options to meet the requirements of each plate.
- Exactness. No more 13.99999mm or 14.00001mm cutouts; this generator will always use exact, accurate dimensions.

### Usage
Script is nowhere near complete, so options are only changed in the file for now.
With `debug_use_generic_matrix` and `debug_log` turned off, and output_method set to stdout, simply pipe in keyboard-layout-editor.com data:

cat kle-data | python3 plategen.py > plate.dxf

### Issues
- Having a quotation mark in a legend breaks the script. Need to filter it out

### Todo
- Rotated switch/stabilizer support.
- Stabilizer cutout filleting.
- More stabilizer cutout options.
- More switch cutout options.
- Alps stabilizers.
- ISO, bigass enter support.

Some features to be based on https://github.com/swill/kad in the future.
