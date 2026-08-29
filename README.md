# 102Architect

A command-line tool that builds the 3x3 homogeneous transformation matrix for a single 2D
affine transformation — translation, homothety (scaling), rotation, or axial symmetry — and
applies it to a point `(x, y)`, printing both the matrix and the resulting coordinates.

Note: despite the Epitech-style numbered name, this exercise is implemented in **Python 3**,
not C. There is no Makefile, `src/`, `include/`, or `tests/` directory in this project, so the
usual `make` / `mingw32-make` build step does not apply here.

## Build

Nothing to compile — it's a Python script.

- **Windows**: `python 102architect <args>`
- **Unix/macOS/WSL**: `chmod +x 102architect && ./102architect <args>` (it has a
  `#!/usr/bin/python3` shebang)

## Usage

```
python 102architect x y -t i j     # translate by vector (i, j)
python 102architect x y -h m n     # homothety: scale by ratio m on x, n on y
python 102architect x y -r alpha   # rotate by alpha degrees
python 102architect x y -s alpha   # reflect about an axis inclined at alpha degrees
```

`x y` (the point to transform) are required; a missing pair exits with code 84.

**Example — translation:**
```
$ python 102architect 3 4 -t 1 2
Translation by the vector (1, 2)
1.00	0.00	1.00
0.00	1.00	2.00
0.00	0.00	1.00
(3,4) => (4.00,6.00)
```

**Example — rotation:**
```
$ python 102architect 1 0 -r 90
Rotation at a 90 degree angle
0.00	-1.00	0.00
1.00	0.00	0.00
0.00	0.00	1.00
(1,0) => (0.00,1.00)
```

## How it works

`main()` starts from a 3x3 identity matrix. Depending on which flag (`-t`, `-h`, `-r`, `-s`) is
found on the command line, it fills in the matching coefficients directly: `-t` adds the
translation vector into the last column, `-h` scales the diagonal by the given ratios, and
`-r`/`-s` set the 2x2 block from `cos`/`sin` of the angle (in radians) to build a rotation or
reflection matrix. The `translation()`, `homothety()`, `rotation()`, and `symmetry()` helper
functions only print the human-readable description line for each case. The matrix is then
printed row by row, and applied to `(x, y)` in homogeneous coordinates:
`x' = m0*x + m1*y + m2`, `y' = m3*x + m4*y + m5`.

## Testing

`test_102architect.py` is a pytest suite that runs the script as a subprocess and covers the
documented examples above, boundary values (zero/negative/large coordinates, a full 360-degree
rotation), and malformed input. Run it with:

```
python -m pytest test_102architect.py -v
```

**Bug fixed:** previously, a non-integer `x`/`y` (e.g. `python 102architect abc 4 -t 1 2`) or a
transformation flag given without its required numeric operands (e.g. `python 102architect 3 4
-t 1`) raised an unhandled `ValueError`/`IndexError` traceback and exited with code `1`, instead
of the documented graceful exit code `84`. The argument parsing is now wrapped so both cases
exit `84` cleanly, consistent with the missing-point-args case.
