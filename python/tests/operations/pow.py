import os

import numpy as np
import pytest

import equistore
from equistore import Labels, TensorBlock, TensorMap


DATA_ROOT = os.path.join(os.path.dirname(__file__), "..", "data")


class TestPow:
    def test_self_pow_scalar_gradient(self):
        b1_s0 = np.array([1, 2])
        b1_s2 = np.array([3, 5])

        b1grad_s01 = np.array([[6, 1], [7, 2]])
        b1grad_s11 = np.array([[8, 3], [9, 4]])

        b2_s0 = np.array([11, 12])
        b2_s2 = np.array([13, 14])
        b2_s7 = np.array([15, 16])

        b2grad_s01 = np.array([[10, 11], [12, 13]])
        b2grad_s11 = np.array([[14, 15], [10, 11]])
        b2grad_s21 = np.array([[12, 13], [14, 15]])

        block_1 = TensorBlock(
            values=np.vstack([b1_s0, b1_s2]),
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_1.add_gradient(
            "parameter",
            data=np.vstack([[b1grad_s01], [b1grad_s11]]),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )
        block_2 = TensorBlock(
            values=np.vstack([b2_s0, b2_s2, b2_s7]),
            samples=Labels(["samples"], np.array([[0], [2], [7]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_2.add_gradient(
            "parameter",
            data=np.vstack([[b2grad_s01], [b2grad_s11], [b2grad_s21]]),
            samples=Labels(
                ["sample", "positions"],
                np.array([[0, 1], [1, 1], [2, 1]], dtype=np.int32),
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )

        keys = Labels(
            names=["key_1", "key_2"], values=np.array([[0, 0], [1, 0]], dtype=np.int32)
        )

        B = 2
        rvalues1 = block_1.values[:] ** B
        rvalues2 = block_2.values[:] ** B
        A = TensorMap(keys, [block_1, block_2])
        A_copy = A.copy()

        block_res1 = TensorBlock(
            values=rvalues1,
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_res1.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [B * b1grad_s01 * (b1_s0 ** (B - 1))],
                    [B * b1grad_s11 * (b1_s2 ** (B - 1))],
                ]
            ),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )
        block_res2 = TensorBlock(
            values=rvalues2,
            samples=Labels(["samples"], np.array([[0], [2], [7]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_res2.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [B * b2grad_s01 * (b2_s0 ** (B - 1))],
                    [B * b2grad_s11 * (b2_s2 ** (B - 1))],
                    [B * b2grad_s21 * (b2_s7 ** (B - 1))],
                ]
            ),
            samples=Labels(
                ["sample", "positions"],
                np.array([[0, 1], [1, 1], [2, 1]], dtype=np.int32),
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )

        keys = Labels(
            names=["key_1", "key_2"], values=np.array([[0, 0], [1, 0]], dtype=np.int32)
        )

        C = np.array([2.0])

        tensor_sum = equistore.pow(A, B)
        tensor_sum_array = equistore.pow(A, C)
        tensor_result = TensorMap(keys, [block_res1, block_res2])

        assert equistore.allclose(tensor_result, tensor_sum)
        assert equistore.allclose(tensor_result, tensor_sum_array)
        # Check not modified in place
        assert equistore.equal(A, A_copy)

    def test_self_pow_components_scalar_gradient(self):
        b1_s0_c00 = np.array([1, 2])
        b1_s2_c01 = np.array([3, 5])
        b1_s0_c10 = np.array([1.1, 2.2])
        b1_s2_c11 = np.array([3.3, 5.5])

        b1grad_s01_c00 = np.array([6, 1])
        b1grad_s11_c01 = np.array([8, 3])
        b1grad_s01_c10 = np.array([7.1, 2.1])
        b1grad_s11_c11 = np.array([9.1, 4.1])

        block_1 = TensorBlock(
            values=np.vstack(
                [
                    [[[b1_s0_c00], [b1_s2_c01]], [[b1_s0_c10], [b1_s2_c11]]],
                ]
            ),
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[
                Labels(["component1"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component2"], np.array([[0]], dtype=np.int32)),
            ],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )

        block_1.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [
                        [
                            [[b1grad_s01_c00], [b1grad_s01_c10]],
                            [[b1grad_s01_c00 + 6], [b1grad_s01_c10 + 3.1]],
                        ],
                        [
                            [[b1grad_s11_c01 + 4.1], [b1grad_s11_c11 + 6.8]],
                            [[b1grad_s11_c01], [b1grad_s11_c11]],
                        ],
                    ],
                ]
            ),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["grad_components"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component1"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component2"], np.array([[0]], dtype=np.int32)),
            ],
        )

        keys = Labels(names=["key_1"], values=np.array([[0]], dtype=np.int32))

        B = 2
        rvalues1 = block_1.values[:] ** B
        A = TensorMap(keys, [block_1])

        block_res1 = TensorBlock(
            values=rvalues1,
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[
                Labels(["component1"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component2"], np.array([[0]], dtype=np.int32)),
            ],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_res1.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [
                        [
                            [
                                [B * b1grad_s01_c00 * (b1_s0_c00 ** (B - 1))],
                                [B * b1grad_s01_c10 * (b1_s2_c01 ** (B - 1))],
                            ],
                            [
                                [B * (b1grad_s01_c00 + 6) * (b1_s0_c00 ** (B - 1))],
                                [B * (b1grad_s01_c10 + 3.1) * (b1_s2_c01 ** (B - 1))],
                            ],
                        ]
                    ],
                    [
                        [
                            [
                                [B * (b1grad_s11_c01 + 4.1) * (b1_s0_c10 ** (B - 1))],
                                [B * (b1grad_s11_c11 + 6.8) * (b1_s2_c11 ** (B - 1))],
                            ],
                            [
                                [B * b1grad_s11_c01 * (b1_s0_c10 ** (B - 1))],
                                [B * b1grad_s11_c11 * (b1_s2_c11 ** (B - 1))],
                            ],
                        ]
                    ],
                ]
            ),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["grad_components"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component1"], np.array([[0], [1]], dtype=np.int32)),
                Labels(["component2"], np.array([[0]], dtype=np.int32)),
            ],
        )
        keys = Labels(names=["key_1"], values=np.array([[0]], dtype=np.int32))

        C = np.array([2.0])

        tensor_pow = equistore.pow(A, B)
        tensor_pow_array = equistore.pow(A, C)
        tensor_result = TensorMap(keys, [block_res1])

        assert equistore.allclose(tensor_result, tensor_pow)
        assert equistore.allclose(tensor_result, tensor_pow_array)

    def test_self_pow_scalar_sqrt_gradient(self):
        b1_s0 = np.array([1, 2])
        b1_s2 = np.array([4.7, 7])

        b1grad_s01 = np.array([[6, 1], [7, 2]])
        b1grad_s11 = np.array([[8, 3], [9, 4]])

        b2_s0 = np.array([11, 12])
        b2_s2 = np.array([13, 14])
        b2_s7 = np.array([0.15, 1.6])

        b2grad_s01 = np.array([[10.6, 11], [1.2, 13]])
        b2grad_s11 = np.array([[14, 1.5], [10, 11]])
        b2grad_s21 = np.array([[12, 13.2], [14, 15]])

        block_1 = TensorBlock(
            values=np.vstack([b1_s0, b1_s2]),
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_1.add_gradient(
            "parameter",
            data=np.vstack([[b1grad_s01], [b1grad_s11]]),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )
        block_2 = TensorBlock(
            values=np.vstack([b2_s0, b2_s2, b2_s7]),
            samples=Labels(["samples"], np.array([[0], [2], [7]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_2.add_gradient(
            "parameter",
            data=np.vstack([[b2grad_s01], [b2grad_s11], [b2grad_s21]]),
            samples=Labels(
                ["sample", "positions"],
                np.array([[0, 1], [1, 1], [2, 1]], dtype=np.int32),
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )

        keys = Labels(
            names=["key_1", "key_2"], values=np.array([[0, 0], [1, 0]], dtype=np.int32)
        )

        B = 0.5
        rvalues1 = np.sqrt(block_1.values[:])
        rvalues2 = np.sqrt(block_2.values[:])
        A = TensorMap(keys, [block_1, block_2])

        block_res1 = TensorBlock(
            values=rvalues1,
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_res1.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [B * b1grad_s01 * (b1_s0 ** (B - 1))],
                    [B * b1grad_s11 * (b1_s2 ** (B - 1))],
                ]
            ),
            samples=Labels(
                ["sample", "positions"], np.array([[0, 1], [1, 1]], dtype=np.int32)
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )
        block_res2 = TensorBlock(
            values=rvalues2,
            samples=Labels(["samples"], np.array([[0], [2], [7]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        block_res2.add_gradient(
            "parameter",
            data=np.vstack(
                [
                    [B * b2grad_s01 * (b2_s0 ** (B - 1))],
                    [B * b2grad_s11 * (b2_s2 ** (B - 1))],
                    [B * b2grad_s21 * (b2_s7 ** (B - 1))],
                ]
            ),
            samples=Labels(
                ["sample", "positions"],
                np.array([[0, 1], [1, 1], [2, 1]], dtype=np.int32),
            ),
            components=[
                Labels(["components"], np.array([[0], [1]], dtype=np.int32)),
            ],
        )

        keys = Labels(
            names=["key_1", "key_2"], values=np.array([[0, 0], [1, 0]], dtype=np.int32)
        )

        C = np.array([0.5])

        tensor_sum = equistore.pow(A, B)
        tensor_sum_array = equistore.pow(A, C)
        tensor_result = TensorMap(keys, [block_res1, block_res2])

        assert equistore.allclose(tensor_result, tensor_sum)
        assert equistore.allclose(tensor_result, tensor_sum_array)

    def test_self_pow_error(self):
        block_1 = TensorBlock(
            values=np.array([[1, 2], [3, 5]]),
            samples=Labels(["samples"], np.array([[0], [2]], dtype=np.int32)),
            components=[],
            properties=Labels(["properties"], np.array([[0], [1]], dtype=np.int32)),
        )
        keys = Labels(
            names=["key_1", "key_2"], values=np.array([[0, 0]], dtype=np.int32)
        )
        A = TensorMap(keys, [block_1])
        B = np.ones((3, 4))

        with pytest.raises(TypeError, match="B should be a scalar value. "):
            keys = equistore.pow(A, B)


# TODO: pow tests with torch & torch scripting/tracing
