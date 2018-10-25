# Another Keyboard Builder
An exact mechanical keyboard plate creator that doesn't result in 13.99999mm cutouts

### Why?
Alternate generators don't have either the features or exactness that designers need.
This plate generator is designed to save keyboard designers significant amounts of time, while also providing top-notch accuracy required for designs costing hundreds of dollars.

### Features
- Filleting. Fillet all corners during generation so Fusion 360 doesn't have to crash 50 times later attempting it.
- Exactness. No more 13.99999mm or 14.00001mm cutouts; this generator will always use exact, accurate dimensions.
- A variety of cutout options based on actual production-use dimensions.

## Usage

The command itself:
```
plategen.py [-h] [-ct CUTOUT_TYPE] [-cr CUTOUT_RADIUS] [-st STAB_TYPE]
                   [-sr STAB_RADIUS] [-at ACOUSTICS_TYPE]
                   [-ar ACOUSTICS_RADIUS] [-uw UNIT_WIDTH] [-uh UNIT_HEIGHT]
                   [-om OUTPUT_METHOD] [-of OUTPUT_FILENAME] [--debug-log]
```
Run `python plategen.py -h` to see detailed information on each argument.

An example of generating based on raw data in a file:
```
cat kle-raw | python plategen.py > plate.dxf
```


### Requirements:
- Python 3.7
- Everything in requirements.txt

### Todo
- More stabilizer cutout options.
- More switch cutout options.
