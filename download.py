#!/usr/bin/env python3

import os
from google.cloud import bigquery
import click

@click.command()
@click.option('--credentials', '-c', type=click.Path(exists=True), help='Path to your google API key, json file')
@click.option('--output', '-o', type=click.Path(exists=False), help='Output file (defaults to scikit-hep-FROM-TO.csv)')
@click.option('--from', '-f', 'from_', default='20190531', show_default=True, help='From date')
@click.option('--to', '-t', default='20250101', show_default=True, help='To date')
def main(credentials, output, from_, to):
    if credentials is not None:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials

    if output is None:
        output = 'scikit-hep-{from_}-{to}.csv'.format(from_=from_, to=to)

    client = bigquery.Client()
    sql = """
    SELECT
      timestamp,
      country_code,
      file.project AS file_project,
      file.version AS file_version,
      file.type AS file_type,
      details.installer.version AS details_installer_version,
      details.python AS details_python,
      details.distro.name AS details_distro_name,
      details.distro.version AS details_distro_version,
      details.distro.libc.version AS details_distro_libc_version,
      details.system.name AS details_system_name,
      details.system.release AS details_system_release,
      details.cpu AS details_cpu,
      details.openssl_version AS details_openssl_version,
      details.setuptools_version AS details_setuptools_version
    FROM `the-psf.pypi.downloads*`
    WHERE
      _TABLE_SUFFIX BETWEEN '{from_}' AND '{to}'
      AND details.installer.name = 'pip'
      AND file.project IN (
        'aghast',
        'awkward',
        'awkward0',
        'awkward1',
        'boost-histogram',
        'decaylanguage',
        'excursion',
        'formulate',
        'hepstats',
        'hepunits',
        'hist',
        'histoprint',
        'iminuit',
        'madminer',
        'mplhep',
        'numpythia',
        'particle',
        'probfit',
        'pyBumpHunter',
        'pyhf',
        'pyjet',
        'pylhe',
        'reana-client',
        'root-numpy',
        'root-pandas',
        'rootpy',
        'scikit-hep',
        'scikit-hep-testdata',
        'scikit-optimize',
        'uhi',
        'uproot',
        'uproot3',
        'uproot4',
        'uproot-methods',
        'uproot3-methods',
        'vector',
        'vegascope',
        'yadage'
      )
    """.format(from_=from_, to=to)

    # Run a Standard SQL query using the environment's default project
    df = client.query(sql).to_dataframe()
    df.to_csv(output, index=False)

if __name__ == '__main__':
    main()
