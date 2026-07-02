# lissajous_animations

A terminal-based Lissajous curve animator using Unicode braille characters and 24-bit colour. No dependencies beyond the Python standard library.

![a=3 b=5](Images/Images_expanded_2/Screenshot%20from%202026-07-02%2019-32-52.png)

## What are Lissajous curves?

A Lissajous figure is traced by composing two sine waves at right angles:

```
x(t) = sin(a·t + δ)
y(t) = sin(b·t + φ)
```

The ratio `a:b` determines the shape — 3:2 gives a trefoil knot, 1:1 gives an ellipse, 1:3 gives three arcs. When `a:b` is rational the curve closes; when irrational it never closes and fills the square densely. The figures are projections of geodesics on a torus, and the integer ratios correspond directly to musical intervals (2:1 octave, 3:2 perfect fifth, 4:3 perfect fourth).

The animation drifts `φ` continuously, so you're watching a geodesic slide around the torus in real time.

## Usage

```
python3 lissajous.py
```

Requires Python 3.6+ and a terminal with 24-bit colour support.

## Controls

| Key | Action |
|-----|--------|
| `←` / `→` | decrease / increase `b` |
| `↑` / `↓` | increase / decrease `a` |
| `[` / `]` | shift static phase offset `δ` |
| `f` | toggle square (correct proportions) / fill (stretches to terminal) |
| `q` | quit |

## Tips

- The figure is sized to a square by default, centred in the terminal. On a wide terminal it will sit in the middle with empty space on the sides — this is correct; it ensures circles look like circles. Press `f` to stretch it to fill the screen instead.
- Interesting ratios to explore: `3:2`, `5:4`, `5:3`, `7:4`, `3:7`, `1:1` (collapsing ellipse).
- A taller terminal window gives you a larger figure.
