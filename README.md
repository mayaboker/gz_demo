# gz_demo

Standalone Gazebo demo project workspace.

## Project Documents

- [Project overview](docs/plan/project-overview.md)
- [Milestones](docs/plan/milestones.md)
- [Architecture](docs/plan/architecture.md)
- [Decisions](docs/plan/decisions.md)
- [Functional requirements](docs/requirements/functional-requirements.md)
- [Technical requirements](docs/requirements/technical-requirements.md)

## Layout

```text
docs/          Planning, requirements, decisions, and notes
src/           Source code
config/        Runtime and tool configuration
launch/        Standalone Gazebo launch scripts
worlds/        Gazebo world files
models/        Gazebo models
scripts/       Utility scripts
tests/         Static and integration tests
```

## Run Milestone 1

```bash
./launch/basic_terrain.sh
```

The launch script sets `GZ_SIM_RESOURCE_PATH` to the local `models/` directory and starts Gazebo with `gz sim worlds/basic_terrain.sdf`.

## Run Milestone 2

```bash
./launch/textured_terrain.sh
```

The textured terrain world uses `models/textured_terrain/meshes/textured_terrain.dae` and the checker texture documented in [Texturing](docs/plan/texturing.md).

## Run Milestone 3

```bash
./launch/multi_texture_terrain.sh
```

The multi-texture terrain world uses one DAE mesh with two material regions:
grass and stone. The falling box should land on the textured mesh surface.

## Run Milestone 4

```bash
./launch/levels_terrain.sh
```

The levels demo starts Gazebo with `--levels`. It defines three level terrain
tiles with different textures and uses a yellow vehicle as the level performer.
The world SDF contains `TriggeredPublisher` plugins that command the vehicle
from Gazebo keyboard events.

Keyboard controls:

```text
W  forward
X  reverse
A  turn left
D  turn right
S  stop
```

To disable only the external helper, no action is needed. It is already off by
default:

```bash
AUTO_DRIVE=0 ./launch/levels_terrain.sh
```

You can still publish manual velocity commands from another terminal:

```bash
./scripts/drive_level_vehicle.sh
```

Or send one command directly:

```bash
gz topic \
  -t /model/level_vehicle/cmd_vel \
  -m gz.msgs.Twist \
  -p "linear: {x: 2.0}"
```

## Run Milestone 5

```bash
./launch/levels_submodels.sh
```

The submodel levels demo starts Gazebo with `--levels`. It reuses the three
level terrain tiles and loads a box, sphere, and cone with each level by listing
those model instance names in the matching `<level>` refs.

## Run Milestone 6

```bash
./launch/levels_multi_items.sh
```

The multi-item levels demo starts Gazebo with `--levels`. It reuses the
Milestone 5 box, sphere, and cone models as independent top-level includes. Each
level directly refs multiple item instances, so there is no grouped submodel.

## Test

```bash
python3 -m pytest tests
```

The test suite includes static SDF checks and headless Gazebo integration tests that record simulation state to confirm the falling box lands on all terrain worlds, including the levels world.
