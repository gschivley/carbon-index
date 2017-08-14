import pandas as pd
from src.util.utils import getParentDir
from os.path import join, abspath, normpath, dirname, split

def annual(df, state):
    """Return the percent of gen & consumption by fuel type in each NERC region
    for a state"""

    if 'reporting frequency' in df.columns:
        a = df.loc[(df.state == state) &
                         (df['reporting frequency'] == 'A')].copy()
    else:
        a = df.copy()
    a.drop(['plant id', 'year'], axis=1, inplace=True)
    a = a.groupby(['NERC', 'fuel category']).sum()

    fuels = set(a.index.get_level_values('fuel category'))

    temp_list = []
    for fuel in fuels:
        temp = (a.xs(fuel, level='fuel category')
                / a.xs(fuel, level='fuel category').sum())
        temp['fuel category'] = fuel
        temp_list.append(temp)

    result = pd.concat(temp_list)
    result.reset_index(inplace=True)
    result['state'] = state

    rename_cols = {'generation (MWh)': '% generation',
                   'total fuel (mmbtu)': '% total fuel',
                   'elec fuel (mmbtu)': '% elec fuel'}

    result.rename(columns=rename_cols, inplace=True)
    keep_cols = ['state', 'NERC', 'fuel category'] + list(rename_cols.values())
    result = result.loc[:, keep_cols]

    return result

def add_nerc(df):
    """
    Add the NERC region as a column based on lat/lon data in a dataframe

    """
    import geopandas as gpd
    from shapely.geometry import Point
    from geopandas import GeoDataFrame

    ap = abspath(__file__)
    top_path = getParentDir(dirname(ap), level=2)

    # Only do a spatial join on points when necessary
    cols = ['lat', 'lon', 'plant id', 'year']
    small_facility = df.loc[:, cols].drop_duplicates()
    geometry = [Point(xy) for xy in zip(small_facility.lon, small_facility.lat)]
    crs = {'init': 'epsg:4326'}
    geo_df = GeoDataFrame(small_facility, crs=crs, geometry=geometry)

    # Read NERC shapefile
    nerc_path = join(top_path, 'Data storage', 'NERC_Regions_EIA',
                'NercRegions_201610.shp')
    regions = gpd.read_file(nerc_path)

    # Spatial join of the facilities with the NERC regions
    facility_nerc = gpd.sjoin(geo_df, regions, how='inner', op='within')

    # Merge the NERC labels back into the main dataframe
    cols = ['plant id', 'year', 'NERC']
    df = df.merge(facility_nerc.loc[:, cols],
                  on=['plant id', 'year'], how='left')

    return df
