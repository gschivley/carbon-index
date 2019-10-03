"""
[summary]

"""

import pandas as pd

from src.analysis.index import (
    adjust_epa_emissions,
    change_since_2005,
    extra_emissions_gen,  # facility_co2,
    facility_emission_gen,
    g2lb,
    generation_index,
    group_facility_data,
    group_fuel_cats,
    reduce_emission_factors,
)
from src.analysis.load_transformed_data import (
    EF,
    EIA_TOTALS,
    EPA_DF,
    FACILITY_DF,
    LOCATION_LABELS,
)
from src.params import (
    CUSTOM_FUELS,
    DATA_DATE,
    DATA_PATHS,
    NERCS,
    STATE_FACILITY_FUELS,
    STATES,
    FINAL_DATA_YEAR,
    FINAL_DATA_QUARTER,
    LAST_ANNUAL_923_YEAR,
    QUARTER_YEAR,
)
from src.util import add_facility_location, add_quarter, rename_cols, add_datetime
from src.data.make_data import get_annual_plants
from src.analysis.state2nerc import fraction_state2nerc, add_region

PREV_YEAR = FINAL_DATA_YEAR - 1
idx = pd.IndexSlice


####################
# Figure out how to pass the variables back and forth, or just keep calculating
# them multiple times.


class CarbonIndex:
    def __init__(self, *args, **kwargs):

        # self.eia_fac = EIA_TOTALS
        # self.epa = EPA_DF
        self.FACILITY_DF = FACILITY_DF
        self.co2, self.facility_gen_fuels_state = facility_emission_gen(
            eia_facility=FACILITY_DF,
            epa=EPA_DF,
            state_fuel_cat=STATE_FACILITY_FUELS,
            custom_fuel_cat=CUSTOM_FUELS,
            export_state_cats=True,
        )
        location_path = DATA_PATHS["transformed_data"] / "Facility locations_RF.csv"
        self.location_labels = pd.read_csv(location_path)
        self.co2 = add_facility_location(self.co2, self.location_labels,
                            labels=['lat', 'lon', 'state', 'nerc', 'year'])

        self.extra_co2, self.extra_gen_fuel = extra_emissions_gen(
            self.facility_gen_fuels_state, EIA_TOTALS, EF
        )

        # a dictionary to match column names
        self.nerc_frac_match = {
            "% generation": "generation (mwh)",
            "% total fuel": "total fuel (mmbtu)",
            "% elec fuel": "elec fuel (mmbtu)",
        }

        # This should work with PREV_YEAR in all cases but there is potential for

        self.annual_ids_prev = get_annual_plants(LAST_ANNUAL_923_YEAR)

    def calc_total_national_co2(self):

        facility_co2 = self.co2.groupby(["year", "month"]).sum()
        self.national_co2 = (
            facility_co2.loc[:, "final co2 (kg)"]
            + self.extra_co2.loc[:, "elec fuel co2 (kg)"]
            .groupby(["year", "month"])
            .sum()
        )

    def calc_total_national_gen(self):

        gen_fuel_cols = [
            "total fuel (mmbtu)",
            "generation (mwh)",
            "elec fuel (mmbtu)",
        ]

        gen_fuel_co2_cols = [
            "total fuel (mmbtu)",
            "generation (mwh)",
            "elec fuel (mmbtu)",
            "elec fuel fossil co2 (kg)",
            "elec fuel total co2 (kg)",
            "all fuel fossil co2 (kg)",
            "all fuel total co2 (kg)",
        ]

        # National generation with the original fuel categories ('type' column)
        self.national_gen = (
            self.facility_gen_fuels_state.groupby(["type", "year", "month"])[
                gen_fuel_co2_cols
            ]
            .sum()
            .add(self.extra_gen_fuel[gen_fuel_cols], fill_value=0)
        )

        self.national_gen_cat = group_fuel_cats(
            df=self.national_gen.reset_index(),
            fuel_cats=CUSTOM_FUELS,
            fuel_col="type",
            new_col="fuel category",
        ).set_index(["fuel category", "year", "month"])

        self.total_national_gen = self.national_gen_cat.groupby(["year", "month"]).sum()

    def calc_national_index(self):

        # Calculate national CO2 and generation
        self.calc_total_national_co2()
        self.calc_total_national_gen()

        # Monthly index
        self.national_monthly_index = self.total_national_gen.copy()
        self.national_monthly_index["final co2 (kg)"] = self.national_co2
        self.national_monthly_index["index (g/kwh)"] = (
            self.national_monthly_index["final co2 (kg)"]
            / self.national_monthly_index["generation (mwh)"]
        )
        self.national_monthly_index.reset_index(inplace=True)
        add_quarter(self.national_monthly_index)
        # g2lb(self.national_monthly_index)
        # change_since_2005(self.national_monthly_index)

        # Quarterly index
        quarter_cols = ["year", "quarter"]
        self.national_quarterly_index = self.national_monthly_index.groupby(
            quarter_cols, as_index=False
        )["generation (mwh)", "final co2 (kg)"].sum()

        self.national_quarterly_index["index (g/kwh)"] = (
            self.national_quarterly_index.loc[:, "final co2 (kg)"]
            / self.national_quarterly_index.loc[:, "generation (mwh)"]
        )
        self.national_quarterly_index["year_quarter"] = (
            self.national_quarterly_index["year"].astype(str)
            + " Q"
            + self.national_quarterly_index["quarter"].astype(str)
        )
        # change_since_2005(self.national_quarterly_index)
        # g2lb(self.national_quarterly_index)

        # Annual index
        self.national_annual_index = self.national_quarterly_index.groupby(
            "year", as_index=False
        )["generation (mwh)", "final co2 (kg)"].sum()
        self.national_annual_index["index (g/kwh)"] = (
            self.national_annual_index.loc[:, "final co2 (kg)"]
            / self.national_annual_index.loc[:, "generation (mwh)"]
        )
        # change_since_2005(self.national_annual_index)
        # g2lb(self.national_annual_index)

        indices = [
            self.national_annual_index,
            self.national_quarterly_index,
            self.national_monthly_index,
        ]
        for index in indices:
            g2lb(index)
            change_since_2005(index)

    def calc_national_gen_intensity(self):

        self.category_ef = pd.Series(reduce_emission_factors(EF), name="type")

        # Calculate emissions for each fuel type based on emission factors
        self.total_national_gen["elec fuel fossil co2 (kg)"] = (
            self.total_national_gen["elec fuel (mmbtu)"]
            .multiply(self.category_ef, level=0)
            .fillna(0)
        )

        self.total_national_gen["elec fuel fossil co2 (kg)"] = (
            self.total_national_gen["elec fuel fossil co2 (kg)"]
            + self.extra_co2.groupby(["year", "month"])["elec fuel co2 (kg)"].sum()
        )

        self.gen_monthly = (
            self.national_gen_cat.groupby(["fuel category", "year", "month"])
            .sum()
            .reset_index()
        )

        # Use actual emissions and intensity to modify emissions and calculate
        # intensity from fuel consumption and emission factors
        generation_index(
            gen_df=self.gen_monthly,
            index_df=self.national_monthly_index,
            group_by=["year", "month"],
        )
        add_quarter(self.gen_monthly)

        # Quarterly values
        self.gen_quarter = self.gen_monthly.groupby(
            ["fuel category", "year", "quarter"]
        ).sum()
        self.gen_quarter["adjusted index (g/kwh)"] = (
            self.gen_quarter["adjusted co2 (kg)"] / self.gen_quarter["generation (mwh)"]
        )
        self.gen_quarter["adjusted index (lb/mwh)"] = (
            self.gen_quarter["adjusted index (g/kwh)"] * 2.2046
        )
        self.gen_quarter["year_quarter"] = (
            self.gen_quarter.index.get_level_values("year").astype(str)
            + " Q"
            + self.gen_quarter.index.get_level_values("quarter").astype(str)
        )

        self.gen_quarter.drop(columns=["month"], inplace=True)

        self.gen_annual = self.gen_monthly.groupby(["fuel category", "year"]).sum()
        self.gen_annual["adjusted index (g/kwh)"] = (
            self.gen_annual["adjusted co2 (kg)"] / self.gen_annual["generation (mwh)"]
        )
        self.gen_annual["adjusted index (lb/mwh)"] = (
            self.gen_annual["adjusted index (g/kwh)"] * 2.2046
        )

        self.gen_annual.drop(columns=["month"], inplace=True)

    def calc_nerc_extra(self):

        # Determine the gen/fuel use of annual reporting facilities from the last
        # year
        self.eia_prev_annual = self.FACILITY_DF.loc[
            (self.FACILITY_DF["plant id"].isin(self.annual_ids_prev))
            & (self.FACILITY_DF["year"] == LAST_ANNUAL_923_YEAR),
            :
        ].copy()

        # Group to state-level fuel categories
        self.eia_prev_annual_nerc = self.eia_prev_annual.pipe(
            group_fuel_cats, fuel_cats=STATE_FACILITY_FUELS
        ).pipe(
            add_facility_location,
            label_df=self.location_labels,
            labels=["state", "nerc", "year"],
        )

        # Calculate the fraction of annual generation/fuel in each state
        # that should be allocated to each nerc.
        df_list = []
        for state in STATES:
            df_list.append(
                fraction_state2nerc(
                    self.eia_prev_annual_nerc, state, region_col="nerc", fuel_col="type"
                )
            )
        self.nerc_fraction_per_state = pd.concat(df_list)
        self.nerc_fraction_per_state.set_index(["state", "nerc", "type"], inplace=True)
        self.nerc_fraction_per_state.sort_index(inplace=True)

        self.state_total = EIA_TOTALS.groupby(["state", "year", "month", "type"])[
            list(self.nerc_frac_match.values())
        ].sum()

        eia_fac_by_type = group_fuel_cats(FACILITY_DF, STATE_FACILITY_FUELS)
        eia_fac_by_type = add_facility_location(eia_fac_by_type, self.location_labels, ['state', 'year'])
        eia_fac_by_type = eia_fac_by_type.groupby(
            ['state', 'year', 'month', 'type']
            )[list(self.nerc_frac_match.values())].sum()

        self.state_extra = (self.state_total.loc[idx[:, PREV_YEAR:, :, :], :]
                        - eia_fac_by_type.loc[idx[:, PREV_YEAR:, :, :], :])
        self.state_extra.dropna(how='all', inplace=True)
        self.state_extra = self.state_extra.reorder_levels(
            ['year', 'state', 'month', 'type']
        )
        self.state_extra.sort_index(inplace=True)

        self.nerc_fraction_per_state.sort_index(inplace=True)
        self.state_extra.sort_index(inplace=True)

        df_list = []
        for month in range(1, 13):
            df = self.nerc_fraction_per_state.copy()
            df['month'] = month
            df.set_index('month', append=True, inplace=True)
            df_list.append(df)

        nerc_frac_monthly = pd.concat(df_list, axis=0)
        nerc_frac_monthly.sort_index(inplace=True)
        nerc_frac_monthly = (nerc_frac_monthly
                            .reorder_levels(['nerc', 'state', 'month', 'type']))

        df_list_outer = []
        for year in [FINAL_DATA_YEAR]:
            df_list_inner = []
            for nerc in NERCS:
                try:
                    df = pd.concat([(nerc_frac_monthly
                                    .loc[nerc]['% generation']
                                    * self.state_extra
                                    .loc[year]['generation (mwh)']).dropna(),
                                    (nerc_frac_monthly.
                                    loc[nerc]['% total fuel']
                                    * self.state_extra
                                    .loc[year]['total fuel (mmbtu)']).dropna(),
                                    (nerc_frac_monthly
                                    .loc[nerc]['% elec fuel']
                                    * self.state_extra
                                    .loc[year]['elec fuel (mmbtu)']).dropna()],
                                    axis=1)
                    df.columns = list(self.nerc_frac_match.values())
                    df['nerc'] = nerc
                    df['year'] = year
                    df = df.groupby(['year', 'nerc', 'month', 'type']).sum()
                    df_list_inner.append(df)
                except KeyError:
                    print(f"{nerc} does not have extra state-level gen/fuel")

            df_list_outer.append(pd.concat(df_list_inner))
        self.nerc_extra = pd.concat(df_list_outer)
        self.nerc_extra.sort_index(inplace=True)

        category_ef_series = pd.Series(self.category_ef, name='type')
        self.extra_nerc.loc[:, 'total co2 (kg)'] = (self.extra_nerc
                                            .loc[:, 'total fuel (mmbtu)']
                                            .multiply(category_ef_series, 'type'))
        self.extra_nerc.loc[:, 'elec co2 (kg)'] = (self.extra_nerc
                                            .loc[:, 'elec fuel (mmbtu)']
                                            .multiply(category_ef_series, 'type'))

    def calc_nerc_co2(self):

        # Total of CO2 from facilities where we have NERC labels
        self.nerc_co2 = self.co2.groupby(['year', 'nerc', 'month'])['final co2 (kg)'].sum()

        # Add CO2 that was calculated using state-level fuel consumption
        # allocated to NERC regions
        self.nerc_total_co2 = self.nerc_co2.add(self.extra_nerc.groupby(['year', 'nerc', 'month'])['elec co2 (kg)'].sum(), fill_value=0)
        self.nerc_total_co2.name = 'final co2 (kg)'

    def calc_nerc_gen(self):

        self.gen_fuels_nerc = add_facility_location(self.gen_fuels_state,
                                            self.location_labels, labels=['nerc', 'year'])
        self.nerc_total_gen = (self.gen_fuels_nerc
                        .groupby(['year', 'nerc', 'month', 'type'])
                        ['generation (mwh)'].sum())

        self.nerc_total_gen.loc[idx[FINAL_DATA_YEAR:, :, :, :]] = (self.nerc_total_gen.loc[FINAL_DATA_YEAR:]
                                            .add(self.extra_nerc.loc[:, 'generation (mwh)']
                                                , fill_value=0))
        self.nerc_total_gen_all_fuels = self.nerc_total_gen.groupby(['year', 'nerc', 'month']).sum()
        add_datetime(self.nerc_total_gen)

    def calc_nerc_index(self):

        self.calc_nerc_extra()
        self.calc_nerc_co2()
        self.calc_nerc_gen()

        self.nerc_index = (
            self.nerc_total_co2 / self.nerc_total_gen_all_fuels['generation (mwh)']
        )

        self.nerc_index.name = 'index'

    def save_files(self):

        # National Index
        self.national_monthly_index.to_csv(
            DATA_PATHS['results'] / f'Monthly index {QUARTER_YEAR}.csv',
            index=False
        )
        self.national_quarterly_index.to_csv(
            DATA_PATHS['results'] / f'Quarterly index {QUARTER_YEAR}.csv',
            index=False
        )
        self.national_annual_index.to_csv(
            DATA_PATHS['results'] / f'Annual index {QUARTER_YEAR}.csv',
            index=False
        )

        # National generation and fuel index intensity
        self.gen_monthly.to_csv(
            DATA_PATHS['results'] / f'Monthly generation {QUARTER_YEAR}.csv',
            index=True
        )
        self.gen_quarter.to_csv(
            DATA_PATHS['results'] / f'Quarterly generation {QUARTER_YEAR}.csv',
            index=True
        )
        self.gen_annual.to_csv(
            DATA_PATHS['results'] / f'Annual generation {QUARTER_YEAR}.csv',
            index=True
        )

        # # NERC index
        # self.nerc_index.to_csv(
        #     DATA_PATHS['results'] / f'NERC gen emissions and index {QUARTER_YEAR}.csv'
        # )





def calc_national_gen_co2():

    co2, gen_fuels_state = facility_emission_gen(
        eia_facility=FACILITY_DF,
        epa=EPA_DF,
        state_fuel_cat=STATE_FACILITY_FUELS,
        custom_fuel_cat=CUSTOM_FUELS,
        export_state_cats=True,
    )

    extra_co2, extra_gen_fuel = extra_emissions_gen(gen_fuels_state, EIA_TOTALS, EF)

    facility_co2 = co2.groupby(["year", "month"]).sum()
    national_co2 = (
        facility_co2.loc[:, "final co2 (kg)"]
        + extra_co2.loc[:, "elec fuel co2 (kg)"].groupby(["year", "month"]).sum()
    )
    national_co2.name = "final co2 (kg)"

    national_gen = (
        gen_fuels_state.groupby(["type", "year", "month"])["generation (mwh)"]
        .sum()
        .add(extra_gen_fuel["generation (mwh)"], fill_value=0)
        .reset_index(inplace=True)
    )
    national_gen = group_fuel_cats(
        df=national_gen.reset_index(),
        fuel_cats=CUSTOM_FUELS,
        fuel_col="type",
        new_col="fuel category",
    ).set_index(["fuel category", "year", "month"])

    return national_gen, national_co2


def calc_national_index():

    # co2, gen_fuels_state = facility_emission_gen(
    #     eia_facility=FACILITY_DF, epa=EPA_DF,
    #     state_fuel_cat=STATE_FACILITY_FUELS,
    #     custom_fuel_cat=CUSTOM_FUELS,
    #     export_state_cats=True
    # )

    # extra_co2, extra_gen_fuel = extra_emissions_gen(gen_fuels_state, EIA_TOTALS, EF)

    # facility_co2 = co2.groupby(['year', 'month']).sum()
    # national_co2 = (facility_co2.loc[:, 'final co2 (kg)']
    #                 + extra_co2.loc[:, 'elec fuel co2 (kg)']
    #                            .groupby(['year', 'month']).sum())
    # national_co2.name = 'final co2 (kg)'

    # national_gen = (
    #     gen_fuels_state.groupby(
    #         ['type', 'year', 'month']
    #         )['generation (mwh)']
    #                    .sum()
    #                    .add(extra_gen_fuel['generation (mwh)'], fill_value=0)
    #                    .reset_index(inplace=True)
    # )
    # national_gen = (
    #             group_fuel_cats(
    #                 df=national_gen.reset_index(),
    #                 fuel_cats=CUSTOM_FUELS,
    #                 fuel_col='type',
    #                 new_col='fuel category'
    #             ).set_index(['fuel category', 'year', 'month'])
    # )

    national_gen, national_co2 = calc_national_gen_co2()

    nerc_total_gen = national_gen.groupby(["year", "month"]).sum()

    national_index = nerc_total_gen.copy()
    national_index["final co2 (kg)"] = national_co2
    national_index["index (g/kwh)"] = (
        national_index["final co2 (kg)"] / national_index["generation (mwh)"]
    )
    national_index.reset_index(inplace=True)
    add_quarter(national_index)
    g2lb(national_index)
    change_since_2005(national_index)

    monthly_index = national_index.copy()
    quarterly_index = monthly_index.groupby(["year", "quarter"])[
        "generation (mwh)", "final co2 (kg)"
    ].sum()
    quarterly_index.reset_index(inplace=True)
    quarterly_index["index (g/kwh)"] = (
        quarterly_index.loc[:, "final co2 (kg)"]
        / quarterly_index.loc[:, "generation (mwh)"]
    )
    quarterly_index["year_quarter"] = (
        quarterly_index["year"].astype(str)
        + " Q"
        + quarterly_index["quarter"].astype(str)
    )
    change_since_2005(quarterly_index)
    g2lb(quarterly_index)

    annual_index = quarterly_index.groupby("year")[
        "generation (mwh)", "final co2 (kg)"
    ].sum()
    annual_index.reset_index(inplace=True)
    annual_index["index (g/kwh)"] = (
        annual_index.loc[:, "final co2 (kg)"] / annual_index.loc[:, "generation (mwh)"]
    )
    change_since_2005(annual_index)
    g2lb(annual_index)


def calc_national_gen():

    self.category_ef = reduce_emission_factors(EF)

    national_gen, national_co2 = calc_national_gen_co2()

    national_gen["elec fuel fossil co2 (kg)"] = 0
    for fuel in self.category_ef.keys():
        national_gen.loc[idx[fuel, :, :], "elec fuel fossil co2 (kg)"] = (
            national_gen.loc[idx[fuel, :, :], "elec fuel (mmbtu)"] * self.category_ef[fuel]
        )

    national_gen["elec fuel fossil co2 (kg)"] = (
        national_gen["elec fuel fossil co2 (kg)"] + extra_co2["elec fuel co2 (kg)"]
    )
