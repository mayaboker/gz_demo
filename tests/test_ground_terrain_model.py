from pathlib import Path
import os
import shutil
import sqlite3
import subprocess
import xml.etree.ElementTree as ET

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = PROJECT_ROOT / "models" / "ground_terrain"
FALLING_BOX_ROOT = PROJECT_ROOT / "models" / "falling_box"
TEXTURED_TERRAIN_ROOT = PROJECT_ROOT / "models" / "textured_terrain"
MULTI_TEXTURE_TERRAIN_ROOT = PROJECT_ROOT / "models" / "multi_texture_terrain"
LEVEL_VEHICLE_ROOT = PROJECT_ROOT / "models" / "level_vehicle"
DEM_TERRAIN_ROOT = PROJECT_ROOT / "models" / "dem_terrain"
LEVEL_TERRAIN_ROOTS = {
    "model://level_terrain_a": PROJECT_ROOT / "models" / "level_terrain_a",
    "model://level_terrain_b": PROJECT_ROOT / "models" / "level_terrain_b",
    "model://level_terrain_c": PROJECT_ROOT / "models" / "level_terrain_c",
}
LEVEL_MARKER_ROOTS = {
    "model://level_marker_box": PROJECT_ROOT / "models" / "level_marker_box",
    "model://level_marker_sphere": PROJECT_ROOT / "models" / "level_marker_sphere",
    "model://level_marker_cone": PROJECT_ROOT / "models" / "level_marker_cone",
}
MESH_URI = "model://ground_terrain/meshes/ground_terrain.dae"
TEXTURED_MESH_URI = "model://textured_terrain/meshes/textured_terrain.dae"
MULTI_TEXTURE_MESH_URI = (
    "model://multi_texture_terrain/meshes/multi_texture_terrain.dae"
)
DEM_DAE_PATH = PROJECT_ROOT / "data" / "dae" / "example_dem_100m.dae"
DEM_MESH_URI = "../../data/dae/example_dem_100m.dae"


def test_ground_terrain_mesh_exists():
    mesh_path = MODEL_ROOT / "meshes" / "ground_terrain.dae"

    assert mesh_path.is_file()


def test_model_uses_same_mesh_for_visual_and_collision():
    model_tree = ET.parse(MODEL_ROOT / "model.sdf")
    model_root = model_tree.getroot()

    visual_uris = [
        uri.text
        for uri in model_root.findall(".//visual/geometry/mesh/uri")
    ]
    collision_uris = [
        uri.text
        for uri in model_root.findall(".//collision/geometry/mesh/uri")
    ]

    assert visual_uris == [MESH_URI]
    assert collision_uris == [MESH_URI]
    assert visual_uris == collision_uris


def test_world_includes_ground_terrain_model():
    world_tree = ET.parse(PROJECT_ROOT / "worlds" / "basic_terrain.sdf")
    world_root = world_tree.getroot()
    include_uris = [
        uri.text
        for uri in world_root.findall(".//include/uri")
    ]

    assert "model://ground_terrain" in include_uris


def test_world_includes_dynamic_falling_box_above_ground():
    world_tree = ET.parse(PROJECT_ROOT / "worlds" / "basic_terrain.sdf")
    world_root = world_tree.getroot()
    includes = world_root.findall(".//include")

    falling_box_includes = [
        include
        for include in includes
        if include.findtext("uri") == "model://falling_box"
    ]

    assert len(falling_box_includes) == 1
    assert _include_pose_z(world_root, "model://falling_box") > (
        _include_pose_z(world_root, "model://ground_terrain") + 2.0
    )


def test_falling_box_is_dynamic_with_visual_and_collision_box():
    model_tree = ET.parse(FALLING_BOX_ROOT / "model.sdf")
    model_root = model_tree.getroot()

    assert model_root.findtext(".//model/static") == "false"
    assert model_root.findtext(".//visual/geometry/box/size") == "1 1 1"
    assert model_root.findtext(".//collision/geometry/box/size") == "1 1 1"


def test_launch_sets_gazebo_resource_path():
    launch_path = PROJECT_ROOT / "launch" / "basic_terrain.sh"
    launch_text = launch_path.read_text(encoding="utf-8")

    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "/models" in launch_text
    assert "gz sim" in launch_text
    assert "ros2" not in launch_text.lower()
    assert "launch.py" not in launch_text


def test_ros_launch_file_is_not_present():
    assert not (PROJECT_ROOT / "launch" / "basic_terrain.launch.py").exists()


def test_textured_terrain_has_texture_and_uvs():
    texture_path = (
        TEXTURED_TERRAIN_ROOT
        / "materials"
        / "textures"
        / "terrain_checker.png"
    )
    mesh_tree = ET.parse(TEXTURED_TERRAIN_ROOT / "meshes" / "textured_terrain.dae")
    mesh_root = mesh_tree.getroot()
    namespace = {"dae": "http://www.collada.org/2005/11/COLLADASchema"}

    assert texture_path.is_file()
    assert (
        mesh_root.findtext(".//dae:library_images/dae:image/dae:init_from", namespaces=namespace)
        == "../materials/textures/terrain_checker.png"
    )
    assert mesh_root.find(".//dae:input[@semantic='TEXCOORD']", namespace) is not None
    assert mesh_root.find(".//dae:source[@id='textured_terrain_uvs']", namespace) is not None


def test_textured_model_uses_same_mesh_for_visual_and_collision():
    model_tree = ET.parse(TEXTURED_TERRAIN_ROOT / "model.sdf")
    model_root = model_tree.getroot()

    visual_uris = [
        uri.text
        for uri in model_root.findall(".//visual/geometry/mesh/uri")
    ]
    collision_uris = [
        uri.text
        for uri in model_root.findall(".//collision/geometry/mesh/uri")
    ]

    assert visual_uris == [TEXTURED_MESH_URI]
    assert collision_uris == [TEXTURED_MESH_URI]
    assert visual_uris == collision_uris


def test_textured_world_and_launch_script_are_standalone_gazebo():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "textured_terrain.sdf").getroot()
    include_uris = [
        uri.text
        for uri in world_root.findall(".//include/uri")
    ]
    launch_text = (PROJECT_ROOT / "launch" / "textured_terrain.sh").read_text(
        encoding="utf-8"
    )

    assert "model://textured_terrain" in include_uris
    assert "model://falling_box" in include_uris
    assert _include_pose_z(world_root, "model://falling_box") > (
        _include_pose_z(world_root, "model://textured_terrain") + 2.0
    )
    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim" in launch_text
    assert "ros2" not in launch_text.lower()
    assert "textured_terrain.sdf" in launch_text


def test_multi_texture_terrain_has_two_textures_and_material_regions():
    texture_root = MULTI_TEXTURE_TERRAIN_ROOT / "materials" / "textures"
    mesh_tree = ET.parse(
        MULTI_TEXTURE_TERRAIN_ROOT / "meshes" / "multi_texture_terrain.dae"
    )
    mesh_root = mesh_tree.getroot()
    namespace = {"dae": "http://www.collada.org/2005/11/COLLADASchema"}
    image_paths = [
        node.text
        for node in mesh_root.findall(
            ".//dae:library_images/dae:image/dae:init_from",
            namespace,
        )
    ]
    triangle_materials = [
        node.attrib["material"]
        for node in mesh_root.findall(".//dae:triangles", namespace)
    ]

    assert (texture_root / "grass_checker.png").is_file()
    assert (texture_root / "stone_checker.png").is_file()
    assert image_paths == [
        "../materials/textures/grass_checker.png",
        "../materials/textures/stone_checker.png",
    ]
    assert triangle_materials == ["grass_material", "stone_material"]
    assert mesh_root.find(".//dae:input[@semantic='TEXCOORD']", namespace) is not None


def test_multi_texture_model_uses_same_mesh_for_visual_and_collision():
    model_tree = ET.parse(MULTI_TEXTURE_TERRAIN_ROOT / "model.sdf")
    model_root = model_tree.getroot()

    visual_uris = [
        uri.text
        for uri in model_root.findall(".//visual/geometry/mesh/uri")
    ]
    collision_uris = [
        uri.text
        for uri in model_root.findall(".//collision/geometry/mesh/uri")
    ]

    assert visual_uris == [MULTI_TEXTURE_MESH_URI]
    assert collision_uris == [MULTI_TEXTURE_MESH_URI]
    assert visual_uris == collision_uris


def test_multi_texture_world_and_launch_script_are_standalone_gazebo():
    world_root = ET.parse(
        PROJECT_ROOT / "worlds" / "multi_texture_terrain.sdf"
    ).getroot()
    include_uris = [
        uri.text
        for uri in world_root.findall(".//include/uri")
    ]
    launch_text = (PROJECT_ROOT / "launch" / "multi_texture_terrain.sh").read_text(
        encoding="utf-8"
    )

    assert "model://multi_texture_terrain" in include_uris
    assert "model://falling_box" in include_uris
    assert _include_pose_z(world_root, "model://falling_box") > (
        _include_pose_z(world_root, "model://multi_texture_terrain") + 2.0
    )
    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim" in launch_text
    assert "ros2" not in launch_text.lower()
    assert "multi_texture_terrain.sdf" in launch_text


def test_levels_world_defines_vehicle_performer_and_three_levels():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_terrain.sdf").getroot()
    level_plugin = world_root.find(".//plugin[@name='gz::sim']")
    levels = level_plugin.findall("level")
    include_uris = [
        uri.text
        for uri in world_root.findall(".//include/uri")
    ]

    assert level_plugin is not None
    assert level_plugin.attrib["filename"] == "dummy"
    assert level_plugin.findtext("performer/ref") == "level_vehicle"
    assert level_plugin.findtext("performer/geometry/box/size") == "1.4 1.0 1.0"
    assert [level.attrib["name"] for level in levels] == [
        "level_a",
        "level_b",
        "level_c",
    ]
    assert [
        [ref.text for ref in level.findall("ref")]
        for level in levels
    ] == [
        ["level_terrain_a", "level_terrain_b", "falling_box"],
        ["level_terrain_a", "level_terrain_b", "level_terrain_c"],
        ["level_terrain_b", "level_terrain_c"],
    ]
    assert {
        "model://level_terrain_a",
        "model://level_terrain_b",
        "model://level_terrain_c",
        "model://falling_box",
        "model://level_vehicle",
    }.issubset(include_uris)


def test_level_terrain_models_have_distinct_textures():
    expected_maps = {
        "model://level_terrain_a": "model://level_terrain_a/materials/textures/level_a.png",
        "model://level_terrain_b": "model://level_terrain_b/materials/textures/level_b.png",
        "model://level_terrain_c": "model://level_terrain_c/materials/textures/level_c.png",
    }

    for model_uri, model_root_path in LEVEL_TERRAIN_ROOTS.items():
        model_tree = ET.parse(model_root_path / "model.sdf")
        model_root = model_tree.getroot()
        texture_uri = model_root.findtext(".//visual/material/pbr/metal/albedo_map")
        texture_path = model_root_path / "materials" / "textures" / Path(texture_uri).name

        assert model_root.findtext(".//model/static") == "true"
        assert model_root.findtext(".//visual/geometry/box/size") == "10.5 8 0.02"
        assert model_root.findtext(".//collision/geometry/box/size") == "10.5 8 0.02"
        assert texture_uri == expected_maps[model_uri]
        assert texture_path.is_file()

    assert len(set(expected_maps.values())) == len(expected_maps)


def test_level_terrain_tiles_overlap_for_vehicle_transition():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_terrain.sdf").getroot()
    tile_extents = []

    for model_uri, model_root_path in LEVEL_TERRAIN_ROOTS.items():
        model_tree = ET.parse(model_root_path / "model.sdf")
        model_root = model_tree.getroot()
        tile_width = float(
            model_root.findtext(".//collision/geometry/box/size").split()[0]
        )
        tile_center_x = _include_pose_x(world_root, model_uri)
        tile_extents.append(
            (
                tile_center_x - tile_width / 2,
                tile_center_x + tile_width / 2,
            )
        )

    tile_extents.sort()

    for left_tile, right_tile in zip(tile_extents, tile_extents[1:]):
        assert left_tile[1] >= right_tile[0]


def test_levels_launch_script_is_standalone_gazebo_with_levels_enabled():
    launch_text = (PROJECT_ROOT / "launch" / "levels_terrain.sh").read_text(
        encoding="utf-8"
    )

    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim --levels" in launch_text
    assert "levels_terrain.sdf" in launch_text
    assert "AUTO_DRIVE" in launch_text
    assert 'AUTO_DRIVE="${AUTO_DRIVE:-0}"' in launch_text
    assert "drive_level_vehicle.sh" in launch_text
    assert "ros2" not in launch_text.lower()


def test_levels_world_commands_vehicle_from_keyboard():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_terrain.sdf").getroot()
    publishers = world_root.findall(
        ".//plugin[@name='gz::sim::systems::TriggeredPublisher']"
    )
    commands = {
        publisher.findtext("input/match"): publisher.find("output").text
        for publisher in publishers
    }

    assert len(publishers) == 5
    assert all(
        publisher.find("input").attrib["topic"] == "/keyboard/keypress"
        and publisher.find("input").attrib["type"] == "gz.msgs.Int32"
        for publisher in publishers
    )
    assert all(
        publisher.find("output").attrib["topic"] == "/model/level_vehicle/cmd_vel"
        and publisher.find("output").attrib["type"] == "gz.msgs.Twist"
        for publisher in publishers
    )
    assert set(commands) == {"87", "88", "65", "68", "83"}
    assert "linear: {x: 1.2}" in commands["87"]
    assert "linear: {x: -0.8}" in commands["88"]
    assert "angular: {z: 0.8}" in commands["65"]
    assert "angular: {z: -0.8}" in commands["68"]
    assert "linear: {x: 0.0}" in commands["83"]
    assert "angular: {z: 0.0}" in commands["83"]


def test_level_vehicle_is_driveable_with_diff_drive():
    model_root = ET.parse(LEVEL_VEHICLE_ROOT / "model.sdf").getroot()
    plugin = model_root.find(".//plugin[@name='gz::sim::systems::DiffDrive']")
    drive_script = (PROJECT_ROOT / "scripts" / "drive_level_vehicle.sh").read_text(
        encoding="utf-8"
    )

    assert plugin is not None
    assert plugin.attrib["filename"] == "gz-sim-diff-drive-system"
    assert plugin.findtext("left_joint") == "left_wheel_joint"
    assert plugin.findtext("right_joint") == "right_wheel_joint"
    assert plugin.findtext("topic") == "/model/level_vehicle/cmd_vel"
    assert "/model/level_vehicle/cmd_vel" in drive_script
    assert "gz topic" in drive_script
    assert "gz.msgs.Twist" in drive_script


def test_level_marker_models_are_static_shapes():
    expected_geometry = {
        "model://level_marker_box": "box",
        "model://level_marker_sphere": "sphere",
        "model://level_marker_cone": "cone",
    }

    for model_uri, model_root_path in LEVEL_MARKER_ROOTS.items():
        model_root = ET.parse(model_root_path / "model.sdf").getroot()
        geometry = model_root.find(".//visual/geometry")

        assert model_root.findtext(".//model/static") == "true"
        assert geometry.find(expected_geometry[model_uri]) is not None
        assert model_root.find(".//collision/geometry") is not None


def test_levels_submodels_world_refs_shapes_in_matching_levels():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_submodels.sdf").getroot()
    level_plugin = world_root.find(".//plugin[@name='gz::sim']")
    levels = level_plugin.findall("level")
    include_names = {
        include.findtext("name")
        for include in world_root.findall(".//include")
    }
    include_uris = [
        include.findtext("uri")
        for include in world_root.findall(".//include")
    ]

    assert level_plugin is not None
    assert level_plugin.attrib["filename"] == "dummy"
    assert level_plugin.findtext("performer/ref") == "level_vehicle"
    assert [level.attrib["name"] for level in levels] == [
        "level_a",
        "level_b",
        "level_c",
    ]
    assert [
        [ref.text for ref in level.findall("ref")]
        for level in levels
    ] == [
        [
            "level_terrain_a",
            "level_a_box",
            "level_a_sphere",
            "level_a_cone",
            "falling_box",
        ],
        [
            "level_terrain_b",
            "level_b_box",
            "level_b_sphere",
            "level_b_cone",
        ],
        [
            "level_terrain_c",
            "level_c_box",
            "level_c_sphere",
            "level_c_cone",
        ],
    ]
    assert {
        "model://level_marker_box",
        "model://level_marker_sphere",
        "model://level_marker_cone",
    }.issubset(include_uris)

    for level in levels:
        for ref in level.findall("ref"):
            assert ref.text in include_names


def test_levels_submodels_cones_are_clear_of_vehicle_path():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_submodels.sdf").getroot()

    for cone_name in ["level_a_cone", "level_b_cone", "level_c_cone"]:
        cone_include = _include_by_name(world_root, cone_name)
        cone_y = float(cone_include.findtext("pose").split()[1])

        assert abs(cone_y) >= 2.0


def test_levels_submodels_launch_script_is_standalone_gazebo_with_levels_enabled():
    launch_text = (PROJECT_ROOT / "launch" / "levels_submodels.sh").read_text(
        encoding="utf-8"
    )

    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim --levels" in launch_text
    assert "levels_submodels.sdf" in launch_text
    assert "ros2" not in launch_text.lower()


def test_levels_multi_items_world_refs_multiple_independent_items_per_level():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_multi_items.sdf").getroot()
    level_plugin = world_root.find(".//plugin[@name='gz::sim']")
    levels = level_plugin.findall("level")
    include_names = {
        include.findtext("name")
        for include in world_root.findall(".//include")
    }
    include_uris = [
        include.findtext("uri")
        for include in world_root.findall(".//include")
    ]

    assert level_plugin is not None
    assert level_plugin.attrib["filename"] == "dummy"
    assert level_plugin.findtext("performer/ref") == "level_vehicle"
    assert [level.attrib["name"] for level in levels] == [
        "level_a",
        "level_b",
        "level_c",
    ]
    assert {
        "model://level_marker_box",
        "model://level_marker_sphere",
        "model://level_marker_cone",
    }.issubset(include_uris)

    for level in levels:
        refs = [ref.text for ref in level.findall("ref")]
        marker_refs = [ref for ref in refs if "_box_" in ref or "_sphere_" in ref or "_cone_" in ref]

        assert len(marker_refs) == 6
        assert sum("_box_" in ref for ref in marker_refs) == 2
        assert sum("_sphere_" in ref for ref in marker_refs) == 2
        assert sum("_cone_" in ref for ref in marker_refs) == 2
        assert all(ref in include_names for ref in refs)


def test_levels_multi_items_cones_are_clear_of_vehicle_path():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "levels_multi_items.sdf").getroot()
    cone_names = [
        include.findtext("name")
        for include in world_root.findall(".//include")
        if include.findtext("uri") == "model://level_marker_cone"
    ]

    assert len(cone_names) == 6
    for cone_name in cone_names:
        cone_include = _include_by_name(world_root, cone_name)
        cone_y = float(cone_include.findtext("pose").split()[1])

        assert abs(cone_y) >= 2.0


def test_levels_multi_items_launch_script_is_standalone_gazebo_with_levels_enabled():
    launch_text = (PROJECT_ROOT / "launch" / "levels_multi_items.sh").read_text(
        encoding="utf-8"
    )

    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim --levels" in launch_text
    assert "levels_multi_items.sdf" in launch_text
    assert "ros2" not in launch_text.lower()


def test_dem_terrain_model_uses_generated_dae_for_visual_and_collision():
    model_root = ET.parse(DEM_TERRAIN_ROOT / "model.sdf").getroot()
    visual_uri = model_root.findtext(".//visual/geometry/mesh/uri")
    collision_uri = model_root.findtext(".//collision/geometry/mesh/uri")
    visual_scale = model_root.findtext(".//visual/geometry/mesh/scale")
    collision_scale = model_root.findtext(".//collision/geometry/mesh/scale")

    assert DEM_DAE_PATH.is_file()
    assert model_root.findtext(".//model/static") == "true"
    assert visual_uri == DEM_MESH_URI
    assert collision_uri == DEM_MESH_URI
    assert visual_scale == "1 1 1"
    assert collision_scale == "1 1 1"


def test_dem_terrain_dae_has_matching_vertex_normals():
    mesh_root = ET.parse(DEM_DAE_PATH).getroot()
    namespace = {"dae": "http://www.collada.org/2005/11/COLLADASchema"}
    vertex_accessor = mesh_root.find(
        ".//dae:source[@id='terrain_positions']/dae:technique_common/dae:accessor",
        namespace,
    )
    normal_accessor = mesh_root.find(
        ".//dae:source[@id='terrain_normals']/dae:technique_common/dae:accessor",
        namespace,
    )
    normal_input = mesh_root.find(
        ".//dae:triangles/dae:input[@semantic='NORMAL']",
        namespace,
    )
    triangle_indices = mesh_root.findtext(".//dae:triangles/dae:p", namespaces=namespace)

    assert vertex_accessor is not None
    assert normal_accessor is not None
    assert normal_input is not None
    assert vertex_accessor.attrib["count"] == normal_accessor.attrib["count"]
    assert normal_input.attrib["offset"] == "1"
    assert len(triangle_indices.split()) % 6 == 0


def test_dem_terrain_world_and_launch_script_are_standalone_gazebo():
    world_root = ET.parse(PROJECT_ROOT / "worlds" / "dem_terrain.sdf").getroot()
    launch_text = (PROJECT_ROOT / "launch" / "dem_terrain.sh").read_text(
        encoding="utf-8"
    )
    include_uris = [
        include.findtext("uri")
        for include in world_root.findall(".//include")
    ]

    assert "model://dem_terrain" in include_uris
    assert "model://falling_box" in include_uris
    assert _include_pose_z(world_root, "model://falling_box") > (
        _include_pose_z(world_root, "model://dem_terrain") + 10.0
    )
    assert _include_pose_x(world_root, "model://dem_terrain") == -50.0
    assert "GZ_SIM_RESOURCE_PATH" in launch_text
    assert "gz sim" in launch_text
    assert "dem_terrain.sdf" in launch_text
    assert "ros2" not in launch_text.lower()


def test_readme_explains_dem_terrain_scale_and_pose():
    readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "data/dae/example_dem_100m.dae" in readme_text
    assert "<scale>x y z</scale>" in readme_text
    assert "<pose>x y z roll pitch yaw</pose>" in readme_text
    assert "-50 -50 0 0 0 0" in readme_text


@pytest.mark.parametrize(
    ("world_file", "terrain_uri", "extra_gz_args"),
    [
        ("basic_terrain.sdf", "model://ground_terrain", []),
        ("textured_terrain.sdf", "model://textured_terrain", []),
        ("multi_texture_terrain.sdf", "model://multi_texture_terrain", []),
        ("levels_terrain.sdf", "model://level_terrain_a", ["--levels"]),
    ],
)
def test_falling_box_collides_with_terrain_mesh_in_headless_gazebo(
    tmp_path,
    world_file,
    terrain_uri,
    extra_gz_args,
):
    if shutil.which("gz") is None:
        pytest.skip("Gazebo CLI `gz` is not available")

    serialized_map_pb2 = pytest.importorskip(
        "gz.msgs10.serialized_map_pb2",
        reason="Gazebo Python message bindings are not available",
    )

    record_path = tmp_path / "gazebo_state"
    env = os.environ.copy()
    env["GZ_SIM_RESOURCE_PATH"] = (
        f"{PROJECT_ROOT / 'models'}:{env['GZ_SIM_RESOURCE_PATH']}"
        if env.get("GZ_SIM_RESOURCE_PATH")
        else str(PROJECT_ROOT / "models")
    )

    result = subprocess.run(
        [
            "gz",
            "sim",
            "-s",
            "-r",
            *extra_gz_args,
            "--iterations",
            "2500",
            "--record-path",
            str(record_path),
            "--log-overwrite",
            str(PROJECT_ROOT / "worlds" / world_file),
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    z_samples = _moving_entity_z_samples(
        record_path / "state.tlog",
        serialized_map_pb2.SerializedStateMap,
    )
    world_root = ET.parse(PROJECT_ROOT / "worlds" / world_file).getroot()
    terrain_z = _include_pose_z(world_root, terrain_uri)
    falling_box_z = _include_pose_z(world_root, "model://falling_box")
    expected_landed_z = terrain_z + 0.5

    assert z_samples[0] >= falling_box_z - 0.1
    assert z_samples[-1] < z_samples[0] - 2.0
    assert abs(z_samples[-1] - expected_landed_z) < 0.1
    assert max(z_samples[-20:]) - min(z_samples[-20:]) < 0.01


def _include_pose_z(world_root, model_uri):
    for include in world_root.findall(".//include"):
        if include.findtext("uri") != model_uri:
            continue

        pose_text = include.findtext("pose", "0 0 0 0 0 0")
        return float(pose_text.split()[2])

    raise AssertionError(f"Missing include for {model_uri}")


def _include_pose_x(world_root, model_uri):
    for include in world_root.findall(".//include"):
        if include.findtext("uri") != model_uri:
            continue

        pose_text = include.findtext("pose", "0 0 0 0 0 0")
        return float(pose_text.split()[0])

    raise AssertionError(f"Missing include for {model_uri}")


def _include_by_name(world_root, include_name):
    for include in world_root.findall(".//include"):
        if include.findtext("name") == include_name:
            return include

    raise AssertionError(f"Missing include named {include_name}")


def _moving_entity_z_samples(state_log_path, serialized_state_map_cls):
    assert state_log_path.is_file()

    connection = sqlite3.connect(state_log_path)
    try:
        changed_state_topic_id = connection.execute(
            "select id from topics where name like ?",
            ("%/changed_state",),
        ).fetchone()
        assert changed_state_topic_id is not None

        samples_by_entity = {}
        for (message_blob,) in connection.execute(
            "select message from messages where topic_id = ? order by id",
            (changed_state_topic_id[0],),
        ):
            state_map = serialized_state_map_cls()
            state_map.ParseFromString(message_blob)

            for entity_id, entity_state in state_map.entities.items():
                for component in entity_state.components.values():
                    z_value = _z_from_pose_component(component.component)
                    if z_value is None:
                        continue
                    samples_by_entity.setdefault(entity_id, []).append(z_value)
    finally:
        connection.close()

    moving_entities = [
        samples
        for samples in samples_by_entity.values()
        if len(samples) > 20 and max(samples) - min(samples) > 1.0
    ]

    assert len(moving_entities) == 1
    return moving_entities[0]


def _z_from_pose_component(component_text):
    parts = component_text.split()
    if len(parts) != 6:
        return None

    try:
        return float(parts[2])
    except ValueError:
        return None
