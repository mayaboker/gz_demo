from pathlib import Path

from osgeo import gdal
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DEM_PATH = PROJECT_ROOT / "data" / "dem" / "example_dem_100m.tif"
DEFAULT_DAE_PATH = PROJECT_ROOT / "data" / "dae" / "example_dem_100m.dae"


def dem_to_dae(
    dem_path=DEFAULT_DEM_PATH,
    dae_path=DEFAULT_DAE_PATH,
    step=1,
    z_scale=1.0
):
    dem_path = Path(dem_path)
    dae_path = Path(dae_path)
    dae_path.parent.mkdir(parents=True, exist_ok=True)

    ds = gdal.Open(str(dem_path))
    if ds is None:
        raise RuntimeError(f"Could not open DEM: {dem_path}")

    band = ds.GetRasterBand(1)
    dem = band.ReadAsArray().astype(float)

    nodata = band.GetNoDataValue()
    gt = ds.GetGeoTransform()

    # Downsample for smaller mesh
    dem = dem[::step, ::step]
    rows, cols = dem.shape

    vertices = []
    vertex_index = {}
    faces = []

    for r in range(rows):
        for c in range(cols):
            z = dem[r, c]

            if nodata is not None and z == nodata:
                continue
            if np.isnan(z):
                continue

            # Convert raster pixel to map/world coordinates
            x = gt[0] + (c * step) * gt[1] + (r * step) * gt[2]
            y = gt[3] + (c * step) * gt[4] + (r * step) * gt[5]
            z = z * z_scale

            vertex_index[(r, c)] = len(vertices)
            vertices.append((x, y, z))

    # Create two triangles per grid cell
    for r in range(rows - 1):
        for c in range(cols - 1):
            keys = [
                (r, c),
                (r, c + 1),
                (r + 1, c),
                (r + 1, c + 1)
            ]

            if all(k in vertex_index for k in keys):
                v00 = vertex_index[(r, c)]
                v10 = vertex_index[(r, c + 1)]
                v01 = vertex_index[(r + 1, c)]
                v11 = vertex_index[(r + 1, c + 1)]

                faces.append((v00, v10, v11))
                faces.append((v00, v11, v01))

    normals = compute_vertex_normals(vertices, faces)
    write_dae(dae_path, vertices, normals, faces)


def compute_vertex_normals(vertices, faces):
    normals = np.zeros((len(vertices), 3), dtype=float)

    for a, b, c in faces:
        v0 = np.array(vertices[a], dtype=float)
        v1 = np.array(vertices[b], dtype=float)
        v2 = np.array(vertices[c], dtype=float)
        face_normal = np.cross(v1 - v0, v2 - v0)

        if face_normal[2] < 0:
            face_normal = -face_normal

        length = np.linalg.norm(face_normal)
        if length == 0:
            continue

        face_normal /= length
        normals[a] += face_normal
        normals[b] += face_normal
        normals[c] += face_normal

    for index, normal in enumerate(normals):
        length = np.linalg.norm(normal)
        normals[index] = normal / length if length else [0.0, 0.0, 1.0]

    return [tuple(normal) for normal in normals]


def write_dae(path, vertices, normals, faces):
    path = Path(path)
    positions = " ".join(
        f"{x} {y} {z}" for x, y, z in vertices
    )

    normal_values = " ".join(
        f"{x} {y} {z}" for x, y, z in normals
    )

    face_indices = " ".join(
        f"{a} {a} {b} {b} {c} {c}" for a, b, c in faces
    )

    dae = f"""<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset>
    <unit name="meter" meter="1"/>
    <up_axis>Z_UP</up_axis>
  </asset>

  <library_geometries>
    <geometry id="terrain_mesh" name="terrain_mesh">
      <mesh>
        <source id="terrain_positions">
          <float_array id="terrain_positions_array" count="{len(vertices) * 3}">
            {positions}
          </float_array>
          <technique_common>
            <accessor source="#terrain_positions_array" count="{len(vertices)}" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>

        <source id="terrain_normals">
          <float_array id="terrain_normals_array" count="{len(normals) * 3}">
            {normal_values}
          </float_array>
          <technique_common>
            <accessor source="#terrain_normals_array" count="{len(normals)}" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>

        <vertices id="terrain_vertices">
          <input semantic="POSITION" source="#terrain_positions"/>
        </vertices>

        <triangles count="{len(faces)}">
          <input semantic="VERTEX" source="#terrain_vertices" offset="0"/>
          <input semantic="NORMAL" source="#terrain_normals" offset="1"/>
          <p>{face_indices}</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>

  <library_visual_scenes>
    <visual_scene id="Scene" name="Scene">
      <node id="terrain" name="terrain">
        <instance_geometry url="#terrain_mesh"/>
      </node>
    </visual_scene>
  </library_visual_scenes>

  <scene>
    <instance_visual_scene url="#Scene"/>
  </scene>
</COLLADA>
"""

    with path.open("w", encoding="utf-8") as f:
        f.write(dae)


if __name__ == "__main__":
    dem_to_dae(
        step=4,       # increase for smaller mesh
        z_scale=1.0   # change if elevation needs scaling
    )
