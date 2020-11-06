# Statistics aggregator for the Scikit-HEP packages

This is an admin-focused repository collecting scripts and material to look at
statistics for the org packages.
The present tools collect and display the [PyPI](https://pypi.org/) statistics of all org packages.

Rendered Jupyter notebooks for Python 2 vs. 3: [Table][] and [Plot][].

[Table]: https://nbviewer.jupyter.org/github/scikit-hep/scikit-hep-orgstats/blob/master/Python2vs3.ipynb
[Plot]: https://nbviewer.jupyter.org/github/scikit-hep/scikit-hep-orgstats/blob/master/Python2vs3Plot.ipynb

## Setup

Warning: grabbing the last 2-3 years of data can use about $50 in cloud credits.
The Google Big Query script is best run in a virtual environment:

```bash
python3 -m venv .env
. .env/bin/activate
pip install -r requirements.txt
```
You will have to set up your credentials as described [here](https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python) or [here](https://googleapis.github.io/google-cloud-python/latest/bigquery/index.html).


## Download

Then, you can run the download script:

```bash
./download.py -c ~/google-api-key.json
```
(Either set `GOOGLE_APPLICATION_CREDENTIALS` or use the parameter shown above to set your API key file.)

You can use `./download.py --help` to see options.

Each package release contains the latest snapshots attached, which can be used
to run several analyses, see below.
Refer to the [releases page](https://github.com/scikit-hep/scikit-hep-orgstats/releases).

## Analyze

You can run `./plot.py` to produce the final plots. Use `--help` to see usage instructions:

```
./plot.py --help
Usage: plot.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...

Options:
  -f, --filename FILENAME    Files to read in (defaults to all CSVs)
  -n, --name TEXT            Add prefix to all plots
  -m, --minor                Use minor version too
  -p, --package TEXT         Select only one package instead of all
  -x, --filter-package TEXT  Remove package(s) from package list
  --unique                   Filter based on OS "uniqueness"
  --filter <TEXT TEXT>...    Filter based on KEY VALUE
  --help                     Show this message and exit.

Commands:
  all   Make a comparison by projects
  freq  Make a frequency plot over a key
  main  Make a weekly or daily downloads plot
```

You can run multiple commands and often give options multiple times.
`main`, `freq`, and `all`, support `--key KEY`, though they choose a nice default.
The two "per-week" plots also support a `--daily` flag to change weekly into daily statistics.

Most of the commands don't do much to generate a custom name if you change options, so you can use the `--name` option to set a prefix.
If you want minor versions to not be combined with major ones, pass `--minor`.
You can list multiple `--package NAME` and `--filename NAME` options; otherwise they default to all.

Example:

```bash
./plot.py --name 20190429_ -x scikit-optimize all main freq
```

Filtering on only Switzerland:

```bash
./plot.py -n CH_ -x uproot -x uproot-methods -x awkward -x root-pandas --filter country_code CH all
```

To look at packages pre-dating the Scikit-HEP project and compare with the `uproot` series:

```bash
./plot.py \
  -p iminuit -p rootpy \
  -p root_numpy -p root_pandas \
  -p uproot \
  -p uproot4 \
  all
```

```bash
./plot.py \
  -p pyjet \
  -p particle \
  -p hepunits \
  -p numpythia \
  -p decaylanguage \
  all
```
