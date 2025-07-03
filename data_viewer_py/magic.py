from .viewer import _launch_data_viewer

try:
    from IPython import get_ipython
except ImportError:
    get_ipython = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import polars as pl
except ImportError:
    pl = None

use_parquet = True
try:
    import pyarrow
except ImportError:
    use_parquet = False


def launch_data_viewer_formatter(df, p, cycle):
    """
    IPython display formatter that launches the data viewer.
    """
    _launch_data_viewer(df, use_parquet=use_parquet)
    p.text(
        "[Data Viewer launched for the DataFrame. Disable with %unload_ext data_viewer_py.magic]"
    )


def load_ipython_extension(ipython):
    """
    Loads the IPython extension.
    """
    if get_ipython is None:
        raise ImportError(
            "IPython is not installed. Please install it with `pip install ipython`"
        )

    formatter = ipython.display_formatter.formatters["text/plain"]
    if pd:
        formatter.for_type(pd.DataFrame, launch_data_viewer_formatter)
    if pl:
        formatter.for_type(pl.DataFrame, launch_data_viewer_formatter)
    print(
        "Data Viewer magic enabled. Executing a DataFrame will now launch the viewer."
    )


def unload_ipython_extension(ipython):
    """
    Unloads the IPython extension.
    """
    if get_ipython is None:
        return

    formatter = ipython.display_formatter.formatters["text/plain"]
    # To unregister, we delete the type from the formatter's dictionary
    if pd and pd.DataFrame in formatter.type_printers:
        del formatter.type_printers[pd.DataFrame]
    if pl and pl.DataFrame in formatter.type_printers:
        del formatter.type_printers[pl.DataFrame]
    print("Data Viewer magic disabled.")
