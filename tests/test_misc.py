import jax
import jax.numpy as jnp
import optimistix._misc as optx_misc
import pytest

from .helpers import (
    tree_allclose,
    tree_where__pred_true_false_expected,
    trees_to_clip,
    y_bounds_step_offset_expected,
)


def test_inexact_asarray_no_copy():
    x = jnp.array([1.0])
    assert optx_misc.inexact_asarray(x) is x
    y = jnp.array([1.0, 2.0])
    assert jax.vmap(optx_misc.inexact_asarray)(y) is y


# See JAX issue #15676
def test_inexact_asarray_jvp():
    p, t = jax.jvp(optx_misc.inexact_asarray, (1.0,), (2.0,))
    assert type(p) is not float
    assert type(t) is not float


@pytest.mark.parametrize("tree, lower, upper, result", trees_to_clip)
def test_tree_clip(tree, lower, upper, result):
    clipped_tree = optx_misc.tree_clip(tree, lower, upper)
    assert tree_allclose(clipped_tree, result)


@pytest.mark.parametrize(
    "pred, true, false, expected", tree_where__pred_true_false_expected
)
def test_tree_where(pred, true, false, expected):
    result = optx_misc.tree_where(pred, true, false)
    assert tree_allclose(result, expected)


@pytest.mark.parametrize(
    "y, bounds, step, offset, expected_result",
    y_bounds_step_offset_expected,
)
def test_feasible_step_length(y, bounds, step, offset, expected_result):
    if offset is None:
        result = optx_misc.feasible_step_length(y, step, *bounds)
    else:
        result = optx_misc.feasible_step_length(y, step, *bounds, offset=offset)
    assert tree_allclose(result, expected_result)
    assert optx_misc.tree_min(result) >= 0.0
    assert optx_misc.tree_max(result) <= 1.0
