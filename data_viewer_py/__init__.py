from .viewer import _launch_data_viewer

try:
    import pandas as pd
    pd.DataFrame.launch_data_viewer = _launch_data_viewer
except ImportError:
    pass

try:
    import polars as pl
    pl.DataFrame.launch_data_viewer = _launch_data_viewer
except ImportError:
    pass
