from orcestra.meteor import get_meteor_track


def plot_meteor_latest_position(ax, **kwargs):
    meteor = get_meteor_track(deduplicate_latlon=True)
    meteor_latest = meteor.isel(time=-1)
    ax.scatter(meteor_latest["lon"], meteor_latest["lat"], **kwargs)


def plot_meteor_track(ax, **kwargs):
    meteor = get_meteor_track(deduplicate_latlon=True)
    ax.plot(meteor["lon"], meteor["lat"], **kwargs)