"""
[summary]

"""

import pandas as pd

from src.params import (DATA_PATHS, FINAL_DATA_QUARTER, FINAL_DATA_YEAR,
                        QUARTER_YEAR)


# Constants
QUARTER_WORD_DICT = {
    1: 'first',
    2: 'second',
    3: 'third',
    4: 'fourth'
}
CURRENT_QUARTER = f'Q{FINAL_DATA_QUARTER}'
PREV_YEAR = FINAL_DATA_YEAR - 1
QUARTER_WORD = QUARTER_WORD_DICT[FINAL_DATA_QUARTER]
CURRENT_Y_Q = f'{FINAL_DATA_YEAR} Q{FINAL_DATA_QUARTER}'
PREV_Y_Q = f'{PREV_YEAR} Q{FINAL_DATA_QUARTER}'

index_2005 = 599.1
index_2005_lb = 1321
co2_2005 = 2429.59

# Read data files
index_path = DATA_PATHS['results'] / f'Quarterly index {QUARTER_YEAR}.csv'
index = pd.read_csv(index_path).set_index('year_quarter')

gen_path = DATA_PATHS['results'] / f'Quarterly generation {QUARTER_YEAR}.csv'
gen = pd.read_csv(gen_path)
total_gen = gen.groupby(['year', 'quarter'], as_index=False).sum()
total_gen['year_quarter'] = total_gen.apply(lambda row: '{} Q{}'
                                            .format(int(row['year']),
                                                    int(row['quarter'])), axis=1)
total_gen['fuel category'] = 'Total'

gen = pd.concat([gen, total_gen], sort=True)
fuel_cats = gen['fuel category'].unique()
gen.set_index(['fuel category', 'year_quarter'], inplace=True)

# Calculate change in values
curr_q_index_lb = index.loc[CURRENT_Y_Q, 'index (lb/mwh)']
curr_q_index_str = '{:,}'.format(int(round(curr_q_index_lb)))

prev_q_index_lb = index.loc[PREV_Y_Q, 'index (lb/mwh)']
prev_q_index_str = '{:,}'.format(int(round(prev_q_index_lb)))

index_yoy_change = curr_q_index_lb - prev_q_index_lb
index_yoy_per = index_yoy_change / prev_q_index_lb
index_yoy_per_str = '{:.0f}'.format(abs(index_yoy_per * 100))

if index_yoy_per < 0:
    direction = 'down'
else:
    direction = 'up'


prev_q_str = (
    f'The Carnegie Mellon Power Sector Carbon Index provides a comprehensive '
    f'picture of the carbon intensity of electricity production in the during '
    f'the previous 12 months and over an extended period to 2001. The CMU index '
    f'also provides a summary of how much electricity generation is from coal, '
    f'natural gas, nuclear, and renewables. According to the Carnegie Mellon '
    f'Power Sector Carbon Index, U.S. power plant emissions averaged '
    f'{curr_q_index_str} lb CO<sub>2</sub> per MWh in the {QUARTER_WORD} quarter '
    f'of {FINAL_DATA_YEAR}, which was {direction} {index_yoy_per_str} percent '
    f'from the same time frame in {PREV_YEAR}.')

# Compare to 2005
curr_q_index_lb = round(index.loc[CURRENT_Y_Q, 'index (lb/mwh)'])
curr_q_index = index.loc[CURRENT_Y_Q, 'index (g/kwh)']
curr_roll_co2 = index.loc[:, 'final co2 (kg)'][-4:].sum() / 1e9
curr_roll_co2_str = '{:,}'.format(int(round(curr_roll_co2)))

# only add the last 4 values (last 4 quarters) for the rolling totals
curr_roll_index = (index.loc[:, 'final co2 (kg)'][-4:].sum()
                   / index.loc[:, 'generation (mwh)'][-4:].sum())

curr_roll_index_lb = round(curr_roll_index * 2.2046)
index_change_2005_str = '{:.0%}'.format(abs(index.loc[CURRENT_Y_Q,
                                            'change since 2005']))
roll_change_2005 = abs((index_2005 - curr_roll_index) / index_2005)
roll_change_2005_str = '{:.0%}'.format(roll_change_2005)

roll_co2_change = abs((co2_2005 - curr_roll_co2) / co2_2005)
roll_co2_change_str = '{:.0%}'.format(roll_co2_change)

change_2005_str = (
    f'The Power Sector Carbon Index for {CURRENT_QUARTER} of {FINAL_DATA_YEAR} '
    f'was {index_change_2005_str} lower than in the annual value in 2005, from '
    f'{index_2005_lb:,} lb CO<sub>2</sub> per MWh to {curr_q_index_lb:,.0f} lb '
    f'CO<sub>2</sub> per MWh (or {index_2005:.0f} to {curr_q_index:.0f} g '
    f'CO<sub>2</sub> per kWh). As of {CURRENT_QUARTER} of {FINAL_DATA_YEAR}, '
    f'the rolling annual average carbon intensity was {curr_roll_index_lb:,.0f} '
    f'lb CO<sub>2</sub> per MWh (or {curr_roll_index:.0f} g CO<sub>2</sub> per '
    f'kWh), which is {roll_change_2005_str} lower than the annual value in 2005. '
    f'Total annual rolling CO<sub>2</sub> emissions were {curr_roll_co2_str} '
    f'million metric tonnes, which was {roll_co2_change_str} lower than in 2005. '
)

# Generation
idx = pd.IndexSlice
fuels = ['Total', 'Coal', 'Natural Gas', 'Hydro', 'Wind', 'Solar',
         'Nuclear', 'Other', 'Other Renewables', ]
gen_results = []
for fuel in fuels:
    prev_gen = gen.loc[idx[fuel, PREV_Y_Q], 'generation (mwh)']
    prev_gen_str = '{:.0f} million MWh'.format(prev_gen / 1e6)

    curr_gen = gen.loc[idx[fuel, CURRENT_Y_Q], 'generation (mwh)']
    curr_gen_str = '{:.0f} million MWh'.format(curr_gen / 1e6)

    per_change = (curr_gen - prev_gen) / prev_gen
    per_change_str = '{:.0%}'.format(abs(per_change))

    if prev_gen > curr_gen:
        direction = 'down'
    else:
        direction = 'up'

    kwargs = {
        'fuel': fuel,
        'dir': direction,
        'change': per_change_str,
        'curr_q': CURRENT_Y_Q,
        'curr_gen': curr_gen_str,
        'prev_q': PREV_Y_Q,
        'prev_gen': prev_gen_str
    }

    result_str = (
        '- {fuel} generation was {dir} {change} in {curr_q} ({curr_gen}) when '
        'compared to {prev_q} ({prev_gen}).').format(**kwargs)

    if fuel != 'Total':
        total_gen = gen.loc[idx['Total', CURRENT_Y_Q], 'generation (mwh)']
        per_gen = curr_gen / total_gen
        per_gen_str = '{:.0%}'.format(per_gen)

        second_str = (
            ' {} represented {} of total generation in {}'
        ).format(fuel, per_gen_str, CURRENT_Y_Q)

        result_str += second_str

    gen_results.append(result_str)

first_header = (
    f'## Comparing {CURRENT_QUARTER} {FINAL_DATA_YEAR} to '
    f'{CURRENT_QUARTER} {PREV_YEAR}'
)

second_header = (
    f'## Comparing performance in {FINAL_DATA_YEAR} to 2005'
)

third_header = (
    f'## Highlights of the {CURRENT_Y_Q} results'
)


def write_blog_text():
    blog_path = DATA_PATHS['web_files'] / 'blog.txt'
    with blog_path.open(mode='w') as outF:
        outF.write(first_header)
        outF.write('\n')
        outF.write(prev_q_str)
        outF.write('\n\n')
        outF.write(second_header)
        outF.write('\n')
        outF.write(change_2005_str)
        outF.write('\n\n')

        outF.write(third_header)
        outF.write('\n')
        for line in gen_results:
            outF.write(line)
            outF.write('\n')
