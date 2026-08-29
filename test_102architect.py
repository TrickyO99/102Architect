"""
Automated test suite for the 102Architect CLI script.

Invokes the script as a subprocess (it has no .py extension, so the
interpreter is passed explicitly) and asserts on stdout / exit code.
"""

import subprocess
import sys
import os

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "102architect")


def run(*args):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Happy path (documented README examples)
# ---------------------------------------------------------------------------

def test_readme_translation_example():
    result = run("3", "4", "-t", "1", "2")
    assert result.returncode == 0
    expected = (
        "Translation by the vector (1, 2)\n"
        "1.00\t0.00\t1.00\n"
        "0.00\t1.00\t2.00\n"
        "0.00\t0.00\t1.00\n"
        "(3,4) => (4.00,6.00)\n"
    )
    assert result.stdout == expected


def test_readme_rotation_example():
    result = run("1", "0", "-r", "90")
    assert result.returncode == 0
    expected = (
        "Rotation at a 90 degree angle\n"
        "0.00\t-1.00\t0.00\n"
        "1.00\t0.00\t0.00\n"
        "0.00\t0.00\t1.00\n"
        "(1,0) => (0.00,1.00)\n"
    )
    assert result.stdout == expected


def test_homothety_scaling():
    result = run("2", "3", "-h", "2", "3")
    assert result.returncode == 0
    assert "Homothety by the ratios 2 and 3" in result.stdout
    # (2,3) scaled by (2,3) => (4.00, 9.00)
    assert "(2,3) => (4.00,9.00)" in result.stdout


def test_symmetry_axis():
    result = run("1", "1", "-s", "0")
    assert result.returncode == 0
    assert "Symmetry about an axis inclined with an angle of 0 degrees" in result.stdout


# ---------------------------------------------------------------------------
# Edge cases: boundary / zero / negative values
# ---------------------------------------------------------------------------

def test_zero_point_no_flag_is_identity():
    # No transformation flag at all -> identity matrix applied to (0,0)
    result = run("0", "0")
    assert result.returncode == 0
    expected = (
        "1.00\t0.00\t0.00\n"
        "0.00\t1.00\t0.00\n"
        "0.00\t0.00\t1.00\n"
        "(0,0) => (0.00,0.00)\n"
    )
    assert result.stdout == expected


def test_negative_coordinates_translation():
    result = run("-5", "-5", "-t", "10", "10")
    assert result.returncode == 0
    assert "(-5,-5) => (5.00,5.00)" in result.stdout


def test_rotation_full_circle_360():
    # Rotating by 360 degrees should return (approximately) to the same point.
    # Note: due to floating-point imprecision in sin(2*pi), the y coordinate
    # prints as "-0.00" rather than "0.00" - a harmless display artifact.
    result = run("1", "0", "-r", "360")
    assert result.returncode == 0
    assert "(1,0) => (1.00,-0.00)" in result.stdout


def test_large_translation_vector():
    result = run("0", "0", "-t", "1000000", "-1000000")
    assert result.returncode == 0
    assert "(0,0) => (1000000.00,-1000000.00)" in result.stdout


# ---------------------------------------------------------------------------
# Bad input: should fail gracefully (exit 84), never an unhandled traceback
# ---------------------------------------------------------------------------

def test_missing_point_args_exits_84():
    result = run("3")
    assert result.returncode == 84
    assert result.stderr == ""


def test_no_args_exits_84():
    result = run()
    assert result.returncode == 84
    assert result.stderr == ""


def test_non_integer_point_exits_gracefully():
    """
    Bug found & fixed: passing a non-integer x/y used to raise an unhandled
    ValueError (traceback, exit code 1) instead of the documented exit 84.
    """
    result = run("abc", "4", "-t", "1", "2")
    assert result.returncode == 84
    assert "Traceback" not in result.stderr
    assert result.stderr == ""


def test_flag_missing_operands_exits_gracefully():
    """
    Bug found & fixed: a transformation flag (e.g. -t) given without its
    required numeric operands used to raise an unhandled IndexError
    (traceback, exit code 1) instead of the documented exit 84.
    """
    result = run("3", "4", "-t", "1")
    assert result.returncode == 84
    assert "Traceback" not in result.stderr
    assert result.stderr == ""


def test_unknown_flag_is_ignored_not_crashed():
    # An unrecognized flag isn't matched by any `if`, so it's silently
    # ignored and the identity matrix is used - documented behavior, not a bug.
    result = run("3", "4", "-z", "1", "2")
    assert result.returncode == 0
    assert "(3,4) => (3.00,4.00)" in result.stdout
