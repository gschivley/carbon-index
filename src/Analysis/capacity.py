import pandas as pd
import os
import calendar
from joblib import Parallel, delayed
idx = pd.IndexSlice

def month_hours(year, month):
    'Look up the number of hours in a given month'

    # second value in tuple is number of days in a month
    days = calendar.monthrange(year, month)[-1]
    hours = days * 24

    return hours


def monthly_capacity_all(op, ret, years, nerc_plant_list, fuels,
                         months=range(1,13), cap_type='nameplate capacity (mw)',
                         n_jobs=-1, print_year=False,):
    """
    Calculate the operable capacity for every month in a range of years

    inputs:
        op (df): data from the EIA-860m operable sheet - must have columns
            [op datetime, nerc, fuel category, nameplate capacity (mw)]
        ret (df): data from the EIA-860m retired sheet - must have columns
            [ret datetime, op datetime, nerc, fuel category,
            nameplate capacity (mw)]
        years (list): one or more years to calculate capacity during
        nerc_plant_list (dict): dict of dicts (year -> nerc -> list(plant id))
        fuels (list): fuel categories
        months (list): months to calculate - default is all months
        cap_type (str): options are 'nameplate capacity (mw)',
            'net summer capacity (mw)', or 'net winter capacity (mw)'
        n_jobs (int): number of threads for parallel processing
        print_year (bool): print each year during processing

    outputs:
        df: dataframe with all capacity that was operable (including out of
            service and standby) during the years and months specified
    """
    kwargs = dict(
        op = op,
        ret = ret,
        fuels = fuels,
        months = months,
        cap_type = cap_type,
        print_year = print_year
    )

    # pass a single year and all of the other arguments
    df_list = Parallel(n_jobs=n_jobs)(delayed(monthly_capacity_year)
                                      (year, nerc_plant_list[year], **kwargs)
                                       for year in years)

    # combine list of dataframes and sort the index
    op_df_capacity = pd.concat(df_list)
    op_df_capacity.sort_index(inplace=True)

    return op_df_capacity


def monthly_capacity_year(year, nerc_plants, op, ret, fuels,
                          months=range(1,13),
                          cap_type='nameplate capacity (mw)',
                          print_year=False):
    """
    Calculate the operable capacity for every month in a single year

    inputs:
        op (df): data from the EIA-860m operable sheet - must have columns
            [op datetime, nerc, fuel category, nameplate capacity (mw)]
        ret (df): data from the EIA-860m retired sheet - must have columns
            [ret datetime, op datetime, nerc, fuel category,
            nameplate capacity (mw)]
        year (int): single year to calculate capacity during
        nerc_plants (dict): nerc regions for the keys with a list of plant ids
            for each value
        fuels (list): fuel categories
        months (list): months to calculate - default is all months
        cap_type (str): options are 'nameplate capacity (mw)',
            'net summer capacity (mw)', or 'net winter capacity (mw)'
        print_year (bool): print each year during processing

    outputs:
        df: dataframe with all capacity that was operable (including out of
            service and standby) during the years and months specified
    """
    if print_year:
        print(year)

    # create list of strings and convert to datetime
    date_strings = ['{}-{}-01'.format(year, month) for month in months]
    dt_list = pd.to_datetime(date_strings, yearfirst=True)

    # Make an empty dataframe to fill with capacity and possible generation
    nercs = nerc_plants.keys()

    # Add USA to the list of nerc regions for national calculations
    nercs_national = list(nercs) + ['USA']

    # Create a multiindex
    index = pd.MultiIndex.from_product([nercs_national, fuels, [year], months],
                                   names=['nerc', 'fuel category',
                                          'year', 'month'])
    # Create an empty dataframe
    op_df_capacity = pd.DataFrame(index=index, columns=['active capacity',
                                                        'possible gen',
                                                        'datetime'])
    op_df_capacity.sort_index(inplace=True)

    # add datetime column, which is dt_list repeated for every nerc and fuel
    op_df_capacity['datetime'] = (list(dt_list) * len(nercs_national)
                                  * len(fuels))

    for dt, month in zip(dt_list, months):
        hours_in_month = month_hours(year=year, month=month)

        # Initial slice of operating and retirement dataframes by datetime
        # Don't include units the month that they come online or retire
        op_month = op.loc[(op['op datetime'] < dt), :]
        ret_month = ret.loc[(ret['ret datetime'] > dt) &
                            (ret['op datetime'] < dt), :]
        for fuel in fuels:
            # Further slice the dataframes for just the fuel category
            op_fuel = op_month.loc[op_month['fuel category'] == fuel, :]
            ret_fuel = ret_month.loc[ret_month['fuel category'] == fuel, :]

            # National totals - in case not all plant ids show up in a nerc
            total_op = op_fuel.loc[:, cap_type].sum()
            total_ret = ret_fuel.loc[:, cap_type].sum()

            total_active = total_op + total_ret

            # Insert total USA capacity for the fuel and month into dataframe
            op_df_capacity.loc[idx['USA', fuel, year, month],
                               'active capacity'] = total_active

            # Possible generation is active capacity multiplied by hours in
            # month
            op_df_capacity.loc[idx['USA', fuel, year, month],
                               'possible gen'] = hours_in_month * total_active

        # Loop through the dictionary, where each set of values is a list with
        # plant ids in a nerc
            for nerc, plant_ids in nerc_plants.items():


                # Capacity on operable sheet
                plants_op = (op_fuel.loc[op_fuel['plant id'].isin(plant_ids),
                                         cap_type]
                                    .sum())

                # Capacity on retired sheet that was active for the given month
                plants_ret = (ret_fuel.loc[ret_fuel['plant id'].isin(plant_ids),
                                           cap_type]
                                      .sum())

                # all active capacity from both sheets
                active_cap = plants_op + plants_ret

                # Add capacity from active and retired sheets to dataframe
                op_df_capacity.loc[idx[nerc, fuel, year, month],
                                   'active capacity'] = active_cap

                # Possible generation is active capacity multiplied by hours in
                # month
                op_df_capacity.loc[idx[nerc, fuel, year, month],
                                   'possible gen'] = hours_in_month * active_cap

    return op_df_capacity


def monthly_ng_type_all(op, ret, years, nerc_plant_list, fuels,
                         months=range(1,13), cap_type='nameplate capacity (mw)',
                         n_jobs=-1, print_year=False):
    """
    Calculate natural gas capacity by prime mover type (NGCC, Turbine, and
    Other) and the fraction of capacity for each.

    inputs:
        op (df): data from the EIA-860m operable sheet - must have columns
            [op datetime, nerc, fuel category, nameplate capacity (mw)]
        ret (df): data from the EIA-860m retired sheet - must have columns
            [ret datetime, op datetime, nerc, fuel category,
            nameplate capacity (mw)]
        years (list): one or more years to calculate capacity during
        nerc_plant_list (dict): dict of dicts (year -> nerc -> list(plant id))
        fuels (list): fuel categories
        months (list): months to calculate - default is all months
        cap_type (str): options are 'nameplate capacity (mw)',
            'net summer capacity (mw)', or 'net winter capacity (mw)'
        n_jobs (int): number of threads for parallel processing
        print_year (bool): print each year during processing

    outputs:
        df
    """

    kwargs = dict(
        op = op,
        ret = ret,
        fuels = fuels,
        months = months,
        cap_type = cap_type,
        print_year = print_year
    )

    # pass a single year and all of the other arguments
    df_list = Parallel(n_jobs=n_jobs)(delayed(monthly_ng_type_year)
                                     (year, nerc_plant_list[year], **kwargs)
                                       for year in years)

    # combine list of dataframes and sort the index
    op_ng_capacity = pd.concat(df_list)
    op_ng_capacity.sort_index(inplace=True)

    return op_ng_capacity



def monthly_ng_type_year(year, nerc_plants, op, ret, fuels,
                          months=range(1,13),
                          cap_type='nameplate capacity (mw)',
                          print_year=False):
    """
    Calculate the operable natural gas capacity and prime mover type
    for every month in a single year

    inputs:
        op (df): data from the EIA-860m operable sheet - must have columns
            [op datetime, nerc, fuel category, nameplate capacity (mw)]
        ret (df): data from the EIA-860m retired sheet - must have columns
            [ret datetime, op datetime, nerc, fuel category,
            nameplate capacity (mw)]
        year (int): single year to calculate capacity during
        nerc_plants (dict): nerc regions for the keys with a list of plant ids
            for each value
        fuels (list): fuel categories
        months (list): months to calculate - default is all months
        cap_type (str): options are 'nameplate capacity (mw)',
            'net summer capacity (mw)', or 'net winter capacity (mw)'
        print_year (bool): print each year during processing

    outputs:
        df
    """
    if print_year:
        print(year)

    # create list of strings and convert to datetime
    date_strings = ['{}-{}-01'.format(year, month) for month in months]
    dt_list = pd.to_datetime(date_strings, yearfirst=True)

    # Make an empty dataframe to fill with capacity and possible generation
    nercs = nerc_plants.keys()

    # Add USA to the list of nerc regions for national calculations
    nercs_national = list(nercs) + ['USA']

    # Create a multiindex
    index = pd.MultiIndex.from_product([nercs_national, [year], months],
                                   names=['nerc', 'year', 'month'])
    # Create an empty dataframe
    op_ng_type = pd.DataFrame(index=index,
                              columns=['ngcc', 'turbine', 'other', 'total',
                                       'ngcc fraction', 'turbine fraction',
                                       'other fraction'])
    op_ng_type.sort_index(inplace=True)

    # add datetime column, which is dt_list repeated for every nerc and fuel
    op_ng_type['datetime'] = (list(dt_list) * len(nercs_national))

    # Lists of prime mover codes for each category
    ngcc_pm = ['CA', 'CS', 'CT']
    turbine_pm = ['GT']
    other_pm = ['IC', 'ST']



    for dt, month in zip(dt_list, months):
        # Split out generator types into separate dataframes for given month
        op_ngcc = op.loc[(op['fuel category'] == 'Natural Gas') &
                         (op['prime mover code'].isin(ngcc_pm)) &
                         (op['op datetime'] < dt), :]
        op_turbine = op.loc[(op['fuel category'] == 'Natural Gas') &
                         (op['prime mover code'].isin(turbine_pm)) &
                         (op['op datetime'] < dt), :]
        op_other = op.loc[(op['fuel category'] == 'Natural Gas') &
                          (op['prime mover code'].isin(other_pm)) &
                          (op['op datetime'] < dt), :]

        ret_ngcc = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                         (ret['prime mover code'].isin(ngcc_pm)) &
                         (ret['ret datetime'] > dt) &
                         (ret['op datetime'] < dt), :]
        ret_turbine = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                          (ret['prime mover code'].isin(turbine_pm)) &
                          (ret['ret datetime'] > dt) &
                          (ret['op datetime'] < dt), :]
        ret_other = ret.loc[(ret['fuel category'] == 'Natural Gas') &
                          (ret['prime mover code'].isin(other_pm)) &
                          (ret['ret datetime'] > dt) &
                          (ret['op datetime'] < dt), :]

        # National level statistics
        ngcc_total = (op_ngcc.loc[:, cap_type].sum()
                      + ret_ngcc.loc[:, cap_type].sum())
        turbine_total = (op_turbine.loc[:, cap_type].sum()
                         + ret_turbine.loc[:, cap_type].sum())
        other_total = (op_other.loc[:, cap_type].sum()
                       + ret_other.loc[:, cap_type].sum())

        total = sum_ng_cap(ngcc_total, turbine_total, other_total)
        op_ng_type.loc[idx['USA', year, month], 'total'] = total
        op_ng_type.loc[idx['USA', year, month], 'ngcc'] = ngcc_total
        op_ng_type.loc[idx['USA', year, month], 'turbine'] = turbine_total
        op_ng_type.loc[idx['USA', year, month], 'other'] = other_total



        # For each nerc region
        for nerc, plant_ids in nerc_plants.items():

            ngcc = ng_nerc_type(op=op_ngcc, ret=ret_ngcc,
                                plant_list=plant_ids, cap_type=cap_type)
            turbine = ng_nerc_type(op=op_turbine, ret=ret_turbine,
                                plant_list=plant_ids, cap_type=cap_type)
            other = ng_nerc_type(op=op_other, ret=ret_other,
                                plant_list=plant_ids, cap_type=cap_type)

            total = sum_ng_cap(ngcc, turbine, other)

            op_ng_type.loc[idx[nerc, year, month], 'total'] = total
            op_ng_type.loc[idx[nerc, year, month], 'ngcc'] = ngcc
            op_ng_type.loc[idx[nerc, year, month], 'turbine'] = turbine
            op_ng_type.loc[idx[nerc, year, month], 'other'] = other

    # Calculate fraction of capacity by prime mover type

    op_ng_type['ngcc fraction'] = op_ng_type['ngcc'] / op_ng_type['total']
    op_ng_type['turbine fraction'] = op_ng_type['turbine'] / op_ng_type['total']
    op_ng_type['other fraction'] = op_ng_type['other'] / op_ng_type['total']
    op_ng_type.fillna(0, inplace=True)


    return op_ng_type

######
# A couple helper function for the NG calculations

def sum_ng_cap(ngcc, turbine, other):
    total = ngcc + turbine + other
    return total

def ng_nerc_type(op, ret, plant_list, cap_type):
    op_cap = op.loc[op['plant id'].isin(plant_list), cap_type].sum()
    ret_cap = ret.loc[ret['plant id'].isin(plant_list), cap_type].sum()

    total_cap = op_cap + ret_cap

    return total_cap
