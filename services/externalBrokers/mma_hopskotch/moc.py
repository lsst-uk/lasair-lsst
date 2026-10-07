import healpy as hp
import numpy as np
from mocpy import MOC
import math

# Makes a MOC from a single-level (Icecube) type healpix file
def moc_single_level(contour, input_file, output_file, logger):
    map_data, header = hp.read_map(input_file, h=True, dtype=None)
    header_dict = dict(header)

    # Determine grid properties
    nside = hp.npix2nside(len(map_data))
    order = hp.nside2order(nside)
    ordering = header_dict.get('ORDERING', 'RING').strip().upper()

    msg = f"moc_single_level: NSIDE = {nside} (Order {order}), Ordering = {ordering}"
    if logger: logger.info(msg)
    else:      print(msg)

    prob = map_data / map_data.sum()
    order_idx = np.argsort(prob)[::-1]
    cum = np.cumsum(prob[order_idx])

    credible = np.empty_like(prob)
    credible[order_idx] = cum
    top_pixels = np.where(credible <= contour / 100.0)[0]

    if ordering == 'RING':
        nested_pixels = hp.ring2nest(nside, top_pixels)
    else:
        nested_pixels = top_pixels

    moc = MOC.from_healpix_cells(
        ipix=nested_pixels,
        depth=order,
        max_depth=order
    )
    moc.save(output_file, format='fits', overwrite=True)
    ALL_SKY = 180*180*4/math.pi
    area =  moc.sky_fraction * ALL_SKY
    msg = f"moc_single_level: area {area} saved to {output_file}"
    if logger: logger.info(msg)
    else:      print(msg)

    return area

