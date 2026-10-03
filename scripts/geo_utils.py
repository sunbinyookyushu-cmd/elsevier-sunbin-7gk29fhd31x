"""Shared geo helpers: haversine great-circle distance (km / statute miles)."""
import numpy as np
R_KM = 6371.0088
def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (np.asarray(lat1,float), np.asarray(lon1,float), np.asarray(lat2,float), np.asarray(lon2,float)))
    a = np.sin((lat2-lat1)/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin((lon2-lon1)/2)**2
    return 2*R_KM*np.arcsin(np.sqrt(a))
def km_to_miles(km): return np.asarray(km,float)/1.609344
