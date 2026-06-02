from pathlib import Path

from osgeo import gdal, osr
import numpy as np

# Create a simple 100m x 100m DEM at 1m resolution
size = 101
x = np.linspace(-1, 1, size)
y = np.linspace(-1, 1, size)
X, Y = np.meshgrid(x, y)

# Small hill in the middle
dem = 10 * np.exp(-(X**2 + Y**2) * 4)

project_root = Path(__file__).resolve().parents[1]
output_dir = project_root / "data" / "dem"
output_dir.mkdir(parents=True, exist_ok=True)
outfile = output_dir / "example_dem_100m.tif"

driver = gdal.GetDriverByName("GTiff")
ds = driver.Create(str(outfile), size, size, 1, gdal.GDT_Float32)

# 1 m pixels, arbitrary origin
ds.SetGeoTransform((0, 1, 0, 100, 0, -1))

srs = osr.SpatialReference()
srs.ImportFromEPSG(3857)
ds.SetProjection(srs.ExportToWkt())

band = ds.GetRasterBand(1)
band.WriteArray(dem.astype(np.float32))
band.SetNoDataValue(-9999)
band.FlushCache()

ds = None

print(outfile)
