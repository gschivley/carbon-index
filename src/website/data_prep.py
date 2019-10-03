import pandas as pd
import numpy as np
from datetime import datetime
import csv

from src.params import DATA_PATHS, QUARTER_YEAR, FINAL_DATA_YEAR, DATA_DATE


def index_hovertext(row, units='kg/mwh'):
    """
    Helper function to create index hovertext strings. Use with df.apply
    inputs:
        row: row of a dataframe
        units (string): either kg/mwh or lb/mwh
    """
    # dataframe column uses g/kWh, website uses kg/mwh
    if units == 'kg/mwh':
        df_units = 'g/kwh'
        units = 'kg/MWh' # need to make MW uppercase
    else:
        df_units = units
        units = 'lb/MWh' # need to make MW uppercase
    index_col = 'index ({})'.format(df_units)

    # want to use kg for website
    # kg_units = 'kg/MWh'

    index = row[index_col]
    change = row['change since 2005']

    if change >= 0:
        output = u'{:,.0f} {} <br>\u2191 {:.1%} from 2005'.format(index,
                                                                  units,
                                                                  change)
    else:
        output = u'{:,.0f} {} <br>\u2193 {:.1%} from 2005'.format(index,
                                                                  units,
                                                                  abs(change))
    return output


def emissions_hovertext(row):
    """
    Helper function to create total co2 emissions hovertextself.
    """
    emissions = row['final co2 (million mt)']

    output = u'{:,.0f} Million<br>Metric Tonnes'.format(emissions)

    return output


def gen_hovertext(row):
    """
    Helper function to create generation hovertext strings. Use with df.apply.
    """
    gen = row['generation (mwh)']
    if row['fuel category'] == 'Total':
        output = '{:,} Million MWh'.format(int(gen / 1e6))
    else:
        index = row['adjusted index (lb/mwh)']
        output = '{:,} Million MWh<br>{:,} lb/MWh'.format(int(gen / 1e6),
                                                          int(index))
    return output


def index_csv(path_in, time_unit, path_out):
    """
    Read in a csv with index data, export a new csv with hovertext and only
    information needed for the website figure
    inputs:
        path_in (string): path for csv import
        time_unit (string): one of "monthly", "quarterly", or "annual"
        path_out (string): output path for the csv
    """
    if time_unit not in ['monthly', 'quarterly', 'annual']:
        raise ValueError('{} is not a valid time option'.format(time_unit))

    dtypes = {'monthly': {'month': 'int',
                          'year': 'int'},
              'quarterly': {'quarter': 'int',
                            'year': 'int'},
              'annual': {'year': 'int'}}

    df = pd.read_csv(path_in, dtype=dtypes[time_unit])

    # Don't include current year in annual data because it won't be complete
    if time_unit == 'annual':
        curr_year = datetime.today().year
        df = df.loc[df['year'] < curr_year]

    # Get the date portion of datetime as a string
    if time_unit == 'monthly':
        # Split datetime into a list then take first element from the list
        #http://pandas.pydata.org/pandas-docs/stable/text.html#splitting-and-replacing-strings
        df['date'] = df.loc[:, 'datetime'].str.split().str[0]

    always_export = ['index (g/kwh)', 'index (lb/mwh)',
                     'final co2 (million mt)',
                     'Imperial hovertext', 'SI hovertext','Emissions hovertext',
                     'year']

    time_unit_cols = {'monthly': ['date'],# ['month'],
                   'quarterly': ['quarter', 'year_quarter'],
                   'annual': []}

    # Convert CO2 from kg to billion metric tons and create hovertext
    df['final co2 (million mt)'] = df['final co2 (kg)'] / 1e9
    df['Emissions hovertext'] = df.apply(lambda row: emissions_hovertext(row),
                                         axis=1)

    # Add hovertext to dataframe
    df['Imperial hovertext'] = df.apply(lambda row: index_hovertext(row,
                                                                    'lb/mwh'),
                                        axis=1)
    df['SI hovertext'] = df.apply(lambda row: index_hovertext(row, 'kg/mwh'),
                                  axis=1)

    # Export dataframe
    cols = always_export + time_unit_cols[time_unit]
    df[cols].to_csv(path_out, index=False, quoting=csv.QUOTE_NONNUMERIC,
                    encoding='utf-8')
    # return df


def gen_csv(path_in, time_unit, path_out):
    """
    Read in a csv with generation data, export a new csv with hovertext and
    only information needed for the website figure
    inputs:
        path_in (string): path for csv import
        time_unit (string): one of "monthly", "quarterly", or "annual"
        path_out (string): output path for the csv
    """
    if time_unit not in ['monthly', 'quarterly', 'annual']:
        raise ValueError('{} is not a valid time option'.format(time_unit))

    always_export = ['fuel category', 'generation (M MWh)', 'hovertext']
    time_unit_cols = {'monthly': ['date'],
                   'quarterly': ['year_quarter'],
                   'annual': ['year']}

    dtypes = {'monthly': {'month': 'int',
                          'year': 'int'},
              'quarterly': {'quarter': 'int',
                            'year': 'int'},
              'annual': {'year': 'int'}}

    df = pd.read_csv(path_in, dtype=dtypes[time_unit])

    # Don't include current year in annual data because it won't be complete
    if time_unit == 'annual':
        curr_year = datetime.today().year
        df = df.loc[df['year'] < curr_year]

    # Get the date portion of datetime as a string
    if time_unit == 'monthly':
        # Split datetime into a list then take first element from the list
        #http://pandas.pydata.org/pandas-docs/stable/text.html#splitting-and-replacing-strings
        df['date'] = df.loc[:, 'datetime'].str.split().str[0]

    # If I haven't modified the file to include a "Total" category...
    if 'Total' not in df['fuel category'].unique():
        group_cols = time_unit_cols[time_unit]
        total_gen = df.groupby(group_cols).sum().reset_index()
        total_gen[['adjusted index (lb/mwh)', 'adjusted index (g/kwh)']] = np.nan
        total_gen['fuel category'] = 'Total'
        df = pd.concat([df, total_gen])

    for fuel in df['fuel category'].unique():
        df.loc[df['fuel category'] == fuel,
               'hovertext'] = (df.loc[df['fuel category'] == fuel]
                                 .apply(gen_hovertext, axis=1))

    # Convert mwh to Million mwh for figure
    df['generation (M MWh)'] = df.loc[:, 'generation (mwh)'] / 1e6

    cols = always_export + time_unit_cols[time_unit]
    df[cols].to_csv(path_out, index=False, quoting=csv.QUOTE_NONNUMERIC)

def _remove_partial_years(df):

    years = df.year.unique()
    keep_years = []
    for y in years:
        months = df.loc[df.year == y, 'month'].unique()
        if 12 in months:
            keep_years.append(y)

    df = df.loc[df.year.isin(keep_years), :]


def annual_index_timeseries_csv(path_in, path_out, region_type, only_final_year=False):

    df = pd.read_csv(path_in)
    _remove_partial_years(df)
    data_cols = [
        'final co2 (kg)',
        'generation (mwh)',
    ]
    df_annual = df.groupby(['year', region_type], as_index=False)[data_cols].sum()
    df_annual['index'] = df_annual['final co2 (kg)'] / df_annual['generation (mwh)']
    df_annual['indexlb'] = df_annual['index'] * 2.2046

    if only_final_year:
        final_year = df_annual.year.max()
        df_annual = df_annual.loc[df_annual.year == final_year, :]

    df_annual.to_csv(path_out, index=False)


def annual_index_single_json(path_in, path_out, region_type):

    df = pd.read_csv(path_in)
    _remove_partial_years(df)
    max_year = df['year'].max()

    data_cols = [
        'final co2 (kg)',
        'generation (mwh)',
    ]
    df_annual = df.groupby(['year', region_type], as_index=False)[data_cols].sum()
    df_annual['value'] = (
        (df_annual['final co2 (kg)'] / df_annual['generation (mwh)']).astype(int)
    )
    df_annual = df_annual.query('year == @max_year')

    cols = ['value', 'nerc']
    df_annual[cols].to_json(path_out, orient='records')


# def nerc_annual_year(path_in, path_out):

#     df = pd.read_csv(path_in)

#     data_cols = [
#         'final co2 (kg)',
#         'generation (mwh)',
#     ]
#     df_annual = df.groupby(['year', 'nerc'])[data_cols].sum()
#     df_annual['index'] = df_annual['final co2 (kg)'] / df_annual['generation (mwh)']


def make_web_files():
    for time in ['Annual', 'Quarterly', 'Monthly']:
        # path = join(cwd, '{} generation 2017 Q4.csv'.format(time))
        path = DATA_PATHS['results'] / f'{time} generation {QUARTER_YEAR}.csv'
        lower = time.lower()
        # out = join(cwd, 'website csv', '{}_gen_website.csv'.format(lower))
        out = DATA_PATHS['web_files'] / f'{lower}_gen_website.csv'

        gen_csv(path, lower, out)

    for time in ['Annual', 'Quarterly', 'Monthly']:
        # path = join(cwd, '{} index 2017 Q4.csv'.format(time))
        path = DATA_PATHS['results'] / f'{time} index {QUARTER_YEAR}.csv'
        lower = time.lower()
        # out = join(cwd, 'website csv', '{}_index_website.csv'.format(lower))
        out = DATA_PATHS['web_files'] / f'{lower}_index_website.csv'

        index_csv(path, lower, out)

    state_path_in = DATA_PATHS['results'] / f'state_index_{DATA_DATE}.csv'
    state_path_out = (
        DATA_PATHS['web_files']
        / 'state_index_map_website.csv'
    )
    nerc_path_in = (
        DATA_PATHS['results']
        / f'NERC gen emissions and index {DATA_DATE}.csv'
    )
    nerc_path_out = (
        DATA_PATHS['web_files'] / 'NERCemissions.json'
    )

    annual_index_timeseries_csv(
        path_in=state_path_in,
        path_out=state_path_out,
        region_type='state'
    )

    # annual_index_single_json(
    #     path_in=nerc_path_in,
    #     path_out=nerc_path_out,
    #     region_type='nerc'
    # )
