#!/usr/bin/env python3
"""Generate the front-page image for 24 November 2026.

Draws a newspaper front page with Pillow + DejaVu fonts:
masthead, one lead story, a 2x3 grid of stories, an ALSO TODAY footer.
Deterministic: fixed fonts, fixed layout, no randomness, no timestamps.
Writes entry.png (1024x1024) next to this script.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 253, 248)
INK = (18, 18, 18)
RED = (168, 24, 24)
NAVY = (22, 38, 66)
GREY = (110, 110, 105)
LIGHT = (238, 236, 228)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Wrap text into lines that fit max_w pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped text; return y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def tanker(draw, x, y, w, h, color):
    """Simple geometric tanker silhouette inside box (x, y, w, h)."""
    # hull
    hull_y = y + int(h * 0.55)
    draw.polygon([
        (x, hull_y),
        (x + int(w * 0.92), hull_y),
        (x + w, hull_y + int(h * 0.22)),
        (x + int(w * 0.08), hull_y + int(h * 0.22)),
    ], fill=color)
    # bow waterline stripe
    draw.rectangle([x, hull_y + int(h * 0.22) - 3, x + w, hull_y + int(h * 0.22)], fill=color)
    # deck / superstructure
    sx = x + int(w * 0.62)
    draw.rectangle([sx, hull_y - int(h * 0.30), sx + int(w * 0.22), hull_y], fill=color)
    draw.rectangle([sx + int(w * 0.05), hull_y - int(h * 0.38), sx + int(w * 0.17), hull_y - int(h * 0.30)], fill=color)
    # funnel
    fx = x + int(w * 0.40)
    draw.rectangle([fx, hull_y - int(h * 0.24), fx + int(w * 0.10), hull_y], fill=color)
    # cargo masts
    for mx in (int(w * 0.18), int(w * 0.30), int(w * 0.52)):
        draw.line([x + mx, hull_y, x + mx, hull_y - int(h * 0.16)], fill=color, width=4)
    # waves
    for i, wy in enumerate((hull_y + int(h * 0.30), hull_y + int(h * 0.38))):
        for k in range(5):
            wx = x + k * int(w * 0.21) + (i * 12)
            draw.arc([wx, wy, wx + int(w * 0.14), wy + 14], 0, 180, fill=color, width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36  # margin
    cw = W - 2 * mx  # content width

    # ---- masthead ----
    f_mast = font(SERIF_B, 62)
    d.text((W // 2, 26), "THE WORLD TODAY", font=f_mast, fill=INK, anchor="ma")
    f_date = font(SANS_B, 21)
    d.text((W // 2, 100), "TUESDAY, 24 NOVEMBER 2026", font=f_date, fill=RED, anchor="ma")
    d.line([(mx, 132), (W - mx, 132)], fill=INK, width=3)
    d.line([(mx, 138), (W - mx, 138)], fill=INK, width=1)

    # ---- lead story ----
    ly = 156
    f_kick = font(SANS_B, 19)
    d.text((mx, ly), "WASHINGTON  •  THE LEAD", font=f_kick, fill=RED)
    f_lead = font(SERIF_B, 40)
    lead_head = "U.S. SEVERS IRAN'S 'LAST FINANCIAL LIFELINE'"
    y = draw_wrapped(d, mx, ly + 30, lead_head, f_lead, 620, leading=48)
    f_dek = font(SANS, 20)
    dek = ("Treasury's 'Operation Economic Outcast' hits dozens of exchange houses "
           "moving billions for Tehran. A U.S. naval blockade has halted its oil exports.")
    y = draw_wrapped(d, mx, y + 8, dek, f_dek, 620, leading=26)
    d.text((mx, y + 10), "Investigators traced $14.7 billion in shadow-banking deals.",
           font=font(SANS_B, 19), fill=NAVY)

    # lead art panel: tanker silhouette
    px, py, pw, ph = 700, 156, 288, 236
    d.rectangle([px, py, px + pw, py + ph], fill=NAVY)
    tanker(d, px + 24, py + 28, pw - 48, 120, (253, 253, 248))
    d.text((px + pw // 2, py + 168), "U.S. NAVAL BLOCKADE", font=font(SANS_B, 19),
           fill=(253, 253, 248), anchor="ma")
    d.text((px + pw // 2, py + 196), "DAY 130 AT SEA", font=font(SANS, 17),
           fill=(200, 205, 220), anchor="ma")
    d.line([(mx, 408), (W - mx, 408)], fill=INK, width=2)

    # ---- grid: 2 rows x 3 cols ----
    stories = [
        ("MARKETS", "HUANG IS BACK — NVIDIA SOARS 31%",
         "Jensen Huang returns as chief executive 11 days after resigning. "
         "The Nasdaq jumps 6.5% in one of the most extraordinary days in U.S. market history."),
        ("SEOUL", "RUSSIAN JET SETS OFF ISLAND ALERT",
         "South Korea briefly orders evacuations on Ulleung island after a Russian "
         "aircraft enters its airspace."),
        ("WARSAW", "NATO SENDS AWACS TO POLAND",
         "Early-warning aircraft deploy after three Russian missiles landed in Poland on Friday."),
        ("BENGHAZI", "UKRAINE SINKS RUSSIAN WARSHIP IN LIBYA",
         "Maritime drones sink the corvette Merkury in port, Kyiv says — the war spreading "
         "far beyond Europe."),
        ("ANTALYA", "CLIMATE TALKS COLLAPSE",
         "COP31 ends without a deal on fossil fuels. Australia faces backlash; "
         "Pacific nations voice despair."),
        ("VANUATU", "6.5 QUAKE SHAKES VANUATU",
         "Strong earthquake strikes the Pacific island nation. No tsunami threat, officials say."),
    ]
    gx, gy = mx, 428
    cell_w = (cw - 2 * 24) // 3
    cell_h = 196
    f_gkick = font(SANS_B, 16)
    f_ghead = font(SERIF_B, 23)
    f_gbody = font(SANS, 16)
    for i, (kick, head, body) in enumerate(stories):
        col, row = i % 3, i // 3
        x = gx + col * (cell_w + 24)
        yy = gy + row * cell_h
        d.text((x, yy), kick, font=f_gkick, fill=RED)
        yy = draw_wrapped(d, x, yy + 24, head, f_ghead, cell_w, leading=28)
        draw_wrapped(d, x, yy + 4, body, f_gbody, cell_w, leading=21)
        if col < 2:
            d.line([(x + cell_w + 12, yy - 8), (x + cell_w + 12, gy + row * cell_h + cell_h - 16)],
                   fill=GREY, width=1)
    d.line([(mx, 428 + 2 * cell_h - 8), (W - mx, 428 + 2 * cell_h - 8)], fill=INK, width=2)

    # ---- ALSO TODAY footer ----
    fy = 428 + 2 * cell_h + 8
    d.text((mx, fy), "ALSO TODAY", font=font(SANS_B, 20), fill=RED)
    f_also = font(SANS, 17)
    also = ("Odesa left without power, heat or water after Russian strikes  •  "
            "Rep. Jimmy Gomez to resign after ethics finding  •  "
            "Murmansk governor held in embezzlement probe  •  "
            "Mexico captures 'El Chapo Isidro'; 16 cartel members killed  •  "
            "Oxfam: Gaza's air, soil and water poisoned by war  •  "
            "BepiColombo enters orbit around Mercury  •  "
            "EU and Indonesia sign landmark trade deal  •  "
            "24 dead as boat capsizes in Nigeria")
    y = draw_wrapped(d, mx, fy + 30, also, f_also, cw, leading=23)
    d.line([(mx, 992), (W - mx, 992)], fill=INK, width=1)
    d.text((W // 2, 998), "THE WORLD TODAY  •  24 NOVEMBER 2026", font=font(SANS, 14),
           fill=GREY, anchor="ma")

    img.save("entry.png", format="PNG", optimize=True)
    data = open("entry.png", "rb").read()
    print("entry.png:", len(data), "bytes, sha256:", hashlib.sha256(data).hexdigest()[:16])


if __name__ == "__main__":
    main()
