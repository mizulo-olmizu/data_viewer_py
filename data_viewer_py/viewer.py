from typing import Union, Optional, Any
import subprocess
import tempfile
import requests
import time

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pyarrow
except ImportError:
    pyarrow = None


def _launch_data_viewer(
    self: Any,
    name: Optional[str] = None,
    use_parquet: bool = False,
    port: int = 3000,
    timeout: Union[int, float] = 3,
    infer_schema_length: Optional[Union[str, int, float]] = None,
    app_path: str = "/Applications/data_viewer.app/Contents/MacOS/data_viewer",
) -> None:
    if infer_schema_length is not None:
        if not (
            infer_schema_length == "Inf"
            or (isinstance(infer_schema_length, (int, float)) and infer_schema_length >= 0)
        ):
            raise ValueError(
                "infer_schema_length must be 'Inf' or a non-negative integer."
            )

    is_pandas = pd is not None and isinstance(self, pd.DataFrame)
    is_polars = pl is not None and isinstance(self, pl.DataFrame)

    if not is_pandas and not is_polars:
        raise TypeError(
            "The 'view' method is only available for pandas or polars DataFrames."
        )

    # Determine name if not provided
    if name is None:
        name = self.__class__.__name__

    # Create temporary file
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=".parquet" if use_parquet else ".csv"
    ) as temp_file:
        temp_file_path = temp_file.name

        if use_parquet:
            if pyarrow is None:
                raise ImportError(
                    "pyarrow is not installed. Please install it with `pip install data-viewer-py[arrow]`"
                )
            if is_pandas:
                self.to_parquet(temp_file_path)
            else:
                self.write_parquet(temp_file_path)
        else:
            if is_pandas:
                self.to_csv(temp_file_path, index=False)
            else:
                self.write_csv(temp_file_path)

        health_check_url = f"http://127.0.0.1:{port}/health-check"
        update_data_url = f"http://127.0.0.1:{port}/update-data"

        def health_check():
            response = requests.get(health_check_url)
            response.raise_for_status()

        def update_data():
            json_data = {"input": temp_file_path}
            if name is not None:
                json_data["name"] = name
            if infer_schema_length is not None:
                json_data["infer_schema_length"] = str(infer_schema_length)
            response = requests.post(update_data_url, json=json_data)
            return response

        try:
            health_check()
        except requests.RequestException:
            subprocess.Popen(
                [app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    health_check()
                    break
                except requests.RequestException:
                    time.sleep(0.1)
            else:
                raise RuntimeError(
                    f"Data Viewer application failed to start within {timeout} seconds."
                )

        # Update data
        update_data_response = update_data()
        print(update_data_response.text)

        if update_data_response.status_code != 200:
            raise RuntimeError(f"Failed to update data. {update_data_response.json()}")