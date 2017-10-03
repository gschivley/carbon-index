import pandas as pd
from src.util.utils import getParentDir
from os.path import join, abspath, normpath, dirname, split

def fraction_state2nerc(df, state, region_col='NERC'):
    """Return the percent of gen & consumption by fuel type in each region
    for a state

    inputs:
        df (dataframe): a dataframe with data from the most recent EIA-923
            final release. It should either contain a column with reporting
            frequency ('A' or 'M' for annual/monthly), or only include annual
            facilities.

    What if I want to do something other than NERC regions? What is the
    appropriate column name?

    What sort of data is this function supposed to accept?
    - State of each facility
    - Reporting frequency
    - Year
    - NERC region (or other region code?)
    - plant id
    - fuel category
    - generation, total fuel, elec fuel

    output:
        result (df): The percent of generation, toal fuel, and electric fuel
            from annual reporting facilities in each (NERC) region from the
            state

    """
    # Not sure if I'll pass through all facilities or just annual.
    # Drop monthly if all facilities are passed through
    if 'reporting frequency' in df.columns:
        a = df.loc[(df.state == state) &
                         (df['reporting frequency'] == 'A')].copy()
    else:
        a = df.copy()

    # Group by region and fuel category
    a.drop(['plant id', 'year'], axis=1, inplace=True)
    a = a.groupby([region_col, 'fuel category']).sum()

    # Unique list of fuels
    fuels = set(a.index.get_level_values('fuel category'))

    # Loop through the fuels and create a df for each fuel. The main df has
    # a multi-index, so use .xs to take a cross-slice. Each new df will have
    # the percent of generation, total fuel, and elec fuel in each region.
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
    keep_cols = (['state', region_col, 'fuel category']
                 + list(rename_cols.values()))
    result = result.loc[:, keep_cols]

    return result

def add_nerc(df, regions):
    """
    Add the NERC (or other) region as a column based on lat/lon data in a
    dataframe

    inputs:
        df (dataframe): Should have 'lat' and 'lon' columns
        regions (dataframe): a geopandas df with region shapes

    outputs:
        df (dataframe): modified version of the original dataframe with region
            column

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
    # nerc_path = join(top_path, 'Data storage', 'NERC_Regions_EIA',
    #             'NercRegions_201610.shp')
    # regions = gpd.read_file(nerc_path)

    # Spatial join of the facilities with the NERC regions
    facility_nerc = gpd.sjoin(geo_df, regions, how='inner', op='within')

    # Merge the NERC labels back into the main dataframe
    cols = ['plant id', 'year', 'NERC']
    df = df.merge(facility_nerc.loc[:, cols],
                  on=['plant id', 'year'], how='left')

    return df
