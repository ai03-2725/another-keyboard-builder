# Another Keyboard Builder
An exact mechanical keyboard plate creator that doesn't result in 13.99999mm cutouts

## Use it here:
[kbplate.ai03.me](http://kbplate.ai03.me/)

## Why?
- Alternate generators don't have either the features or exactness that designers need.
- This plate generator is designed to save keyboard designers significant amounts of time, while also providing top-notch accuracy required for designs costing hundreds of dollars.

## Features
- Filleting. Fillet all corners during generation so Fusion 360 doesn't have to crash 50 times later attempting it.
- Exactness. No more 13.99999mm or 14.00001mm cutouts; this generator will always produce exact, accurate dimensions.
- A variety of cutout options based on actual production-use dimensions.

## Usage

Plategen as a standalone tool:
```
plategen.py [-h] [-ct CUTOUT_TYPE] [-cr CUTOUT_RADIUS] [-st STAB_TYPE]
                   [-sr STAB_RADIUS] [-at ACOUSTICS_TYPE]
                   [-ar ACOUSTICS_RADIUS] [-uw UNIT_WIDTH] [-uh UNIT_HEIGHT]
                   [--debug-log]
```
Run `python plategen.py -h` to see detailed information on each argument.

An example of generating based on raw data in a file:
```
cat kle-raw | python plategen.py > plate.dxf
```

Hosting:
Simply run web.py with requirements installed.

## Additional Options

In addition to feeding in typical Keyboard-Layout-Editor data, custom fields may be added to fine-tune the outcomes:
- `_rs:` Rotate the stabilizer cutout independently from the key. (Idea from [SwillKB Builder](https://github.com/swill/kad))
  
  For example, for bottom row flipped spacebars, a 6.25U spacebar may have the data field `{w:6.25,_rs:180}`.
  
- `_rc:` Similar, but for rotating the switch cutout independently of the key.

## Requirements:
- Python 3.7
- Everything in requirements.txt (or requirements-web.txt if hosting web service)

## Todo
- More stabilizer cutout options.
- More switch cutout options.
- Fix certain rotated switches dying. However, this is mostly due to awful KLE syntax, so I don't plan to repair it soon.
