Mesh from curve - Blender script
================================

## Introduction

Modeling curved shapes is hard. This script tries to help with this task by using blender curve objects and interpolating the mesh surface between them. Instead of tracing object's shape by hand with polygons:

1. Outline it with Bezier curve
1. Duplicate the curve and transform it as You like
1. Select both curves
1. Click the 'Mesh From Curve' button on your toolshelf
1. Adjust the segment count

###### Last tested blender version: 2.72b


## Example

1. Open the provided Violin_example blendfile
1. Run the 'curveScript' ( it is already open in the text editor)
1. Select curves that You want to create mesh from, f.e. 'outer.001' and 'outer.002' on layer 2
1. In toolshelf ( shortcut: 't' in 3D View) select the Create tab ( change to Object Mode if necessary)
1. There should be 'Mesh From Curve' button at the bottom - it was appended when we've run the script in step 2
1. Click the 'Mesh From Curve' button
1. In the tool options on the toolshelf should be slider for segment count and the cyclic checkbox - adjust at will
1. Continue editing!

![step1]
*After step 4*

![step2]
*Adjustments*

## A little bit down the road

![img_fin]
*This should look like a piece of cake now. ( Model is provided in the blendfile if You want to play with it)*

###### The script does not guarantee that every segment will have equal length ( red path on the following image). It does guarrantee that distances between the segment points WHEN FOLLOWING THE CURVE ( blue path) will be equal.

![img2]

[step1]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/step1.jpg
[step2]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/step2.jpg
[img_fin]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/img_fin.png
[img2]: https://raw.github.com/Scthe/MeshFromCurve_blender/master/images/img2.jpg
