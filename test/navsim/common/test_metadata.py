"""
@brief: test the metadata data.
@author: wanghaiyang
@date: 2026-01-09
"""

import os
import sys
import logging
import unittest
import pickle

class TestMetadata(unittest.TestCase):
    """Test the metadata data."""

    def setUp(self):
        """Set up logging configuration for each test."""

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
            force=True
        )

    def test_metadata(self):
        """Test the metadata data."""
        
        pkl_path = "/home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl"
        # if pickle file is not exist, just return.
        if not os.path.exists(pkl_path):
            logging.error(f"Pickle file {pkl_path} does not exist.")
            return
        
        # read a pickle file
        with open(pkl_path, 'rb') as f:
            pkl_data = pickle.load(f)

        logging.info(f"Pickle data lenght:: {len(pkl_data)}")

        self.assertNotEqual(len(pkl_data), 0, "Pickle data length should not be 0.")
        
        # Print the first 5 elements of the pkl_data.
        # logging.info(f"Pickle data the first elements: {pkl_data[0]}")

        data_type = type(pkl_data[0])
        logging.info(f"Pickle element type: {data_type.__name__}")
        logging.info(f"Pickle elemen module: {data_type.__module__}")

        if isinstance(pkl_data[0], dict):
            logging.info(f"Pickle element keys: {pkl_data[0].keys()}")
    
        # Print every key and value of the first element in a single line.
        for key, value in pkl_data[0].items():
            logging.info(f"Pickle first element: {key}: {value}")

    def test_metadata_driving_command(self):
        """Test the driving command data."""

        pkl_path = "/home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl"
        # if pickle file is not exist, just return.
        if not os.path.exists(pkl_path):
            logging.error(f"Pickle file {pkl_path} does not exist.")
            return
        
        # read a pickle file
        with open(pkl_path, 'rb') as f:
            pkl_data = pickle.load(f)

        logging.info(f"Pickle data lenght:: {len(pkl_data)}")

        self.assertNotEqual(len(pkl_data), 0, "Pickle data length should not be 0.")
        
        # Print this driving_command data for each element in the pkl_data.
        for element in pkl_data:
            logging.info(f"Pickle driving command: {element['driving_command']}")

    def test_metadata_frame_idx(self):
        """Test the frame index data."""

        pkl_path = "/home/data/navsim/dataset/navsim_logs/mini/2021.10.11.08.31.07_veh-50_01750_01948.pkl"
        # if pickle file is not exist, just return.
        if not os.path.exists(pkl_path):
            logging.error(f"Pickle file {pkl_path} does not exist.")
            return
        
        # read a pickle file
        with open(pkl_path, 'rb') as f:
            pkl_data = pickle.load(f)

        logging.info(f"Pickle data lenght:: {len(pkl_data)}")

        self.assertNotEqual(len(pkl_data), 0, "Pickle data length should not be 0.")
        
        # Print the frame index data for each element in the pkl_data.
        for element in pkl_data:
            logging.info(f"Pickle frame index: {element['frame_idx']}")

# export PYTHONPATH=$PWD:$PYTHONPATH
# python -m pytest test/navsim/common/test_metadata.py -v -s  # -s flag disables output capturing
if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=False)  # buffer=False allows print/logging output
