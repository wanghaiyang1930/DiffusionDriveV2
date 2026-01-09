"""
@brief: test logging functions.
@author: wanghaiyang
@date: 2026-01-09
"""

import unittest
import logging
import sys

class TestLogging(unittest.TestCase):
    """Test the logging functions."""

    def setUp(self):
        """Set up logging configuration for each test."""

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.StreamHandler(sys.stdout)  # 输出到终端
            ],
            force=True  # 强制重新配置，覆盖之前的配置
        )

    def test_logging(self):
        """Test the logging functions."""
        logging.info("This is a test logging message.")
        logging.warning("This is a test warning message.")
        logging.error("This is a test error message.")
        logging.debug("This is a test debug message.")

# export PYTHONPATH=$PWD:$PYTHONPATH
# python -m pytest test/basic/test_logging.py -v -s  # -s flag disables output capturing
if __name__ == "__main__":
    unittest.main()