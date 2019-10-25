"""
Calculate state-level emissions, generation, and carbon intensity

"""

from joblib import Parallel, delayed
import pandas as pd
from src.params import (
    DATA_DATE,
    DATA_PATHS,
    STATES,
    STATE_FACILITY_FUELS,
    CUSTOM_FUELS,
)
from src.analysis.index import (
    facility_emission_gen,
    group_fuel_cats,
    extra_emissions_gen,
)
from src.util import add_facility_location, add_quarter
from src.analysis.load_transformed_data import (
    load_ef,
    load_facility_gen_fuel_data,
    load_epa_data,
    load_eia_state_gen_data,
)

EF = load_ef()
FACILITY_DF = load_facility_gen_fuel_data()
EPA_DF = load_epa_data()
EIA_TOTALS = load_eia_state_gen_data()

# EF_PATH = DATA_PATHS['inputs'] / 'Final emission factors.csv'
# EF = pd.read_csv(EF_PATH, index_col=0)

# FACILITY_PATH = (
#     DATA_PATHS['eia_compiled']
#     / 'facility_gen_fuel_data_{}.parquet'.format(DATA_DATE)
# )
# facility_df = pd.read_parquet(FACILITY_PATH)
# facility_locations = facility_df.loc[:, ['plant id', 'state']].drop_duplicates()

# epa_path = (
#     DATA_PATHS['epa_emissions']
#     / 'epa_emissions_{}.parquet'.format(DATA_DATE)
# )
# epa_df = pd.read_parquet(epa_path)
# epa_df = add_facility_location(epa_df, facility_locations, labels=['state'])

# STATE_PATH = (
#     DATA_PATHS['eia_compiled']
#     / 'state_gen_fuel_data_{}.parquet'.format(DATA_DATE)
# )
# eia_totals = pd.read_parquet(STATE_PATH)
# eia_totals.reset_index(inplace=True)
# # Remove fuel categories that are duplicated with other categories
# eia_totals = eia_totals.loc[~eia_totals['type'].isin(['SPV', 'AOR', 'TSN'])]


def single_state_index_gen(state):

    eia_fac_state = FACILITY_DF.loc[FACILITY_DF.state == state, :].copy()
    eia_totals_state = EIA_TOTALS.loc[EIA_TOTALS.state == state, :].copy()
    epa_state = EPA_DF.loc[EPA_DF.state == state, :].copy()

    co2, gen_fuels_state = facility_emission_gen(
        eia_facility=eia_fac_state,
        epa=epa_state,
        state_fuel_cat=STATE_FACILITY_FUELS,
        custom_fuel_cat=CUSTOM_FUELS,
        export_state_cats=True,
        print_status=False
    )

    extra_co2, extra_gen = extra_emissions_gen(gen_fuels_state,
                                               eia_totals_state, EF)

    # Combine facility and extra co2, name the series
    co2_monthly = co2.groupby(['year', 'month']).sum()
    total_co2 = (co2_monthly.loc[:, 'final co2 (kg)']
                 + extra_co2.loc[:, 'elec fuel co2 (kg)']
                            .groupby(['year', 'month']).sum())
    total_co2.name = 'final co2 (kg)'

    # Total gen, and the co2 intensity
    total_gen = (eia_totals_state
                 .groupby(['year', 'month'])['generation (mwh)'].sum())

    state_index = pd.concat([total_co2, total_gen], axis=1)
    state_index['index (g/kwh)'] = (state_index['final co2 (kg)']
                                    / state_index['generation (mwh)'])
    state_index['state'] = state
    state_index.set_index('state', append=True, inplace=True)

    # Generation by fuel category
    gen_category = group_fuel_cats(eia_totals_state, CUSTOM_FUELS,
                                   fuel_col='type', new_col='fuel category')

    keep_cols = ['fuel category', 'generation (mwh)', 'total fuel (mmbtu)',
                 'elec fuel (mmbtu)', 'all fuel co2 (kg)',
                 'elec fuel co2 (kg)', 'year', 'month']
    gen_category = gen_category[keep_cols]
    gen_category['state'] = state
    gen_category.set_index(['year', 'month', 'state'], inplace=True)

    return (state_index, gen_category)


def calc_state_index_gen():

    index_gen_tuples = (
        Parallel(n_jobs=-1)(delayed(single_state_index_gen)(state)
                            for state in STATES)
    )

    index_list, gen_list = map(list, zip(*index_gen_tuples))
    # gen_list = []
    # for state in STATES:
    #     eia_fac_state = facility_df.loc[facility_df.state == state, :].copy()
    #     eia_totals_state = eia_totals.loc[eia_totals.state == state, :].copy()
    #     epa_state = epa_df.loc[epa_df.state == state, :].copy()

    #     co2, gen_fuels_state = facility_emission_gen(
    #         eia_facility=eia_fac_state,
    #         epa=epa_state,
    #         state_fuel_cat=STATE_FACILITY_FUELS,
    #         custom_fuel_cat=CUSTOM_FUELS,
    #         export_state_cats=True,
    #         print_status=False
    #     )

    #     extra_co2, extra_gen = extra_emissions_gen(gen_fuels_state,
    #                                             eia_totals_state, ef)

    #     # Combine facility and extra co2, name the series
    #     co2_monthly = co2.groupby(['year', 'month']).sum()
    #     total_co2 = (co2_monthly.loc[:, 'final co2 (kg)']
    #                 + extra_co2.loc[:, 'elec fuel co2 (kg)']
    #                             .groupby(['year', 'month']).sum())
    #     total_co2.name = 'final co2 (kg)'

    #     # Total gen, and the co2 intensity
    #     total_gen = (eia_totals_state
    #                 .groupby(['year', 'month'])['generation (mwh)'].sum())

    #     state_index = pd.concat([total_co2, total_gen], axis=1)
    #     state_index['index (g/kwh)'] = (state_index['final co2 (kg)']
    #                                     / state_index['generation (mwh)'])
    #     state_index['state'] = state
    #     state_index.set_index('state', append=True, inplace=True)

    #     # Generation by fuel category
    #     gen_category = group_fuel_cats(eia_totals_state, CUSTOM_FUELS,
    #                                 fuel_col='type', new_col='fuel category')

    #     keep_cols = ['fuel category', 'generation (mwh)', 'total fuel (mmbtu)',
    #                 'elec fuel (mmbtu)', 'all fuel co2 (kg)',
    #                 'elec fuel co2 (kg)', 'year', 'month']
    #     gen_category = gen_category[keep_cols]
    #     gen_category['state'] = state
    #     gen_category.set_index(['year', 'month', 'state'], inplace=True)

    #     # Add each df to the list
    #     index_list.append(state_index)
    #     gen_list.append(gen_category)

    # Combine lists of dataframes
    state_index_all = pd.concat(index_list)
    add_quarter(state_index_all)

    gen_category_all = pd.concat(gen_list)
    add_quarter(gen_category_all)

    index_fn = 'state_index_{}.csv'.format(DATA_DATE)
    gen_fn = 'state_generation_{}.csv'.format(DATA_DATE)

    state_index_all.to_csv(DATA_PATHS['results'] / index_fn)
    gen_category_all.to_csv(DATA_PATHS['results'] / gen_fn)
