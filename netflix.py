"""
Functions for inspecting Netflix data contained in ViewingActivity.csv.
"""
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
from matplotlib import cm
import numpy as np
import os
import pandas as pd

view_activity_path = os.path.join('datasets', 'ViewingActivity.csv')


def load_viewing_activity(path):
    """Load Netflix ViewingActivity.csv file.

    Add Start Date and Month Begin columns and convert Duration to minutes.

    Args:
        path (str): Full path to Netflix data file

    Returns:
        (DataFrame)
    """
    data = pd.read_csv(path, parse_dates=['Start Time'])
    data['Start Date'] = data['Start Time'].dt.date
    # Use Month Begin for grouping data by month.
    data['Month Begin'] = data['Start Date'] - pd.tseries.offsets.MonthBegin()
    # Convert duration to minutes (scalar).
    data['Duration'] = pd.to_timedelta(data['Duration']) / pd.Timedelta(minutes=1)

    return data


def sum_usage_by_date_and_device(data, display_all=False):
    """Sum usage for each device on each day.

    Args:
        data (DataFrame)
        display_all (bool): Show all rows if True.

    Returns:
        (DataFrame)
    """
    summed = (data[['Start Date', 'Device Type', 'Duration']]
                .groupby(['Start Date', 'Device Type'])
                .sum()
                .sort_values(by='Start Date', ascending=False))
    try:
        if display_all:
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                display(summed)
        else:
            display(summed)
    except Exception:
        # Display is a Jupyter function.
        pass

    return summed


def count_show_watches(dataframe, display_all=False):
    """Count each watch of a show.

    A "watch" could mean resuming an episode/movie that wasn't finished.

    Args:
        dataframe (DataFrame)
        display_all (bool): Show all rows if True.

    Returns:
        (DataFrame)
    """
    data = dataframe.copy()
    data['Short Title'] = data['Title'].str.replace(':.*$', '')
    count = (data.loc[data['Supplemental Video Type'] != 'TRAILER']
        .groupby(['Short Title', 'Profile Name'], as_index=False)
        .count()
        .sort_values(by='Duration', ascending=False))

    for col in count.columns:
        if col not in ['Short Title', 'Profile Name', 'Duration']:
            count.drop(col, 'columns', inplace=True)
    count.rename(columns={'Duration': 'Count'}, inplace=True)

    try:
        if display_all:
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                display(count)
        else:
            display(count)
    except Exception:
        # Display is a Jupyter function.
        pass

    return count


def get_device_color_map(data):
    """Get a unique color for each device.

    Args:
        data (DataFrame)

    Returns:
        (dict[str, Tuple[float, float, float, float]])
    """
    cmap = cm.get_cmap('Set3')
    devices = data['Device Type'].unique()
    mapping = {}
    spacing = 1 / len(devices)
    for ind, dev in enumerate(devices):
        mapping[dev] = cmap(ind * spacing)
    return mapping


def plot_usage_by_date_and_device(data):
    """Plot usage for each device for each day.

    Args:
        data (DataFrame)
    """
    fig, axes = plt.subplots(figsize=(16, 9))
    axes.set_title('Device Usage by Date')
    axes.set_ylabel('Minutes')
    # Plot each device's usage by date on the same graph.
    for _, group in data.groupby('Device Type'):
        # The label is the same for every row, so just get the first one.
        label = group['Device Type'].head(1).array[0]
        axes.plot_date(group['Start Date'], group['Duration'], label=label)
    axes.legend()

    return fig


def plot_monthly_usage_by_device(data):
    """Plot monthly usage for each device.

    Args:
        data (DataFrame)
    """
    fig, axes = plt.subplots(figsize=(12, 8))
    axes.set_title('Monthly Usage by Device')
    axes.set_ylabel('Hours')
    color_mapping = get_device_color_map(data)

    # Plot each device's usage by date on the same graph.
    for name, group in data.groupby(['Month Begin', 'Device Type']):
        device_sum = group['Duration'].sum() / 60
        label = name[1]
        axes.plot_date(name[0], device_sum, color=color_mapping[label], label=label)

    handles, labels = fig.gca().get_legend_handles_labels()
    labels, ids = np.unique(labels, return_index=True)
    handles = [handles[i] for i in ids]
    axes.legend(handles, labels, loc='best')

    return fig
