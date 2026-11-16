from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = Path("raw")
FIG = Path("figures")
FIG.mkdir(exist_ok=True)

def mesure(partie, prefixe, colonne):
    medianes = []

    for rep in (1, 2):
        fichier = RAW / f"p{partie}_{prefixe}_r{rep}.csv"
        d = pd.read_csv(fichier)

        # Exclure les 10 premières secondes
        d = d[d["T_START"] - d["T_START"].min() >= 10]

        if d.empty or (d["STATUS"] != 200).any():
            raise ValueError(f"Mesure invalide : {fichier}")

        if d["INSTANCE"].nunique() != 1:
            raise ValueError(f"Plusieurs instances : {fichier}")

        medianes.append(d[colonne].median())

    return sum(medianes) / 2


def comparer(ax, points, colonne):
    x = [valeur for prefixe, valeur in points]

    for partie, label, marker in [
        (1, "Partie 1 - Avant", "o"),
        (3, "Partie 3 - Après", "s")
    ]:
        y = [
            mesure(partie, prefixe, colonne)
            for prefixe, valeur in points
        ]

        ax.plot(x, y, marker=marker, linewidth=2, label=label)

    ax.grid(alpha=0.3)
    ax.legend()


# FIGURE 1a / 3a : comparaison U et P

fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)

u = [("u100", 100), ("base", 1000), ("u10000", 10000)]
p = [("p10", 10), ("u100", 20),
     ("p100", 100), ("p1000", 1000)]

comparer(axes[0], u, "SERVER_MS")
comparer(axes[1], p, "SERVER_MS")

for ax, facteur, valeurs in [
    (axes[0], "U", [100, 1000, 10000]),
    (axes[1], "P", [10, 20, 100, 1000])
]:
    ax.set_xscale("log")
    ax.set_xticks(valeurs)
    ax.set_xticklabels([str(v) for v in valeurs])
    ax.set_xlabel(f"Facteur {facteur}")

axes[0].set_title("Utilisateurs U (P=20, F=20)")
axes[1].set_title("Publications P (U=100, F=20)")
axes[0].set_ylabel("Temps serveur médian (ms)")

fig.suptitle("Comparaison Partie 1 / Partie 3 - Facteurs U et P")
fig.tight_layout()
fig.savefig(FIG / "fig_compare_1a_3a.png", dpi=160)
plt.close(fig)


# FIGURE 1b / 3b : comparaison F

f = [(f"f{x:02d}", x) for x in range(5, 101, 5)]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

for ax, colonne, titre in [
    (axes[0], "SERVER_MS", "Temps serveur"),
    (axes[1], "LATENCY_MS", "Latence client")
]:
    comparer(ax, f, colonne)
    ax.axvline(30, color="gray", linestyle="--")
    ax.set_yscale("log")
    ax.set_xlabel("F - nombre de comptes suivis")
    ax.set_ylabel("Latence médiane (ms)")
    ax.set_title(titre)

fig.suptitle("Comparaison Partie 1 / Partie 3 - Facteur F")
fig.tight_layout()
fig.savefig(FIG / "fig_compare_1b_3b.png", dpi=160)
plt.close(fig)

print("Figures créées :")
print("figures/fig_compare_1a_3a.png")
print("figures/fig_compare_1b_3b.png")
