import healpy as hp
import matplotlib.pyplot as plt
import numpy as np

def make_skymap(center_lon, center_lat, sigma_deg):
    nside = 256  # Resolution parameter (must be a power of 2)
    npix = hp.nside2npix(nside)
    sigma_rad = np.radians(sigma_deg)
    
    # 2. Convert center coordinates to a 3D unit vector
    # healpy expects theta (colatitude from north pole: 0 to pi) and phi (longitude: 0 to 2pi) in radians
    center_theta = np.radians(90.0 - center_lat)
    center_phi = np.radians(center_lon)
    vec_center = hp.ang2vec(center_theta, center_phi)
    
    # 3. Get 3D unit vectors for all pixels in the HEALPix map
    pix_indices = np.arange(npix)
    vec_pixels = hp.pix2vec(nside, pix_indices)
    
    # 4. Calculate angular separation between each pixel and the center
    # Dot product of normalized 3D vectors gives cos(angular_separation)
    cos_theta = np.dot(vec_center, vec_pixels)
    cos_theta = np.clip( cos_theta, -1.0, 1.0)  # Avoid precision issues outside [-1, 1]
    angular_separation = np.arccos(cos_theta)  # in radians
    
    # 5. Evaluate the 2D Gaussian function based on angular distance
    # G(theta) = exp( - theta^2 / (2 * sigma^2) )
    healpix_map = np.exp(-(angular_separation**2) / (2 * sigma_rad**2))

    return healpix_map


if __name__ == "__main__":
    sm = make_skymap(100, 45, 5)
    filename = 'my_map.fits'
    hp.write_map(filename, sm, overwrite=True)
