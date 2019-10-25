"""
Determine the region (currently NERC region) that each power plant is part of
for every year of calculations

"""

from src.params import DATA_PATHS, DATA_DATE, LAST_ANNUAL_923_YEAR, EIA_860_NERC_INFO
from src.util import download_unzip, download_save

import pandas as pd
# from sklearn import neighbors, metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from collections import Counter
from copy import deepcopy


def load_plants():
    """
    Load information about each plant that we have generation data for. Includes
    plant id, year, lat, lon, and state. Because we don't have facility information
    for every facility operating in

    Returns
    -------
    DataFrame

    """

    from src.analysis.load_transformed_data import load_facility_gen_fuel_data
    FACILITY_DF = load_facility_gen_fuel_data()
    plants = FACILITY_DF.loc[:, ['plant id', 'year', 'lat', 'lon', 'state']]

    # Because the most recent year facility dataframe only includes annually reporting
    # facilities I'm going to duplicate the plant id, lat/lon, and state information
    # from the last year will full data (LAST_ANNUAL_923_YEAR).

    all_years = plants['year'].unique()

    df_list = []
    last_full_year_plants = plants.loc[plants.year == LAST_ANNUAL_923_YEAR, :].copy()
    for year in all_years:
        if year > LAST_ANNUAL_923_YEAR:
            copy_plants = last_full_year_plants.copy()
            copy_plants['year'] = year
            df_list.append(copy_plants)

    copy_years = pd.concat(df_list)

    plants = pd.concat([plants.loc[plants.year <= LAST_ANNUAL_923_YEAR, :], copy_years])

    return plants


def extract_860_nerc_labels(year):

    if year <= 2012:
        params = {
            'io': DATA_PATHS['eia860'] / 'eia8602012' / 'PlantY2012.xlsx',
            'skiprows': 0,
            'usecols': 'B,J'
        }
        data_year = 2012
    else:
        params = {
            'io': DATA_PATHS['eia860'] / f'eia860{year}' / f'2___Plant_Y{year}.xlsx',
            'skiprows': 0,
            'usecols': 'C,L'
        }
        data_year = year

    if not params['io'].exists():
        save_path = params['io'].parent
        try:
            url = (
                'https://www.eia.gov/electricity/data/eia860/'
                + f'archive/xls/eia860{data_year}.zip'
            )
            download_unzip(url, save_path)
        except ValueError:
            url = (
                'https://www.eia.gov/electricity/data/eia860/'
                + f'xls/eia860{data_year}.zip'
            )
            download_unzip(url, save_path)

    eia_nercs = pd.read_excel(**params)
    eia_nercs.columns = ['plant id', 'nerc']
    eia_nercs['year'] = year

    return eia_nercs


def label_new_spp_ercot(filename=None):
    """
    Download and save an EIA860 monthly generator excel file. Can either be the
    most recent month available or a specific month.

    Parameters
    ----------
    filename : str, optional
        the excel filename to download, in format <month>_generator<year>.xlsx
        (the default is None, in which case the most recent file is determined
        from the 860m website)

    """
    base_url = 'https://www.eia.gov/electricity/data/eia860m/'

    if not filename:

        # Scrape the 860m website and find the newest monthly file
        table = pd.read_html(base_url, header=0, flavor='lxml')[0]
        month, year = table['EIA 860M'][0].split()  # 'Month year' as a string
        month = month.lower()
        filename = '{}_generator{}.xlsx'.format(month, year)

    url = base_url + f'xls/{filename}'
    save_path = DATA_PATHS['eia860m'] / filename
    if not save_path.exists():
        download_save(url=url, save_path=save_path)

    _m860 = pd.read_excel(save_path, sheet_name='Operating', skipfooter=1,
                          usecols='C,F,P,AE', skiprows=1)
    _m860.columns = _m860.columns.str.lower()

    m860 = _m860.loc[(_m860['operating year'] > LAST_ANNUAL_923_YEAR)].copy()

    m860.loc[(m860['plant state'].isin(['TX', 'OK'])) &
             (m860['balancing authority code'] == 'SWPP'), 'nerc'] = 'SPP'

    m860.loc[(m860['plant state'].isin(['TX'])) &
             (m860['balancing authority code'] == 'ERCO'), 'nerc'] = 'TRE'

    m860.dropna(inplace=True)
    m860.reset_index(inplace=True, drop=True)

    m860 = m860[['plant id', 'nerc', 'operating year']]
    m860.columns = ['plant id', 'nerc', 'year']
    m860.drop_duplicates(inplace=True)

    return m860


def add_new_spp_tre_labels(nercs):

    new_spp_ercot = label_new_spp_ercot()

    nercs = pd.concat([nercs, new_spp_ercot])

    return nercs


def extract_nerc_labels_all_years(start=2012, end=LAST_ANNUAL_923_YEAR + 1):

    nercs = pd.concat(
        extract_860_nerc_labels(year) for year in range(start, end)
    )

    nercs_plus_spp_tre = add_new_spp_tre_labels(nercs)

    return nercs_plus_spp_tre


def split_training_unknown(training, plants):
    "Separate records that have a valid NERC label from those that don't"

    all_features = pd.merge(training, plants, on=['plant id', 'year'], how='inner')
    # le = LabelEncoder()
    # all_features.loc[:, 'enc_state'] = le.fit_transform(
    #     all_features.loc[:, 'state'].tolist()
    # )

    training = all_features.dropna()
    unknown = all_features.loc[all_features['nerc'].isnull(), :]

    unknown_latlon = unknown.loc[
        ~(unknown[['lat', 'lon']].isnull().any(axis=1)), :
    ]

    unknown_state = unknown.loc[
        (unknown[['lat', 'lon']].isnull().any(axis=1))
        & ~(unknown['state'].isnull()), :
    ]

    return training, unknown_latlon, unknown_state


def classify_rf(training, feature_cols, unknown, n_iter=10, verbose=1):
    "Generic RF classification using provided feature columns"

    X = training.loc[:, feature_cols]
    y = training.loc[:, 'nerc']

    rf = RandomForestClassifier()
    params = dict(
        n_estimators=range(10, 40),  # [10, 15, 20, 25, 50],
        min_samples_split=range(2, 11),  # [2, 5, 10],
        min_samples_leaf=range(1, 6)  # [1, 3, 5],
    )

    clf_rf = RandomizedSearchCV(
        rf, params, n_iter=n_iter, cv=3, n_jobs=-1, iid=False, verbose=verbose
    )
    clf_rf.fit(X[feature_cols], y)

    unknown.loc[:, 'nerc'] = clf_rf.predict(unknown[feature_cols])

    return unknown


def classify_latlon(training, unknown_latlon):
    "Classify plants with lat/lon and year"

    labeled_latlon = classify_rf(
        training,
        feature_cols=['lat', 'lon', 'year'],
        unknown=unknown_latlon
    )

    return labeled_latlon


def classify_state(training, unknown_state):
    "Classify plants without lat/lon, using on the state and year and features"

    if unknown_state.empty:
        n_iter = 1
    else:
        n_iter = 10

    labeled_state = classify_rf(
        training,
        feature_cols=['enc_state', 'year'],
        unknown=unknown_state,
        n_iter=n_iter
    )

    return labeled_state


def label_unknown_regions():

    training = extract_nerc_labels_all_years()
    plants = load_plants()

    training, unknown_latlon, unknown_state = split_training_unknown(training, plants)

    labeled_latlon = classify_latlon(training, unknown_latlon)
    # labeled_state = classify_state(training, unknown_state)

    labeled = pd.concat(
        [
            training.loc[training.notnull().all(axis=1)],
            labeled_latlon,
            # labeled_state.loc[:, ['plant id', 'nerc', 'state', 'year']]
        ]
    )

    return labeled


def write_region_labels():

    labeled = label_unknown_regions()
    path = DATA_PATHS["transformed_data"] / 'facility_labels'
    path.mkdir(parents=True, exist_ok=True)
    labeled.to_csv(path / 'Facility locations_RF.csv', index=False)


if __name__ == "__main__":
    write_region_labels()
