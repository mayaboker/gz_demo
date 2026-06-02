from pathlib import Path
import shutil

from osgeo import gdal, osr
import numpy as np

from dem2dae import compute_vertex_normals, write_dae


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DEM = PROJECT_ROOT / "data" / "dem" / "example_dem_100m.tif"
DEM_OUTPUT_DIR = PROJECT_ROOT / "data" / "dem"
DAE_OUTPUT_DIR = PROJECT_ROOT / "data" / "dae"

QUARTERS = {
    "nw": (0, 51, 0, 51),
    "ne": (0, 51, 50, 101),
    "sw": (50, 101, 0, 51),
    "se": (50, 101, 50, 101),
}
QUARTER_MODELS = {
    "nw": "dem_level_desert",
    "ne": "dem_level_soil",
    "sw": "dem_level_rocks",
    "se": "dem_level_water",
}


def main():
    DEM_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DAE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ds = gdal.Open(str(SOURCE_DEM))
    if ds is None:
        raise RuntimeError(f"Could not open DEM: {SOURCE_DEM}")

    band = ds.GetRasterBand(1)
    dem = band.ReadAsArray().astype(float)
    nodata = band.GetNoDataValue()
    gt = ds.GetGeoTransform()
    projection = ds.GetProjection()

    valid = dem[~np.isnan(dem)]
    if nodata is not None:
        valid = valid[valid != nodata]
    dem = dem - valid.min()

    for name, (row_start, row_end, col_start, col_end) in QUARTERS.items():
        quarter = dem[row_start:row_end, col_start:col_end]
        tif_path = DEM_OUTPUT_DIR / f"example_dem_100m_{name}.tif"
        dae_path = DAE_OUTPUT_DIR / f"example_dem_100m_{name}.dae"

        write_quarter_tif(
            tif_path,
            quarter,
            gt,
            projection,
            row_start,
            col_start,
            nodata,
        )
        write_quarter_dae(dae_path, quarter, gt, nodata)
        model_mesh_path = (
            PROJECT_ROOT
            / "models"
            / QUARTER_MODELS[name]
            / "meshes"
            / dae_path.name
        )
        model_mesh_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dae_path, model_mesh_path)
        print(dae_path)


def write_quarter_tif(path, dem, source_gt, projection, row_start, col_start, nodata):
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = dem.shape
    ds = driver.Create(str(path), cols, rows, 1, gdal.GDT_Float32)

    ds.SetGeoTransform(
        (
            source_gt[0] + col_start * source_gt[1],
            source_gt[1],
            source_gt[2],
            source_gt[3] + row_start * source_gt[5],
            source_gt[4],
            source_gt[5],
        )
    )
    if projection:
        ds.SetProjection(projection)
    else:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(3857)
        ds.SetProjection(srs.ExportToWkt())

    band = ds.GetRasterBand(1)
    band.WriteArray(dem.astype(np.float32))
    if nodata is not None:
        band.SetNoDataValue(nodata)
    band.FlushCache()
    ds = None


def write_quarter_dae(path, dem, source_gt, nodata):
    rows, cols = dem.shape
    pixel_x = abs(source_gt[1])
    pixel_y = abs(source_gt[5])
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

            vertex_index[(r, c)] = len(vertices)
            vertices.append((c * pixel_x, (rows - 1 - r) * pixel_y, z))

    for r in range(rows - 1):
        for c in range(cols - 1):
            keys = [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
            if not all(key in vertex_index for key in keys):
                continue

            v00 = vertex_index[(r, c)]
            v10 = vertex_index[(r, c + 1)]
            v01 = vertex_index[(r + 1, c)]
            v11 = vertex_index[(r + 1, c + 1)]
            faces.append((v00, v11, v10))
            faces.append((v00, v01, v11))

    normals = compute_vertex_normals(vertices, faces)
    write_dae(path, vertices, normals, faces)


if __name__ == "__main__":
    main()
