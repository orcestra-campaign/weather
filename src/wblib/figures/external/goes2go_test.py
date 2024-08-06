from goes2go import GOES
from goes2go.data import goes_nearesttime
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr
import orcestra.sat

time_sat = "2023-02-04T09:30:00.000000000" 
g = goes_nearesttime(time_sat, satellite=16, product="ABI", domain = "F")

dpi = 100
rgb_products = [i for i in dir(g.rgb) if i[0].isupper()]


track = orcestra.sat.SattrackLoader("EARTHCARE", "2024-07-22").get_track_for_day("2024-08-10")

projection = ccrs.PlateCarree()

fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=projection)
ax.set_global()
ax.coastlines()

goes_kwargs = g.rgb.imshow_kwargs

ax.imshow(g.rgb.NaturalColor(gamma=1.2), transform = g.rgb.crs, regrid_shape=3500, interpolation='nearest') 
ax.plot(track.lon, track.lat, color = 'red', linewidth = 3)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha = 0.25)
ax.set_extent([-50, 0, -10, 10])

fig.savefig('/Users/lucaschmidt/Documents/Code/Orcestra/weather/test.png', dpi=dpi)