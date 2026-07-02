#!/usr/bin/env python3
"""Lissajous curve animator — braille canvas, flowing rainbow gradient.

Controls:
  ←/→   decrease/increase b frequency
  ↑/↓   increase/decrease a frequency
  [/]   shift phase delta
  q     quit
"""

import os, sys, tty, termios, select, math, shutil, time

# Braille dot layout within a 2×4 cell: BRAILLE_BITS[row_in_cell][col_in_cell]
BRAILLE_BITS = [[0x01, 0x08], [0x02, 0x10], [0x04, 0x20], [0x40, 0x80]]


def hsv_to_rgb(h, s=0.88, v=1.0):
    h %= 1.0
    i = int(h * 6)
    f = h * 6 - i
    p, q, t_ = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    r, g, b = [(v, t_, p), (q, v, p), (p, v, t_), (p, q, v), (t_, p, v), (v, p, q)][i % 6]
    return int(r * 255), int(g * 255), int(b * 255)


def render(a, b, delta, phase, w, h, square):
    draw_h = h - 2
    dw, dh = w * 2, draw_h * 4
    grid = [[0] * w for _ in range(draw_h)]
    hue_grid = [[0.0] * w for _ in range(draw_h)]

    if square:
        # Braille dots are square in pixels (char cell is ~2× taller than wide,
        # braille packs 2 cols and 4 rows, so each dot = char/2 × char/4 = square).
        # Constrain figure to a square canvas and center it horizontally.
        dim = min(dw, dh)
        xo = (dw - dim) // 2
        x_range, y_range = dim - 1, dh - 1
    else:
        dim = None
        xo = 0
        x_range, y_range = dw - 1, dh - 1

    N = 4000
    hue_shift = phase / (2 * math.pi)

    for i in range(N):
        t = 2 * math.pi * i / N
        x = math.sin(a * t + delta)
        y = math.sin(b * t + phase)
        dx = xo + int((x + 1) / 2 * x_range)
        dy = int((y + 1) / 2 * y_range)
        dx = min(dw - 1, max(0, dx))
        dy = min(dh - 1, max(0, dy))
        cr, cc = dy // 4, dx // 2
        grid[cr][cc] |= BRAILLE_BITS[dy % 4][dx % 2]
        hue_grid[cr][cc] = (i / N + hue_shift) % 1.0

    out = ["\x1b[H"]
    last_r = last_g = last_bv = -1

    for row in range(draw_h):
        line = ""
        for col in range(w - 1):  # skip last column to avoid terminal wrap
            bits = grid[row][col]
            if bits:
                r, g, bv = hsv_to_rgb(hue_grid[row][col])
                if r != last_r or g != last_g or bv != last_bv:
                    line += f"\x1b[38;2;{r};{g};{bv}m"
                    last_r, last_g, last_bv = r, g, bv
                line += chr(0x2800 | bits)
            else:
                if last_r >= 0:
                    line += "\x1b[0m"
                    last_r = -1
                line += " "
        out.append(line)

    mode = "sq" if square else "fill"
    status = (
        f"  a={a}  b={b}  δ={delta / math.pi:.2f}π  [{mode}]"
        f"    ←→ b   ↑↓ a   [] phase   f fill/sq   q quit"
    )
    out.append(f"\x1b[{h - 1};1H\x1b[0m\x1b[2K{status}")

    sys.stdout.write("".join(out))
    sys.stdout.flush()


def main():
    fd = sys.stdin.fileno()
    saved = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        sys.stdout.write("\x1b[?25l\x1b[2J\x1b[H")
        sys.stdout.flush()

        a, b = 3, 2
        delta = math.pi / 4
        phase = 0.0
        square = True

        while True:
            t0 = time.monotonic()
            w, h = shutil.get_terminal_size()
            render(a, b, delta, phase, w, h, square)
            phase = (phase + 0.04) % (2 * math.pi)

            timeout = max(0.0, 1 / 24 - (time.monotonic() - t0))
            rlist, _, _ = select.select([fd], [], [], timeout)
            if rlist:
                key = os.read(fd, 8)
                if key in (b"q", b"Q", b"\x03"):
                    break
                elif key == b"\x1b[A":
                    a = min(a + 1, 15)
                elif key == b"\x1b[B":
                    a = max(a - 1, 1)
                elif key == b"\x1b[C":
                    b = min(b + 1, 15)
                elif key == b"\x1b[D":
                    b = max(b - 1, 1)
                elif key in (b"]", b"=", b"+"):
                    delta = (delta + math.pi / 12) % (2 * math.pi)
                elif key in (b"[", b"-"):
                    delta = (delta - math.pi / 12) % (2 * math.pi)
                elif key in (b"f", b"F"):
                    square = not square
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
        sys.stdout.write("\x1b[?25h\x1b[0m\x1b[2J\x1b[H")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
