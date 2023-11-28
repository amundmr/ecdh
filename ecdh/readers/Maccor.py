# -*- coding: utf-8 -*-
"""Data-readers for Maccor"""

import pandas as pd
import numpy as np
import datetime


def read_txt(filepath):
    # This reads the csv file with some extra options
    df = pd.read_csv(
        filepath,
        usecols=["Cycle", "DPT Time", "Current", "Voltage", "Capacity"],
        encoding="UTF-8",
        header=4,  # We're not using the auto header detection for this since the names have spaces.
        delimiter="\t",  # Removes the odd \t delimiters. Critical.
    )

    # Modifying time
    def convert_timestamp_to_unix_epoch(timestamp_str):
        timestamp_format = "%m/%d/%Y %H:%M:%S"
        datetime_obj = datetime.datetime.strptime(timestamp_str, timestamp_format)

        return datetime_obj.timestamp()  # Returns unix epoch float

    df["t"] = df["DPT Time"].apply(lambda x: convert_timestamp_to_unix_epoch(x))

    # Rename columns to match spec
    df.rename(
        columns={
            "Current": "I",
            "Voltage": "U",
            "Cycle": "Cycle",
        }
    )

    # Remove columns we don't want
    required_columns = ["t", "I", "U", "Cycle"]
    df = df.drop(columns=[col for col in df if col not in required_columns])

    return df
