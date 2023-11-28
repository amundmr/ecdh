import unittest
import pytest
import pandas as pd
from ecdh.readers import maccor
import os


class TestMaccor(unittest.TestCase):
    def test_read_txt_with_valid_datafile(self):
        data_file_path = os.path.join(
            os.path.dirname(__file__), "test_data", "maccor.txt"
        )
        df = maccor.read_txt(data_file_path)

        self.assertIsInstance(df, pd.DataFrame)
        # self.assertEqual(df.shape, (10, 10))

        print(df.columns)
        print(df.head)


if __name__ == "__main__":
    unittest.main()
