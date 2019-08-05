Mesh from curve - Blender script (2.80 compatible!)
================================

## Introduction

Modeling curved shapes is hard. This script tries to help with this task by using blender curve objects and interpolating the mesh surface between them. Instead of tracing object's shape by hand with polygons:

1. Outline it with Bezier curve
1. Duplicate the curve and transform it as You like
1. Select both curves
1. In '3d View' press `shift + A` keys to open `Add` menu
1. There should be `Mesh From Curve` at the bottom of `Mesh` category
1. Click the `Mesh From Curve` option
1. In the tool options there should be a slider for segment count and the cyclic checkbox - adjust at will


## Blender version

* **2.80** - use script from `master` branch
* **2.72b** - use script from [2.72b tag](https://github.com/Scthe/MeshFromCurve_blender/tree/2.72b)
* versions between **2.72b** and **2.80** - blender changed toolbar API, use script version for **2.72b**. If the `Mesh From Curve` button is not visible, use search tool (by default under `SPACEBAR` key).


## Example

1. See provided `Violin_example.blend` file in this repo
1. Run the `meshFromCurve.py` (should be already open in text editor, it's the same file as in the root of the repo)
1. Select curves that You want to create mesh from e.g. `outer.001` and `outer.002` (in `curves` collection)
1. In `3d View` press `shift + A` keys to open `Add` menu
1. There should be `Mesh From Curve` at the bottom of `Mesh` category - it was appended when we have run the script in step 2
1. Click the `Mesh From Curve` option
1. In the tool options there should be a slider for segment count and the cyclic checkbox - adjust at will
1. Continue editing!

![step1]

*After step 4*

![step2]

*Adjustments*

## A little bit down the road

![img_fin]
*This should look like a piece of cake now. Model is provided in the blendfile if You want to play with it*

###### The script does not guarantee that every segment will have equal length (red path on the following image). It does guarrantee that distances between the segment points WHEN FOLLOWING THE CURVE (blue path) will be equal.

![img2]

[step1]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/step1.jpg
[step2]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/step2.jpg
[img_fin]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/img_fin.png
[img2]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/img2.jpg
