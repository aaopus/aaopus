"""Baut das Profilbanner: HI-Logo als ASCII-Art vor einem Beitragskalender der letzten 12 Wochen.

Datenquelle ist der oeffentliche Beitragskalender, den GitHub ohnehin unter dem
Profil zeigt (github.com/users/<name>/contributions). Kein Token, keine
Fremdpakete, nur Python-Standardbibliothek. Das Logo steckt als Raster in dieser Datei.

Aufruf:  python3 banner.py <github-name>
Schreibt banner-dark.svg und banner-light.svg neben dieses Skript.
Schlaegt das Laden oder Lesen fehl, bricht es ab und laesst die alten Banner stehen.
"""
import datetime, html, http.client, math, pathlib, re, sys, time, urllib.request

HERE = pathlib.Path(__file__).parent
WEEKS = 12

THEMES = {
    "dark":  dict(bg="#0f1218", frame="#232a36", art="#b4bbc7", cap="#8a93a3",
                  f0="#1b2028", f1="#262c36", f2="#343b47", f3="#434b59", f4="#5b6475"),
    "light": dict(bg="#f6f7f9", frame="#dde1e8", art="#0f1218", cap="#5d6573",
                  f0="#e2e5ea", f1="#d2d6dd", f2="#bfc4cd", f3="#aeb4be", f4="#8e95a1"),
}
LEVEL_CHARS = [".'", ":;", "+", "=", "#"]   # Stufe 0 (kein Beitrag) bis 4 (viele), wie GitHubs Kacheln

FS, LH, CW, PAD = 13, 16, 7.83, 28
WIDTH = 1024   # Hoehe ergibt sich aus der Logo-Hoehe (2 Pixelzeilen je Textzeile)
GAP = 1.6     # freie Luft um die Logo-Silhouette
HALO = 4      # bis zu diesem Abstand bleibt das Feld ruhig
MIN_H, MAX_H, MAX_W = 27, 78, 100   # Logo-Masse in Pixeln: ab 27 hoch sind alle 7 Wochentage sichtbar

# --- Daten -------------------------------------------------------------------------
def load_levels(user):
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user):
        sys.exit(f"Ungueltiger GitHub-Name: {user!r}")
    req = urllib.request.Request(f"https://github.com/users/{user}/contributions",
                                 headers={"User-Agent": "profile-banner"})
    for attempt in range(3):                       # kurze Netzaussetzer abfangen
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                page = r.read().decode("utf-8")
            break
        except (OSError, http.client.HTTPException) as e:
            if attempt == 2:
                sys.exit(f"Beitragskalender nicht erreichbar ({e}), Banner bleibt unveraendert")
            time.sleep(5)
    levels, counts, ids = {}, {}, {}
    for td in re.findall(r"<td\b[^>]*\bdata-date=[^>]*>", page):
        date = re.search(r'data-date="(\d{4}-\d\d-\d\d)"', td)
        level = re.search(r'data-level="(\d)"', td)
        cid = re.search(r'\bid="([^"]+)"', td)
        if date and level:
            levels[date.group(1)] = int(level.group(1))
            if cid:
                ids[cid.group(1)] = date.group(1)
    for cid, text in re.findall(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        m = re.match(r"\s*(\d[\d,]*) contribution", text)
        if cid in ids:
            counts[ids[cid]] = int(m.group(1).replace(",", "")) if m else 0
    if len(levels) < 7 * WEEKS:
        sys.exit(f"Beitragskalender nicht lesbar ({len(levels)} Tage gefunden), Banner bleibt unveraendert")
    # Zahlen stammen aus den Tooltips; fehlen sie oder passen sie nicht zu den Stufen,
    # hat sich das Format geaendert -> lieber abbrechen als "0 contributions" zeigen
    missing = [d for d in levels if d not in counts or (levels[d] > 0 and counts[d] == 0)]
    if len(counts) < 0.9 * len(levels) or missing:
        sys.exit(f"Beitragszahlen nicht lesbar ({len(missing)} Tage ohne Zahl), Banner bleibt unveraendert")
    return levels, counts

# --- Logo --------------------------------------------------------------------------
# Pixel-HI-Logo, ein Zeichen je 8-px-Pixel (# = schwarz). Neu erzeugen mit logo_einbetten.py.
LOGO = """
...........................................#.....................
.................................#.###...###.....................
................................###########......................
...............................############......................
...............................############......................
..............................###############....................
.............................##########..........................
...........................####....#.............................
...........................##.#...#...................#..........
...........................##.#..##..................#...........
..........................#####.##..................##...........
.........................#########................###............
........................#########................###.............
........................##########..............####.............
.......................##########..............####.........#....
.................#.....###########...........######.....####.....
...............#.#....############.........#######..#######......
...............####..##.#####..###........###############........
..........########...#..####.#####......################.........
........###############.##########...##################..........
.........##############..#############################...........
........################..#################################......
.......##################.######################################.
......####################.#################################.....
......##################################################.........
.....####################.#############################..........
.....###################################################.........
....#####################################################........
.....#######.#####################.##############..########......
......###....#####################.##############......#####.....
............#######################........#######..........#....
...........########################..........#####...............
...........#.######################.............##...............
..........#...#####################...............#..............
.........##...#####################..............................
.........#..#######################..............................
........#..########################..............................
.......##..########################..............................
....####..################.########..............................
.....##...###.###########..#####.................................
....####.####..##########.####..##...............................
...###...#####.##########.####.####..............................
..####...###############.####..#####.............................
..####...###############.####.#######............................
..###...###############.####.#########...........................
.##.....#####...###.###.####.##########..........................
.#.....####.........###.####.##########..........................
#......###...........##.####.###########.........................
.......###...........##.####.#############....#######............
.......####...........#.####.###############..#########..........
.........###............####.################.##########.........
..........##...........#####.################.############.......
.......................####.###############################......
...........................###################...####.#####......
..........................####################...#####..####.....
...........................###################....#####..###.....
.............................#################.....####..####....
................................##############......####..###....
.................................############........###...###...
.................................############.........##....###..
..................................############........##......###
..................................############........###......##
.................................######...#####........##........
................................######....######.......###.......
................................#####......#####.........##......
...............................#####.......#####..........##.....
...............................#####.......####..................
................................####......#####..................
................................#####.....####...................
.................................#####...####....................
..................................####...####....................
..................................###.....###....................
.................................###.......###...................
.................................###.......###...................
.................................######....######................
.................................######....######................
"""

def load_logo():
    rows = LOGO.strip("\n").split("\n")
    W, H = len(rows[0]), len(rows)
    if "#" not in LOGO or any(len(r) != W for r in rows):
        sys.exit("Logo-Raster in banner.py ist beschaedigt, Banner bleibt unveraendert")
    if not (MIN_H <= H <= MAX_H and W <= MAX_W):
        sys.exit(f"Logo {W}x{H} passt nicht ins Banner (max. {MAX_W} breit, {MIN_H}-{MAX_H} hoch), Banner bleibt unveraendert")
    g = [[1 if ch == "#" else 0 for ch in r] for r in rows]
    return g, W, H

def hsh(x, y, salt=0):
    h = (x * 374761393 + y * 668265263 + salt) & 0xFFFFFFFF
    return ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF

def logo_ascii(g, W, H):
    on = lambda x, y: 0 <= x < W and 0 <= y < H and g[y][x]
    def depth(x, y, r=3):
        for d in range(1, r + 1):
            for dy in range(-d, d + 1):
                for dx in range(-d, d + 1):
                    if not on(x + dx, y + dy):
                        return d - 1
        return r
    deep, mid, edge, top, bot = "@%MW#", "gHmk8", "j|lki", "\"'`^*", ".,_;:"
    pick = lambda chars, x, y: chars[(hsh(x, y) >> 16) % len(chars)]
    art = []
    for ty in range(0, H, 2):
        row = ""
        for x in range(W):
            t, b = on(x, ty), on(x, ty + 1)
            if t and b:
                d = min(depth(x, ty), depth(x, ty + 1))
                row += pick(deep if d >= 2 else mid if d == 1 else edge, x, ty)
            elif t:
                row += pick(top, x, ty)
            elif b:
                row += pick(bot, x, ty)
            else:
                row += " "
        art.append(row.ljust(W))
    return art

# --- Banner ------------------------------------------------------------------------
def build(levels, counts, today):
    g, W, H = load_logo()
    art = logo_ascii(g, W, H)
    cols, rows = int((WIDTH - 2 * PAD) / CW), len(art)
    off = (cols - W) // 2

    def dist(cx, cy):
        lx, best = cx - off, 99.0
        for py in range(max(0, cy * 2 - 12), min(H, cy * 2 + 14)):
            for px in range(max(0, lx - 12), min(W, lx + 13)):
                if g[py][px]:
                    best = min(best, math.hypot(px - lx, py - (cy * 2 + 0.5)))
        return best

    start = today - datetime.timedelta(days=today.weekday() + 7 * (WEEKS - 1))
    total = sum(counts.get((start + datetime.timedelta(days=i)).isoformat(), 0)
                for i in range((today - start).days + 1))
    gaps = [d for d in (start + datetime.timedelta(days=i) for i in range((today - start).days + 1))
            if d.isoformat() not in levels]
    if gaps:
        sys.exit(f"Kalender unvollstaendig ({len(gaps)} Tage fehlen), Banner bleibt unveraendert")
    caption = f"{total:,} contribution{'' if total == 1 else 's'} · last {WEEKS} weeks"

    cells = []
    for cy in range(rows):
        line = []
        for cx in range(cols):
            lx = cx - off
            if 0 <= lx < W and art[cy][lx] != " ":
                line.append((art[cy][lx], "art")); continue
            d = dist(cx, cy)
            gutter = (cx * WEEKS) % cols < WEEKS or (cy * 7) % rows < 7
            day = start + datetime.timedelta(days=(cx * WEEKS // cols) * 7 + cy * 7 // rows)
            if d < GAP or gutter or day > today:
                line.append((" ", None)); continue
            lv = levels.get(day.isoformat(), 0)
            if d < HALO:
                lv = min(lv, 1)
            h = hsh(cx, cy, 7); h ^= h >> 16
            line.append((LEVEL_CHARS[lv][h % len(LEVEL_CHARS[lv])], f"f{lv}"))
        cells.append(line)
    x = cols - len(caption) - 1
    if any(cells[rows - 1][x + i][1] == "art" for i in range(-1, len(caption) + 1)):
        sys.exit("Beschriftung wuerde das Logo ueberdecken, Banner bleibt unveraendert")
    cells[rows - 1][x - 1] = (" ", None)           # Luft zwischen Feld und Beschriftung
    cells[rows - 1][cols - 1] = (" ", None)        # und rechts davon
    for i, ch in enumerate(caption):
        cells[rows - 1][x + i] = (ch, "cap")

    out = {}
    for name, c in THEMES.items():
        height = 2 * PAD + rows * LH
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{FS}px">',
               "<title>HI – Histudios</title>",
               "<style>" + "".join(f".{k}{{fill:{c[k]}}}" for k in ("art", "cap", "f0", "f1", "f2", "f3", "f4"))
               + "text,tspan{white-space:pre}</style>",
               f'<rect width="{WIDTH}" height="{height}" rx="12" fill="{c["bg"]}" stroke="{c["frame"]}"/>',
               '<text xml:space="preserve">']
        x0 = (WIDTH - cols * CW) / 2
        for cy, line in enumerate(cells):
            spans, cur, buf = [], None, ""
            for ch, cls in line:
                cls = cls or cur or "art"
                if cls != cur and buf:
                    spans.append((cur, buf)); buf = ""
                cur = cls; buf += ch
            spans.append((cur, buf))
            inner = "".join(f'<tspan class="{k}">{html.escape(t)}</tspan>' for k, t in spans if t)
            # volle Zeilenlaenge + textLength: jede Monospace-Schrift fuellt exakt dieselbe Breite
            svg.append(f'<tspan x="{x0:.1f}" y="{PAD + (cy + 1) * LH - 4}" textLength="{cols * CW:.1f}" lengthAdjust="spacing">{inner}</tspan>')
        svg.append("</text></svg>")
        out[name] = "\n".join(svg) + "\n"
    return out

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Aufruf: python3 banner.py <github-name>")
    levels, counts = load_levels(sys.argv[1])
    today = max(datetime.date.fromisoformat(d) for d in levels)   # letzter Tag im Kalender
    utc_today = datetime.datetime.now(datetime.timezone.utc).date()
    if abs((today - utc_today).days) > 1:      # veralteter Cache oder Zukunftstage
        sys.exit(f"Kalender endet am {today}, heute ist {utc_today}, Banner bleibt unveraendert")
    for name, svg in build(levels, counts, today).items():
        (HERE / f"banner-{name}.svg").write_text(svg, encoding="utf-8")
    print(f"Banner gebaut, Stand {today}")
