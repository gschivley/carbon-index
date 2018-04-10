import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.collections
import pandas as pd
import seaborn as sns
import numpy as np
from statsmodels.tsa.tsatools import detrend
idx = pd.IndexSlice
from os.path import join

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
                      hue='region2', palette='tab10', size=2,
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


def monthly_fuel_gen(gen_df, fuel, folder, file_date, file_type='pdf', dpi=350,
                     save=False):
    """
    Make a FacetGrid plot of monthly generation for a single fuel category

    inputs:
        gen_df (dataframe): monthly generation for all fuels
        fuel (string): name of the fuel category to plot
        folder (path): folder where the plot should be saved
        file_type (string): file format (e.g. pdf, png, etc)
        dpi (int): dots per inch resolution for saved file (if not pdf)
        save (bool): if True, save the file

    """
    order = ['USA', 'SPP', 'MRO', 'RFC', 'SERC', 'TRE', 'FRCC', 'WECC', 'NPCC']
    temp = gen_df.loc[idx[:, fuel, :], :].reset_index()
    temp['Month'] = temp['datetime'].dt.month
    temp['Year'] = temp['datetime'].dt.year
    temp['million mwh'] = temp['generation (mwh)'] / 1e6

    with sns.plotting_context('paper', font_scale=1):

        g = sns.factorplot(x='Month', y='million mwh', hue='Year', sharey=False,
                           data=temp, col='nerc', col_wrap=3, col_order=order,
                           palette='viridis_r', scale=0.5, size=2)

        axes = g.axes.flatten()
        for ax, title in zip(axes, order):
            ax.set_title(title)
            ax.set_ylim(0, None)
    #         ax.set_ylim(0, 1050)
            if title in ['USA', 'RFC', 'FRCC']:
                ax.set_ylabel('Million MWh\n({})'.format(fuel))

    path = join(folder, 'Monthly {} gen {}.{}'.format(fuel, file_date, file_type))
    if save:
        plt.savefig(path, bbox_inches='tight', dpi=dpi)


def plot_nerc_annual(regions_proj, states_proj, data_col, text_col,
                     cmap='cividis_r', vmin=None, vmax=None, title=None,
                     cbar_title=None, **kwargs):

    states_ec = kwargs.get('states_ec', '0.6')
    regions_ec = kwargs.get('regions_ec', '0.2')
    regions_lw = kwargs.get('regions_lw', 0.75)
    font_size = kwargs.get('font_size', 9)
    bbox_alpha = kwargs.get('bbox_alpha', 0.7)
    FRCC_x = kwargs.get('FRCC_x', 4.75)
    SERC_x = kwargs.get('SERC_x', 2)
    SERC_y = kwargs.get('SERC_y', -2)
    SPP_y = kwargs.get('SPP_y', 1.75)
    RFC_y = kwargs.get('RFC_y', -0.5)


    fig, ax = plt.subplots(figsize=(8,3.5))
    # set aspect to equal. This is done automatically
    # when using *geopandas* plot on it's own, but not when
    # working with pyplot directly.
    ax.set_aspect('equal')


    regions_proj.plot(ax=ax, column=data_col, cmap=cmap, legend=True,
                      vmin=vmin, vmax=vmax)
    states_proj.plot(ax=ax, color='none', edgecolor=states_ec)
    regions_proj.plot(ax=ax, color='none', edgecolor=regions_ec,
                     linewidth=regions_lw)
#     plt.text(x=1.1, y=1.01, s=cbar_title, transform=ax.transAxes,
#              ha='center', va='bottom', fontdict={'size':font_size})
    plt.title(title)

    for point, nerc in zip(regions_proj.centroid, regions_proj['nerc'].values):
        text = regions_proj.loc[regions_proj['nerc']==nerc, text_col].values[0]
#         text = '{}'.format(nerc, reduce)
        x = point.x
        y = point.y
        if nerc == 'FRCC':
            x = x + conv_lon(FRCC_x)#-79
            y = y - conv_lat(1)#28
            rot = -67
            plt.text(x, y, text, ha='center', va='center',
                     fontdict={'size':font_size})

        elif nerc == 'NPCC':
            x = x - conv_lon(1.5)
            y = y + conv_lat(2.1)
            plt.text(x, y, text, ha='center',
                     fontdict={'size':font_size})

        elif nerc == 'SERC':
            x = x + conv_lon(SERC_x)
            y = y + conv_lat(SERC_y)
            plt.text(x, y, text, ha='center', va='center',
                     bbox=dict(facecolor='white',
                                alpha=bbox_alpha,
                                boxstyle="square"),
                     fontdict={'size':font_size})
        elif nerc == 'RFC':
#             x = x + conv_lon(RFC_x)
            y = y + conv_lat(RFC_y)
            plt.text(x, y, text, ha='center', va='center',
                     bbox=dict(facecolor='white',
                                alpha=bbox_alpha,
                                boxstyle="square"),
                     fontdict={'size':font_size})

        elif nerc == 'SPP':
    #         x = x + 2
            y = y + conv_lat(SPP_y)
            plt.text(x, y, text, ha='center', va='center',
                     bbox=dict(facecolor='white',
                                alpha=bbox_alpha,
                                boxstyle="square"),
                     fontdict={'size':font_size})

        else:
            plt.text(x, y, text, ha='center', va='center',
                     bbox=dict(facecolor='white',
                                alpha=bbox_alpha,
                                boxstyle="square"),
                     fontdict={'size':font_size})

    sns.despine(left=True, bottom=True)
    ax.set_yticklabels(labels=[])
    ax.set_xticklabels(labels=[])

    cax = fig.get_axes()[-1]
    cax.set_title(cbar_title, fontdict={'size':font_size})


# https://gist.github.com/springmeyer/871897
# Convert lon/lat into meters for use in the projected space

def conv_lon(x):
    newx = x * 20037508.34 / 180
    return newx

def conv_lat(y):
    newy = np.log(np.tan((90 + y) * np.pi / 360)) / (np.pi / 180)
    newy *= 20037508.34 / 180
    return newy
