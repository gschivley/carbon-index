import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.collections
import pandas as pd
import seaborn as sns
import numpy as np
from statsmodels.tsa.tsatools import detrend
import statsmodels.formula.api as sm

def region_facet_grid(df, plot_function, x_axis, y_axis, col_order=None,
                      suptitle='', add_legend=False, x_label=None,
                      y_label=None, FG_kwargs={}, plot_kwargs={},
                      context='notebook', font_scale=1.2):
    sns.set_context(context, font_scale)
    g = sns.FacetGrid(df, col_order=col_order, **FG_kwargs)
    g.map(plot_function, x_axis, y_axis, **plot_kwargs)
    g.set_xticklabels(rotation=35)
    if add_legend:
        g.add_legend()
    if suptitle:
        plt.suptitle(suptitle, y=1.02, size=15)
    if col_order and 'col' in FG_kwargs:
        axes = g.axes.flatten()
        for ax, title in zip(axes, col_order):
            ax.set_title(title)
    if x_label or y_label:
        g.set_axis_labels(x_label, y_label)


def add_count(df):
    'Add a 0-indexed column for the regression line'
    nercs = df['variable'].unique()
    for nerc in nercs:
        df.loc[df['variable'] == nerc, 'count'] = range(
                                            len(df.loc[df['variable'] == nerc])
                                                        )

def rolling_corr_plot(index, region_pairs, window, center=True,
                      order=None, legend_order=None, sup_title=None,
                      detrend_series=False, diff=False, annual=False,
                      seasonal=False, shift=1, fill_alpha=0.3):
    """
    Calculate the rolling correlation of detrended CO2 intensity between pairs
    of regions. Multiple detrend methods are possible, but only the "seasonal"
    method is used in the final figures.

    inputs:
        index (df): dataframe with monthly co2 intensity of each region
        region_pairs (dict): list of tuples, where each tuple is a pair of
            regions to compare
        window (int): length of the rolling window
        center (bool): if the rolling correlation window should be centered
        order (list): order of NERC region facet windows
        legend order (list): order of NERC regions in legend
        sup_title (str): sup title to place above the facet grid
        detrend_series (bool): if the co2 intensity data should be detrended
        diff (bool): use a differencing method to detrend
        annual (bool): use a linear regression detrend separately on each year
        seasonal (bool): detrend with a 12-month rolling mean
        shift (int): value of shift for the diff detrend method (1 = 1 month)
        fill_alpha: alpha value for the 'fill_between' of regplot uncertainty
    """

    df = index.copy()

    df.reset_index(inplace=True)
    nercs = df['nerc'].unique()
    df.set_index(['nerc', 'datetime'], inplace=True)
    df.sort_index(inplace=True)

    df_list = []
    if detrend_series:
        for nerc in nercs:
            if diff:
                df.loc[idx[nerc, :], 'index (g/kwh)'] = \
                    diff_detrend(df.loc[idx[nerc, :], 'index (g/kwh)'], shift)

            if annual:
                df.loc[idx[nerc, :], 'index (g/kwh)'] = \
                    annual_detrend(df.loc[idx[nerc, :]])

            if seasonal:
                trend = (df.loc[nerc, 'index (g/kwh)']
                           .rolling(12, center=True)
                           .mean())
                detr = df.loc[nerc, 'index (g/kwh)'] - trend
                detr = pd.DataFrame(detr)
                detr['nerc'] = nerc
                df_list.append(detr)

            else:
                df.loc[idx[nerc, :], 'index (g/kwh)'] = \
                    detrend(df.loc[idx[nerc, :], 'index (g/kwh)'])

        if seasonal:
            # Need to concat the list of dataframes
            df = pd.concat(df_list)
            df.reset_index(inplace=True)
            df.set_index(['nerc', 'datetime'], inplace=True)

    df.dropna(inplace=True)

    corr_df = pd.concat([(df.loc[regions[0]]['index (g/kwh)']
                            .rolling(window, center=center)
                            .corr(df.loc[regions[1]]['index (g/kwh)']))
                         for regions in region_pairs], axis=1)

    # Create columns with the names of each region. Legacy code, but still
    # functional
    cols = ['{} | {}'.format(regions[0], regions[1])
            for regions in region_pairs]
    corr_df.columns = cols

    # Go from wide-format to tidy
    corr_tidy = pd.melt(corr_df.reset_index(), id_vars=['datetime'],
                        value_name='Correlation')
    corr_tidy['region1'] = corr_tidy['variable'].str.split(' | ').str[0]
    corr_tidy['region2'] = corr_tidy['variable'].str.split(' | ').str[-1]

    # Add the 0-indexed 'count' column
    add_count(corr_tidy)

    if not order:
        order = ['WECC', 'TRE', 'SPP', 'SERC', 'RFC', 'MRO']

    if not legend_order:
        legend_order = ['SPP', 'TRE', 'SERC', 'MRO', 'FRCC', 'NPCC', 'WECC']
    legend_len = len(legend_order)

    g = sns.FacetGrid(corr_tidy.dropna(), col='region1', col_wrap=2, aspect=1.2,
                      hue='region2', palette='tab10', size=2.5,
                      hue_order=legend_order)
    # Use regplot to get the regression line, but set scatter marker size to 0
    g.map(sns.regplot, 'count', 'Correlation', scatter=False,#marker='.',
          truncate=True, line_kws={'lw': 2})

    # regplot only does a scatter - add plt.plot for the lines
    g.map(plt.plot, 'count', 'Correlation')


    # Create custom patch lines for the legend - the default dots were small
    plot_colors = sns.color_palette('tab10', legend_len)
    legend_patches = [mlines.Line2D([], [], color=c) for c in plot_colors]
    legend_data = dict(zip(legend_order, legend_patches))
    g.add_legend(legend_data=legend_data, title='Second Region')

    axes = g.axes.flatten()

    # Grid lines at the start of each even year from 2004-16
    years = range(2004, 2017, 2)
    distance = 24 # months in 2 years
    # tick locations
    x_ticks = [(x * distance) + 6 for x in range(1, 8)]
    for ax, title in zip(axes, order):
        ax.set_title(title)
        ax.set_xticks(x_ticks)
        ax.set_xlim(12, None)

        # find PolyCollection objects (confidence intervals for regplot) and
        # change the alpha to make them darker
        for collection in ax.collections:
            if isinstance(collection, matplotlib.collections.PolyCollection):
                collection.set_alpha(fill_alpha)

    # Year for the ticklabels
    g.set_xticklabels(years, rotation=35)
    g.set_xlabels('Year')

    # Suptitle if desired
    if sup_title:
        plt.subplots_adjust(top=0.9)
        g.fig.suptitle(sup_title)
