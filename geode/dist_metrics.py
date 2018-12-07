import numpy as np

R_EARTH = 6367000

# accepts 2 arrays of lat lon pairs, use with scipy cdist
def haversine(u, v, r=R_EARTH):
    u = np.radians(u)
    v = np.radians(v)

    d = np.sin((u - v) / 2) ** 2

    h = d[0] + np.cos(u[0]) * np.cos(v[0]) * d[1]

    return 2 * r * np.arcsin( np.sqrt(h) )

def gc_manhattan(u, v, r=R_EARTH):
    half_lat = (u[0] + v[0]) / 2
    return haversine(
        u,
        np.array([v[0], u[1]])
    ) + haversine(
        np.array([half_lat, u[1]]),
        np.array([half_lat, v[1]])
    )

PRECISION_THRESHOLD = [
    2_496_000,
    1_248_000,
    642_000,
    321_000
]
