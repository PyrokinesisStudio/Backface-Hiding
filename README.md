# Backface-Hiding
Blender add-on to hide backfacing or non-visible geometry (useful for retopology with X-Ray mode for example)

Here's a comparison with the built-in Backface Culling :
 
![Backface Hiding screenshot](https://i.imgur.com/O0fAeh1.png)

![](https://raw.githubusercontent.com/ChameleonScales/Blender-individual-icons/master/PNG-16x16/ICON_ERROR.png) **Warning :** This add-on doesn't perform in real-time like Backface Culling, it only updates the hidden geometry every time you click on the button.
Also, at the current version, if your object is rotated, you will need to either apply or clear the rotation in order for the hiding features to be oriented properly.

## Installing (regular python addon) :

* Save the raw [*Backface_Hiding_v0_1.py*](https://raw.githubusercontent.com/ChameleonScales/Backface-Hiding/master/Backface_Hiding_v0_1.py) file anywhere on your computer
* In Blender, open the User Preferences and go in the “Addons” tab
* Click on “Install from file” at the bottom
* Find the addon you downloaded
* Enable it with the checkbox
* You should now find the buttons in the Properties region of any 3DView in Edit mode, under Mesh Display.

## Features :

* **Hide backfacing :** hides the backfacing geometry (can be revealed with Alt+H)
* **Hide non-visible :** hides the geometry that's occluded by the view, including the screen area outside of the 3DView editor.

## Add keyboard shortcuts :

Go in User Preferencess > Input > 3DView > Mesh, click on "Add New", expand the added one (called "None"), in the text field type `object.hide_backfacing` and chose your keys. One that is not already used is Q.
For the "Hide non-visible" button the operator is `object.hide_non_visible` and another non-used key is D.

## TODO list :

* Make it work on rotated objects
* Add default keyboard shortcuts and display the shortcut options in the add-on's properties

This addon was made on Blender 2.79
