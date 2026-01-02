"""
Unit tests for dict_to_device function.
@brief: test the dict_to_device function in transfuser_callback.py
@author: wanghaiyang
@date: 2026-01-01
"""

import unittest
import torch
from typing import Dict, Union
from collections.abc import Mapping

from navsim.agents.diffusiondrivev2.transfuser_callback import dict_to_device


class TestDictToDevice(unittest.TestCase):
    """Unit tests for dict_to_device function."""

    def test_simple_dict(self):
        """Test moving a simple dictionary with tensors to device."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'tensor1': torch.tensor([1.0, 2.0, 3.0]),
            'tensor2': torch.tensor([[1.0, 2.0], [3.0, 4.0]]),
        }
        
        result = dict_to_device(data, device)
        
        self.assertEqual(result['tensor1'].device, device)
        self.assertEqual(result['tensor2'].device, device)
        self.assertTrue(torch.equal(result['tensor1'], data['tensor1']))
        self.assertTrue(torch.equal(result['tensor2'], data['tensor2']))

    def test_nested_dict(self):
        """Test moving a nested dictionary with tensors to device."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'level1': {
                'tensor1': torch.tensor([1.0, 2.0]),
                'tensor2': torch.tensor([3.0, 4.0]),
            },
            'tensor3': torch.tensor([5.0, 6.0]),
        }
        
        result = dict_to_device(data, device)
        
        self.assertEqual(result['level1']['tensor1'].device, device)
        self.assertEqual(result['level1']['tensor2'].device, device)
        self.assertEqual(result['tensor3'].device, device)
        self.assertTrue(torch.equal(result['level1']['tensor1'], data['level1']['tensor1']))
        self.assertTrue(torch.equal(result['level1']['tensor2'], data['level1']['tensor2']))
        self.assertTrue(torch.equal(result['tensor3'], data['tensor3']))

    def test_deeply_nested_dict(self):
        """Test moving a deeply nested dictionary with tensors to device."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'level1': {
                'level2': {
                    'level3': {
                        'tensor1': torch.tensor([1.0]),
                    },
                    'tensor2': torch.tensor([2.0]),
                },
                'tensor3': torch.tensor([3.0]),
            },
            'tensor4': torch.tensor([4.0]),
        }
        
        result = dict_to_device(data, device)
        
        self.assertEqual(result['level1']['level2']['level3']['tensor1'].device, device)
        self.assertEqual(result['level1']['level2']['tensor2'].device, device)
        self.assertEqual(result['level1']['tensor3'].device, device)
        self.assertEqual(result['tensor4'].device, device)

    def test_empty_dict(self):
        """Test moving an empty dictionary to device."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {}
        
        result = dict_to_device(data, device)
        
        self.assertEqual(result, {})
        self.assertIsInstance(result, dict)

    def test_nested_empty_dict(self):
        """Test moving a dictionary with nested empty dictionaries."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'empty1': {},
            'empty2': {
                'empty3': {},
            },
            'tensor1': torch.tensor([1.0]),
        }
        
        result = dict_to_device(data, device)
        
        self.assertEqual(result['empty1'], {})
        self.assertEqual(result['empty2']['empty3'], {})
        self.assertEqual(result['tensor1'].device, device)

    def test_device_string(self):
        """Test moving tensors using device string instead of device object."""
        if torch.cuda.is_available():
            device_str = 'cuda:0'
        else:
            device_str = 'cpu'
        
        data = {
            'tensor1': torch.tensor([1.0, 2.0]),
            'nested': {
                'tensor2': torch.tensor([3.0, 4.0]),
            },
        }
        
        result = dict_to_device(data, device_str)
        
        expected_device = torch.device(device_str)
        self.assertEqual(result['tensor1'].device, expected_device)
        self.assertEqual(result['nested']['tensor2'].device, expected_device)

    def test_cpu_to_cuda(self):
        """Test moving tensors from CPU to CUDA if available."""
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")
        
        data = {
            'tensor1': torch.tensor([1.0, 2.0]).to('cpu'),
            'nested': {
                'tensor2': torch.tensor([3.0, 4.0]).to('cpu'),
            },
        }
        
        result = dict_to_device(data, 'cuda:0')
        
        self.assertEqual(result['tensor1'].device.type, 'cuda')
        self.assertEqual(result['nested']['tensor2'].device.type, 'cuda')

    def test_preserves_structure(self):
        """Test that the function preserves the dictionary structure."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'a': torch.tensor([1.0]),
            'b': {
                'c': torch.tensor([2.0]),
                'd': {
                    'e': torch.tensor([3.0]),
                },
            },
        }
        
        result = dict_to_device(data, device)
        
        # Check structure is preserved
        self.assertIn('a', result)
        self.assertIn('b', result)
        self.assertIn('c', result['b'])
        self.assertIn('d', result['b'])
        self.assertIn('e', result['b']['d'])
        
        # Check all tensors are on correct device
        self.assertEqual(result['a'].device, device)
        self.assertEqual(result['b']['c'].device, device)
        self.assertEqual(result['b']['d']['e'].device, device)

    def test_multiple_tensors_same_level(self):
        """Test dictionary with multiple tensors at the same level."""
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        data = {
            'tensor1': torch.tensor([1.0]),
            'tensor2': torch.tensor([2.0]),
            'tensor3': torch.tensor([3.0]),
            'tensor4': torch.tensor([4.0]),
        }
        
        result = dict_to_device(data, device)
        
        for key in ['tensor1', 'tensor2', 'tensor3', 'tensor4']:
            self.assertEqual(result[key].device, device)
            self.assertTrue(torch.equal(result[key], data[key]))

    def test_real_data_v0(self):
        tensor_data = torch.randn([3, 4]).to('cuda')
        dict_data = {'coarse_reward': tensor_data, 'fine_reward_0': tensor_data}

        device = 'cpu'
        result = dict_to_device(dict_data, device)

        self.assertEqual(result['coarse_reward'].device, torch.device(device))
        self.assertEqual(result['fine_reward_0'].device, torch.device(device))
        self.assertTrue(torch.equal(result['coarse_reward'], dict_data['coarse_reward']))
        self.assertTrue(torch.equal(result['fine_reward_0'], dict_data['fine_reward_0']))

# export PYTHONPATH=$PWD:$PYTHONPATH
# python -m pytest test/test_basic_function.py -v
if __name__ == '__main__':
    unittest.main()
