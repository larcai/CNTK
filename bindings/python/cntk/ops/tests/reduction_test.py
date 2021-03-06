# Copyright (c) Microsoft. All rights reserved.

# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================

"""
Unit tests for reduction operations, tested for the forward and the backward pass
"""

from __future__ import division
import numpy as np
import pytest
from .ops_test_utils import unittest_helper, _test_unary_op, AA, I, precision, PRECISION_TO_TYPE, constant
from ...utils import sanitize_dtype_cntk

REDUCE_TEST_OPERANDS = [
    #(input_data,  axis)
    ([[1]], 0),
    ([[1,2],[4,5]], 0),
    ([[1,2],[4,5]], 1),
    ([[1,2],[4,5]], -1),
    ([[[1,2],[3,4]],[[5,6],[7,8]]], -2),
    ([[[1,2],[3,4]],[[5,6],[7,8]]], 2),
]

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_sum(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    expected_forward = [[np.sum(data, axis=(axis), keepdims=True)]]

    backward = np.ones_like(data)

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_sum
    _test_unary_op(precision, device_id, reduce_sum, input_data,
                   expected_forward, expected_backward, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_max(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    expected_forward = [[np.amax(data, axis=(axis), keepdims=True)]]

    forward_array = np.asarray(expected_forward, dtype=dt)
    max_elements = forward_array.reshape(forward_array.size).tolist()

    # place 1.0s where maximum elements are
    backward = np.zeros_like(data)
    for element in max_elements:
        backward += np.asarray(data == element)

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_max
    _test_unary_op(precision, device_id, reduce_max, input_data,
                   expected_forward, expected_backward, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_min(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    expected_forward = [[np.amin(data, axis=(axis), keepdims=True)]]

    forward_array = np.asarray(expected_forward, dtype=dt)
    max_elements = forward_array.reshape(forward_array.size).tolist()

    # place 1.0s where maximum elements are
    backward = np.zeros_like(data)
    for element in max_elements:
        backward += np.asarray(data == element)

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_min
    _test_unary_op(precision, device_id, reduce_min, input_data,
                   expected_forward, expected_backward, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_mean(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    expected_forward = [[np.mean(data, axis=(axis), keepdims=True)]]

    backward = np.ones_like(data) / data.shape[axis]

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_mean
    _test_unary_op(precision, device_id, reduce_mean, input_data,
                   expected_forward, expected_backward, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_mean(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    expected_forward = [[np.mean(data, axis=(axis), keepdims=True)]]

    backward = np.ones_like(data) / data.shape[axis]

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_mean
    _test_unary_op(precision, device_id, reduce_mean, input_data,
                   expected_forward, expected_backward, {'axis': axis})


@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_log_sum(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    data_exp = np.exp(data)
    sum_exp = np.sum(data_exp, axis=(axis), keepdims=True)
    expected_forward = [[np.log(sum_exp)]]

    backward = data_exp / sum_exp

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_log_sum_exp
    _test_unary_op(precision, device_id, reduce_log_sum_exp, input_data,
                   expected_forward, expected_backward, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_prod(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    p = np.prod(data, axis=(axis), keepdims=True)
    expected_forward = [[p]]

    backward = p / data

    expected_backward = {
        'arg': [[backward]]
    }

    from .. import reduce_prod
    _test_unary_op(precision, device_id, reduce_prod, input_data,
                   expected_forward, expected_backward, {'axis': axis})
                   
@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_all(input_data, axis, device_id, precision):
    # FIXME: we'd like to do dt = PRECISION_TO_TYPE[precision]
    # however there seems to be an issue with actual_forward below
    # that gets computed correctly but by the time np.allclose executes
    # it contains garbage values. The problem goes away if one uses 
    # actual_forward  = np.copy(input_op.eval(binding))
    dt = np.float32
    data = AA(input_data, dtype=dt)
    a = I(shape=data.shape,
          dtype=sanitize_dtype_cntk(dt),
          needs_gradient=True,
          name='a')
    # create batch
    value = [AA([data,data-0.5], dtype=dt),AA([data+0.25], dtype=dt)]
    from .. import reduce_sum, reduce_max, reduce_min, reduce_mean, reduce_log_sum_exp, reduce_prod
    from cntk import Axis
    def max_bwd(x,f):
        y = np.zeros_like(x)
        yr = y.ravel()
        xr = x.ravel()
        for i in range(x.size):
            if xr[i] == f: yr[i] = 1
        return y

    ops = [ (reduce_sum,         lambda x:AA(sum(np.sum(xi) for xi in x)),                           lambda x,f:[np.ones_like(xi) for xi in x]),
            (reduce_max,         lambda x:AA(max(np.max(xi) for xi in x)),                           lambda x,f:[max_bwd(xi,f) for xi in x]),
            (reduce_min,         lambda x:AA(min(np.min(xi) for xi in x)),                           lambda x,f:[max_bwd(xi,f) for xi in x]),
            (reduce_mean,        lambda x:AA(sum(np.sum(xi) for xi in x)/sum(xi.size  for xi in x)), lambda x,f:[np.ones_like(xi)/sum(xj.size for xj in x) for xi in x]),
            (reduce_log_sum_exp, lambda x:AA(np.log(sum(np.sum(np.exp(xi)) for xi in x))),           lambda x,f:[np.exp(xi-f)     for xi in x]),
            (reduce_prod,        lambda x:AA(np.prod([np.prod(xi) for xi in x])),                    lambda x,f:[f/xi             for xi in x])
            ]
    
    for op,fwd,bwd in ops:
        input_op = op(a, axis=Axis.all_axes())
        expected_forward = fwd(value)
        expected_backward = bwd(value,expected_forward)
        binding = {a: value}
        actual_backward = input_op.grad(binding)[0]
        actual_forward  = np.copy(input_op.eval(binding))
        assert np.allclose(actual_forward, expected_forward)
        for ab,eb in zip (actual_backward, expected_backward):
            assert np.allclose(ab, eb)

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_mean_all_constant(input_data, axis, device_id, precision):
    # dt = PRECISION_TO_TYPE[precision]
    # FIXME: we'd like to do dt = PRECISION_TO_TYPE[precision]
    # however there seems to be an issue with actual_forward below
    # that gets computed correctly but by the time np.allclose executes
    # it contains garbage values. The problem goes away if one uses 
    # actual_forward  = np.copy(input_op.eval())
    dt = np.float32
    value = AA(input_data, dtype=dt)
    from .. import reduce_mean
    from cntk import Axis, Constant
    a = Constant(value, name='a')
    input_op = reduce_mean(a, axis=Axis.all_axes())
    expected_forward = AA(np.mean(value))
    actual_forward  = input_op.eval()
    assert np.allclose(actual_forward, expected_forward)

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_argmax(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    # numpy argmax doesn't support keepdims
    arg_shape = np.amax(data, axis=(axis), keepdims=True).shape
    expected_forward = [[np.argmax(data, axis=(axis)).reshape(arg_shape)]]

    from .. import argmax
    _test_unary_op(precision, device_id, argmax, input_data,
                   expected_forward, None, {'axis': axis})

@pytest.mark.parametrize("input_data, axis", REDUCE_TEST_OPERANDS)
def test_op_reduce_argmin(input_data, axis, device_id, precision):
    dt = PRECISION_TO_TYPE[precision]

    data = AA(input_data, dtype=dt)

    # numpy argmin doesn't support keepdims
    arg_shape = np.amin(data, axis=(axis), keepdims=True).shape
    expected_forward = [[np.argmin(data, axis=(axis)).reshape(arg_shape)]]

    from .. import argmin
    _test_unary_op(precision, device_id, argmin, input_data,
                   expected_forward, None, {'axis': axis})
