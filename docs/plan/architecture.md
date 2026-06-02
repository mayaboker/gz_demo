# Architecture

## System Overview

This is a standalone Gazebo project. It uses Gazebo SDF worlds, Gazebo models,
mesh assets, shell scripts, and Python tests. It must not depend on ROS, ROS 2,
`ros2 launch`, colcon, ROS packages, or ROS environment setup.

## Components

| Component | Location | Responsibility |
| --- | --- | --- |
| Gazebo worlds | `worlds/` | Simulation environment definitions |
| Gazebo models | `models/` | Reusable simulated objects and robots |
| Launch scripts | `launch/` | Standalone Gazebo startup scripts |
| Configuration | `config/` | Parameters, bridge config, and runtime settings |
| Source code | `src/` | Project packages or application code |
| Tests | `tests/` | Static and integration checks for project assets |

## Project Layout

```text
models/
├── falling_box/
│   ├── model.config
│   └── model.sdf
├── ground_terrain/
│   ├── model.config
│   ├── model.sdf
│   └── meshes/
│       └── ground_terrain.dae
├── level_terrain_a/
│   ├── model.config
│   ├── model.sdf
│   └── materials/
│       └── textures/
│           └── level_a.png
├── level_terrain_b/
│   ├── model.config
│   ├── model.sdf
│   └── materials/
│       └── textures/
│           └── level_b.png
├── level_terrain_c/
│   ├── model.config
│   ├── model.sdf
│   └── materials/
│       └── textures/
│           └── level_c.png
├── level_vehicle/
│   ├── model.config
│   └── model.sdf
├── multi_texture_terrain/
│   ├── model.config
│   ├── model.sdf
│   ├── materials/
│   │   └── textures/
│   │       ├── grass_checker.png
│   │       └── stone_checker.png
│   └── meshes/
│       └── multi_texture_terrain.dae
└── textured_terrain/
    ├── model.config
    ├── model.sdf
    ├── materials/
    │   └── textures/
    │       └── terrain_checker.png
    └── meshes/
        └── textured_terrain.dae
worlds/
├── basic_terrain.sdf
├── levels_terrain.sdf
├── multi_texture_terrain.sdf
└── textured_terrain.sdf
launch/
├── basic_terrain.sh
├── levels_terrain.sh
├── multi_texture_terrain.sh
└── textured_terrain.sh
tests/
└── test_ground_terrain_model.py
scripts/
└── drive_level_vehicle.sh
```

The launch script sets `GZ_SIM_RESOURCE_PATH` to include the local `models/` directory before starting Gazebo with `gz sim`. That lets the world reference the terrain with `model://ground_terrain`.

## Data Flow

For Milestone 1, there is no ROS namespace or ROS launch layer. The world loads the terrain model through Gazebo resource resolution:

```text
launch/basic_terrain.sh
-> sets GZ_SIM_RESOURCE_PATH
-> starts Gazebo with gz sim worlds/basic_terrain.sdf
-> world includes model://ground_terrain
-> world includes model://falling_box above the terrain
-> model.sdf uses meshes/ground_terrain.dae for visual and collision geometry
-> falling_box drops onto the terrain to make collision behavior visible
```

Milestone 2 adds a textured terrain variant:

```text
launch/textured_terrain.sh
-> sets GZ_SIM_RESOURCE_PATH
-> starts Gazebo with gz sim worlds/textured_terrain.sdf
-> world includes model://textured_terrain
-> world includes model://falling_box above the terrain
-> textured_terrain.dae references materials/textures/terrain_checker.png
-> textured_terrain.dae supplies UV coordinates for texture placement
-> falling_box drops onto the textured terrain for collision verification
```

Milestone 3 adds a multi-texture terrain demo:

```text
launch/multi_texture_terrain.sh
-> sets GZ_SIM_RESOURCE_PATH
-> starts Gazebo with gz sim worlds/multi_texture_terrain.sdf
-> world includes model://multi_texture_terrain
-> world includes model://falling_box above the terrain
-> multi_texture_terrain.dae references grass_checker.png and stone_checker.png
-> separate DAE triangle material groups assign the two textures
-> falling_box drops onto the multi-texture terrain for collision verification
```

Milestone 4 adds Gazebo level loading:

```text
launch/levels_terrain.sh
-> sets GZ_SIM_RESOURCE_PATH
-> starts Gazebo with gz sim --levels worlds/levels_terrain.sdf
-> world defines level_vehicle as a performer
-> world defines level_a, level_b, and level_c under the gz::sim levels plugin
-> each level references one terrain model with a unique texture
-> TriggeredPublisher maps W/X/A/D/S keyboard events to /model/level_vehicle/cmd_vel
-> scripts/drive_level_vehicle.sh remains available for terminal-based driving
-> the vehicle can move between levels so terrain models load and unload visibly
-> adjacent level terrain tiles overlap slightly to avoid collision gaps
-> falling_box starts in level_a and lands on the loaded terrain
```

## Open Questions

- 
