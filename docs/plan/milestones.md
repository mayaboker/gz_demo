# Milestones

## Milestone 1: Basic Terrain World

### Deliverables

- [x] Ground terrain mesh at `models/ground_terrain/meshes/ground_terrain.dae`
- [x] Gazebo terrain model at `models/ground_terrain/model.sdf`
- [x] Gazebo model metadata at `models/ground_terrain/model.config`
- [x] Basic world at `worlds/basic_terrain.sdf`
- [x] Standalone Gazebo launch script at `launch/basic_terrain.sh`
- [x] Static model test at `tests/test_ground_terrain_model.py`
- [x] Dynamic falling box model at `models/falling_box/model.sdf`

### Acceptance Criteria

- [x] The mesh file exists.
- [x] `model.sdf` uses the mesh for visual geometry.
- [x] `model.sdf` uses the mesh for collision geometry.
- [x] Visual and collision mesh URIs match.
- [x] `worlds/basic_terrain.sdf` includes `model://ground_terrain`.
- [x] `worlds/basic_terrain.sdf` includes `model://falling_box` above the ground.
- [x] `falling_box` is dynamic and has visual and collision box geometry.
- [x] The launch script sets `GZ_SIM_RESOURCE_PATH`.
- [x] The launch script uses `gz sim` directly, without ROS or ROS 2.


## Milestone 2: Simulation Behavior

### Deliverables

- [x] Textured terrain model at `models/textured_terrain/model.sdf`
- [x] Textured DAE mesh at `models/textured_terrain/meshes/textured_terrain.dae`
- [x] Terrain texture at `models/textured_terrain/materials/textures/terrain_checker.png`
- [x] Textured world at `worlds/textured_terrain.sdf`
- [x] Standalone Gazebo launch script at `launch/textured_terrain.sh`
- [x] Texture workflow notes at `docs/plan/texturing.md`

### Acceptance Criteria

- [x] The textured model uses the DAE mesh for visual geometry.
- [x] The textured model uses the same DAE mesh for collision geometry.
- [x] The DAE mesh references `terrain_checker.png`.
- [x] The DAE mesh contains texture coordinates.
- [x] `worlds/textured_terrain.sdf` includes `model://textured_terrain`.
- [x] `worlds/textured_terrain.sdf` includes `model://falling_box` above the terrain.
- [x] `launch/textured_terrain.sh` sets `GZ_SIM_RESOURCE_PATH` and uses `gz sim`.
- [x] A headless Gazebo integration test verifies the box lands on the textured terrain.
- [x] The docs explain the current texture workflow and other texture options.

## Milestone 3: Demo Readiness

### Deliverables

- [x] Multi-texture terrain model at `models/multi_texture_terrain/model.sdf`
- [x] Multi-texture DAE mesh at `models/multi_texture_terrain/meshes/multi_texture_terrain.dae`
- [x] Grass texture at `models/multi_texture_terrain/materials/textures/grass_checker.png`
- [x] Stone texture at `models/multi_texture_terrain/materials/textures/stone_checker.png`
- [x] Multi-texture world at `worlds/multi_texture_terrain.sdf`
- [x] Standalone Gazebo launch script at `launch/multi_texture_terrain.sh`
- [x] Demo run instructions in `README.md`

### Acceptance Criteria

- [x] The multi-texture model uses the DAE mesh for visual geometry.
- [x] The multi-texture model uses the same DAE mesh for collision geometry.
- [x] The DAE mesh references both texture files.
- [x] The DAE mesh contains two material regions.
- [x] `worlds/multi_texture_terrain.sdf` includes `model://multi_texture_terrain`.
- [x] `worlds/multi_texture_terrain.sdf` includes `model://falling_box` above the terrain.
- [x] `launch/multi_texture_terrain.sh` sets `GZ_SIM_RESOURCE_PATH` and uses `gz sim`.
- [x] A headless Gazebo integration test verifies the box lands on the multi-texture terrain.


## Milestone 4: leveling

### Deliverables

- [x] Level world at `worlds/levels_terrain.sdf`
- [x] Standalone Gazebo levels launcher at `launch/levels_terrain.sh`
- [x] Level A terrain model at `models/level_terrain_a/model.sdf`
- [x] Level B terrain model at `models/level_terrain_b/model.sdf`
- [x] Level C terrain model at `models/level_terrain_c/model.sdf`
- [x] Distinct texture for each level terrain model
- [x] Driveable level performer vehicle at `models/level_vehicle/model.sdf`
- [x] Vehicle drive helper at `scripts/drive_level_vehicle.sh`
- [x] Keyboard-triggered vehicle commands from `worlds/levels_terrain.sdf`

### Acceptance Criteria

- [x] The world defines a `gz::sim` levels plugin.
- [x] The world defines `level_vehicle` as a performer.
- [x] The world defines three levels with box volumes, buffers, and model refs.
- [x] Each level terrain model uses a unique texture so load/unload changes are visible.
- [x] The launch script runs `gz sim --levels`.
- [x] The world can command the vehicle from keyboard events.
- [x] The drive helper publishes velocity commands to `/model/level_vehicle/cmd_vel`.
- [x] A headless Gazebo integration test verifies the box collides with the loaded level terrain.

## Milestone 5: leveling with sub models

### Deliverables
- [x] create a new world and launch like before
- [x] add sub module, like box sphere and cone to each level

### Acceptance Criteria
- [x] the submoudle loaded and unload as part of the leveling model


## Milestone 6: leveling with multiple modules

### Deliverables
- [x] using the models from milestone5 but don't use submodule idea, each level contain multiple items
- [x] create new launch and world

### Acceptance Criteria
- [x] each level loads multiple independent marker model instances through direct level refs
