"""Génère le boîtier de télécommande (base + couvercle) en STL, unités : mm."""
import struct
from pathlib import Path
import numpy as np
from manifold3d import Manifold, CrossSection

L, W, H = 120.0, 45.0, 8.0      # base extérieure
PAROI = 3.0                      # parois et fond
R_EXT = 4.0                      # rayon des coins extérieurs
COUV_EP = 2.0                    # épaisseur du couvercle plat
TROU_D = 10.5                    # Ø des trous (boutons de 10 mm + jeu)
TROUS_X = [20, 40, 60, 80, 100]  # centres des 5 trous, sur l'axe central
SEG = 96

OUT = Path(__file__).parent


def rect_arrondi(l, w, r, h):
    r = max(min(r, l / 2 - 0.01, w / 2 - 0.01), 0.01)
    cs = CrossSection.square((l - 2 * r, w - 2 * r)).offset(r, circular_segments=SEG)
    return Manifold.extrude(cs, h).translate((r, r, 0))


def base():
    ext = rect_arrondi(L, W, R_EXT, H)
    cav = rect_arrondi(L - 2 * PAROI, W - 2 * PAROI, R_EXT - PAROI, H).translate((PAROI, PAROI, PAROI))
    return ext - cav


def couvercle():
    piece = rect_arrondi(L, W, R_EXT, COUV_EP)
    for x in TROUS_X:
        piece -= Manifold.cylinder(COUV_EP * 3, TROU_D / 2, circular_segments=SEG).translate((x, W / 2, -COUV_EP))
    return piece


def ecrire_stl(m, chemin, nom):
    mesh = m.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    t = np.asarray(mesh.tri_verts)
    with open(chemin, "wb") as f:
        f.write(nom.encode().ljust(80, b" "))
        f.write(struct.pack("<I", len(t)))
        for a, b, c in t:
            p0, p1, p2 = v[a], v[b], v[c]
            n = np.cross(p1 - p0, p2 - p0)
            n = n / (np.linalg.norm(n) or 1)
            f.write(struct.pack("<12fH", *n, *p0, *p1, *p2, 0))
    print(f"{chemin.name}: {len(t)} triangles, volume {m.volume() / 1000:.1f} cm³")


b, c = base(), couvercle()
ecrire_stl(b, OUT / "base.stl", "base telecommande")
ecrire_stl(c, OUT / "couvercle.stl", "couvercle telecommande")
ecrire_stl(b + c.translate((0, W + 10, 0)), OUT / "boitier-complet.stl", "boitier telecommande")
