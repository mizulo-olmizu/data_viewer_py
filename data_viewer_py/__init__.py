from .viewer import _launch_data_viewer
import pandas as pd
import polars as pl

pd.DataFrame.launch_data_viewer = _launch_data_viewer
pl.DataFrame.launch_data_viewer = _launch_data_viewer
