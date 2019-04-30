#!/usr/bin/env python3

import datetime
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mpldates
from cycler import cycler

import click
from pathlib import Path

# Requires Python 3.6+ for format strings

# Add fill variations for large numbers of colors
color_cycler = mpl.rc_params()['axes.prop_cycle']
hatch_cycler = cycler(hatch=['', '///', '+++', '***'])
prop_cycle = hatch_cycler * color_cycler


# This is a workaround because the pandas stacked plot does not use dates, just integers. Grrr!
def stacked_plot(df, ax=None, **kargs):
    old = None
    current_prop = prop_cycle()
    for column in df:
        current = df[column]
        if old is None:
            bottom = current*0
        else:
            bottom = df.cumsum(axis=1)[old]
        art = ax.bar(df.index, current, align='edge', bottom=bottom, **next(current_prop), **kargs)
        art.set_label(column)
        old = column

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='center left')


@click.group(chain=True)
@click.pass_context
@click.option('--filename', '-f', type=click.File('rb'), multiple=True, help='Files to read in (defaults to all CSVs)')
@click.option('--name', '-n', default='', help='Add prefix to all plots')
@click.option('--minor', '-m', is_flag=True, help='Use minor version too')
@click.option('--package', '-p', multiple=True, help='Select only one package instead of all')
@click.option('--filter-package', '-x', multiple=True, help='Remove package(s) from package list')
@click.option('--unique', is_flag=True, help='Filter based on OS "uniqueness"')
@click.option('--filter', type=(str, str), multiple=True, help='Filter based on KEY VALUE')
def cli(ctx, filename, name, minor, package, filter_package, unique, filter):
    ctx.ensure_object(dict)

    if not filename:
        filename = list(map(str, Path('.').glob('*.csv')))

    print("Reading:", *filename)

    df = pd.concat(
                 pd.read_csv(f, parse_dates=['timestamp'],
                             infer_datetime_format=True,
                             dtype={'details_distro_version':str})
                 for f in filename)

    # Optional "Uniqueness" column
    df["uniqueness"] = df[["file_project", "file_version", "country_code",
                           "details_distro_name", "details_distro_version",
                           "details_system_name", "details_system_release"]].apply(
                                lambda x: hash(",".join(str(y) for y in x)), axis=1)

    # Drop patch versions
    if not minor:
        df.file_version = df.file_version.str.split('.', 3).str[:2].str.join('.')

    # Fill out packages
    if not package:
        package = df.file_project.unique()

    if filter_package:
        package = list(package)
        for p in filter_package:
            package.remove(p)

    if unique:
        print("Before unique filter:", len(df))
        df.drop_duplicates(["uniqueness"], inplace=True)
        print("After unique filter:", len(df))

    if filter:
        for key, value in filter:
            print("Before filter:", len(df), key, '==' , value)
            df = df[df[key] == value]
            print("After filter:", len(df))

    ctx.obj['df'] = df
    ctx.obj['prefix'] = name
    ctx.obj['packages'] = package

    print("Packages:", *package)



@cli.command(help='Make a weekly or daily downloads plot')
@click.option('--daily', is_flag=True, help='Plot daily instead of weekly')
@click.option('--key', '-k', default='file_version', help='Item to plot over, good choices include file_version (default)'
             ' and details_system_name')
@click.pass_context
def main(ctx, daily, key):
    total_df = ctx.obj['df']
    prefix = ctx.obj['prefix']

    for name in ctx.obj['packages']:
        df = total_df[total_df.file_project == name]
        results = df.groupby(key).resample('D' if daily else 'W',
                                           on='timestamp', 
                                           loffset=datetime.timedelta(days=-6)).count()[key]
        
        print("Computing", len(df), "entries for", name, 'with', len(df[key].unique()), 'unique', key)
        results_df = results[results > 0].unstack(0).fillna(0).astype(int)

        fig, ax = plt.subplots(figsize=(12, 5))
        #ax.xaxis.set_major_locator(mpldates.YearLocator())
        #ax.xaxis.set_major_formatter(mpldates.DateFormatter('\n%y'))
        #ax.xaxis.set_minor_locator(mpldates.MonthLocator())
        #ax.xaxis.set_minor_formatter(mpldates.DateFormatter('%b'))
        fig.autofmt_xdate()
        ax.set_ylabel(f"Number of downloads per {'day' if daily else 'week'}")
        ax.set_title(name)
        # df2.groupby("weeks").sum().plot.bar(stacked=True, width=1, ax=ax)
        stacked_plot(results_df, ax, width=7)
        fname = f"{prefix}{key}_{name}.pdf"
        fig.savefig(fname)
        plt.close(fig)
        print("  Saved", fname)


@cli.command(help='Make a comparison by projects')
@click.pass_context
@click.option('--daily', is_flag=True, help='Plot daily instead of weekly')
@click.option('--key', '-k', default='file_project', help='Item to plot over, most useful is file_project (default)')
def all(ctx, daily, key):
    total_df = ctx.obj['df']
    prefix = ctx.obj['prefix']
    current_prop = prop_cycle()

    df = total_df[total_df.file_project.isin(ctx.obj['packages'])]

    results = df.groupby(key).resample('D' if daily else 'W',
                                       on='timestamp',
                                       loffset=datetime.timedelta(days=-6)).count()[key]
    print("Computing", len(df), 'entries with', len(df[key].unique()), 'unique', key)
    results_df = results[results > 0].unstack(0).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(12, 6))
    #ax.xaxis.set_major_locator(mpldates.YearLocator())
    #ax.xaxis.set_major_formatter(mpldates.DateFormatter('\n%y'))
    #ax.xaxis.set_minor_locator(mpldates.MonthLocator())
    #ax.xaxis.set_minor_formatter(mpldates.DateFormatter('%b'))
    fig.autofmt_xdate()
    ax.set_ylabel(f"Number of downloads per {'day' if daily else 'week'}")
    ax.set_title('Projects' if key is 'file_project' else key)
    stacked_plot(results_df, ax, width=7)
    fname = f"{prefix}all_{key}.pdf"
    fig.savefig(fname)
    plt.close(fig)
    print("  Saved", fname)


@cli.command(help='Make a frequency plot over a key')
@click.pass_context
@click.option('--key', '-k', default='country_code', help='Item to plot over, most useful is file_project (default)')
def freq(ctx, key):
    total_df = ctx.obj['df']
    prefix = ctx.obj['prefix']

    for name in ctx.obj['packages']:
        df = total_df[total_df.file_project == name]
        df2 = df.groupby(key).count().sort_values("timestamp")
        fig, ax = plt.subplots(figsize=(2, 5))
        df2[df2["timestamp"] > 8].plot.barh(y="timestamp", legend=False, ax=ax)
        ax.set_title(name)
        ax.set_ylabel(key)
        fname = f"{prefix}freq_{key}_{name}.pdf"
        plt.tight_layout()
        fig.savefig(fname)
        plt.close(fig)
        print("Saved", fname)


if __name__ == '__main__':
    cli(obj=dict())
