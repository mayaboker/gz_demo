# Texturing

## Current Approach

Milestone 2 adds texture through the mesh file:

```text
models/textured_terrain/meshes/textured_terrain.dae
models/textured_terrain/materials/textures/terrain_checker.png
```

The DAE file contains UV coordinates and references the PNG texture. The Gazebo
model uses the DAE mesh for both visual and collision geometry, but only the
visual rendering uses the texture.

## How To Add A Texture

1. Put the image in the model directory, usually under `materials/textures/`.
2. Add UV coordinates to the mesh so each vertex maps to a point on the image.
3. Reference the image from the DAE material.
4. Use the textured DAE from `model.sdf`.
5. Keep collision geometry simple and aligned with the visual mesh.

## Other Options

- Define material color or PBR maps in `model.sdf` instead of inside the DAE.
- Export the mesh, UVs, and materials from Blender as a DAE file.
- Use a heightmap terrain when the ground should have real elevation changes.
- Use separate visual and collision meshes when the visual mesh is detailed but
  collision should stay simple.

## Multiple Textures

Milestone 3 uses multiple DAE material regions:

```text
models/multi_texture_terrain/meshes/multi_texture_terrain.dae
models/multi_texture_terrain/materials/textures/grass_checker.png
models/multi_texture_terrain/materials/textures/stone_checker.png
```

The DAE has one triangle group using `grass_material` and one triangle group
using `stone_material`. Each material references a different PNG image. This is
useful when one mesh should show different terrain areas without splitting the
terrain into separate Gazebo models.

Milestone 4 uses another valid option: each level terrain model is a box with an
SDF PBR `albedo_map`. This keeps the model geometry simple while still giving
each level a distinct texture:

```text
models/level_terrain_a/materials/textures/level_a.png
models/level_terrain_b/materials/textures/level_b.png
models/level_terrain_c/materials/textures/level_c.png
```
