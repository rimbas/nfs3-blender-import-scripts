# Collection of scripts to help import NFS3:HP data into Blender

# Constructing an atlas

## 0. Install Python prerequisites

`pip install numpy pillow "drawsvg~=2.0"`

## 1. Run FSHTOOL to extract the track's QFS texture file into BMP files

[Denis Auroux Need for Speed resources](http://www.math.polytechnique.fr/cmat/auroux/nfs/)

Do not rename any resulting files.

## 2. Run the atlas UV mapper script to save a combined atlas and UV mapping JSON

`python atlas_uv_mapper.py {texture_directory} {frd_filename}`

## 3. Run the importer script in Python

Change the `track_id` variable to select which track to import.
