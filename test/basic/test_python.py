"""
@brief: test basic grammar of python.
@author: wanghaiyang
@date: 2026-01-09
"""

import unittest

class TestBasicGrammar(unittest.TestCase):
    """Test the basic grammar of python."""

    def test_basic_grammar(self):
        """Test the basic grammar of python."""

        raw_list = range(10)
        print(f"[TestBasicGrammar] [test_basic_grammar] raw_list: {raw_list}")
        skop_list = [i for i in range(0, len(raw_list), 3)]
        print(f"[TestBasicGrammar] [test_basic_grammar] skop_list: {skop_list}")

        
# export PYTHONPATH=$PWD:$PYTHONPATH
# python -m pytest test/basic/test_python.py -v -s  # -s flag disables output capturing
if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=False)  # buffer=False allows print output