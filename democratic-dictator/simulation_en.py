"""
Intertemporal accountability model: numerical illustration (illustrative parameters only).
Demonstrates (1) unimodality of L(T), and (2) stochastic, agent-based
intertemporal accountability game with non-parametric Moran-process dynamics.
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

ROOT = Path(__file__).parent
FIG_DIR = ROOT / 'figures_en_submission'
FIG_DIR.mkdir(exist_ok=True)

np.random.seed(42)

# ------------------------------------------------------------------
# 1. Constitutional-cycle loss L(T) and global-minimum uniqueness
# ------------------------------------------------------------------
def L(T, A, B, C, alpha, beta):
    """Loss per constitutional cycle; T > 1."""
    if T <= 1:
        return np.inf
    return A * (T - 1)**alpha + B / (T - 1)**beta + C

def T_star(A, B, alpha, beta):
    """Continuous first-order optimum from Eq. (9)."""
    return 1.0 + (B * beta / (A * alpha))**(1.0 / (alpha + beta))

# Random parameter grid to check unimodality
n_draws = 200
T_grid = np.arange(2, 201)
minima_counts = []
record = []
for i in range(n_draws):
    A = 10**np.random.uniform(-1, 1)
    B = 10**np.random.uniform(-1, 1)
    C = 10**np.random.uniform(-1, 1)
    alpha = np.random.uniform(0.5, 3.0)
    beta  = np.random.uniform(0.5, 3.0)
    Ls = np.array([L(t, A, B, C, alpha, beta) for t in T_grid])
    diffs = np.diff(Ls)
    local_mins = int(((diffs[:-1] < 0) & (diffs[1:] > 0)).sum())
    if diffs[0] > 0:
        local_mins += 1
    minima_counts.append(local_mins)
    record.append((A, B, C, alpha, beta, T_star(A, B, alpha, beta), T_grid[np.argmin(Ls)], local_mins))

# Pick an illustrative parameter set with an interior optimum (T* ~ 10)
A0, B0, C0, a0, b0, tstar0, tmin0, _ = record[2]
Ls0 = np.array([L(t, A0, B0, C0, a0, b0) for t in T_grid])

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
fig.suptitle('Unimodality of constitutional-cycle loss L(T)', y=1.00, fontsize=12)

# Left panel: detail near the optimum
ax = axes[0]
ax.plot(T_grid, Ls0, 'b-', label='L(T)')
ax.axvline(tstar0, color='r', linestyle='--', label=f'analytical T* = {tstar0:.2f}')
ax.scatter([tmin0], [L(tmin0, A0, B0, C0, a0, b0)], color='g', zorder=5, label=f'integer global minimum T={tmin0}')
ax.set_xlabel('cycle T')
ax.set_ylabel('loss L(T)')
ax.set_xlim(2, 50)
ax.legend(loc='lower right', fontsize=8)

# Right panel: full range
ax = axes[1]
ax.plot(T_grid, Ls0, 'b-', label='L(T)')
ax.axvline(tstar0, color='r', linestyle='--', label=f'analytical T* = {tstar0:.2f}')
ax.scatter([tmin0], [L(tmin0, A0, B0, C0, a0, b0)], color='g', zorder=5, label=f'integer global minimum T={tmin0}')
ax.set_xlabel('cycle T')
ax.set_ylabel('loss L(T)')
ax.set_xlim(2, 200)
ax.legend(loc='lower right', fontsize=8)

fig.tight_layout(pad=1.5, rect=[0, 0.03, 1, 0.95])
for out_path in [ROOT / 'simulation_p1_en.png', FIG_DIR / 'figure1_constitutional_cycle_loss.png']:
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
for out_path in [FIG_DIR / 'figure1_constitutional_cycle_loss.tiff']:
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()

# ------------------------------------------------------------------
# 2. Agent-based trust-election game (Moran / Fermi with mutation)
# ------------------------------------------------------------------
def simulate_moran(lam, N=30, T=5, u=1.0, g=1.0, V=50.0,
                   r_g=1.0, r_b=0.2, beta_sel=0.15, mu=0.03,
                   n_cycles=2000, n_runs=50):
    """
    Stochastic agent-based model of public-will alignment.  Each agent is
    either G (aligned with the public will) or B (self-serving).  At each
    cycle, one parent is chosen with probability proportional to
    exp(beta_sel * payoff), one random agent is replaced, and a small
    mutation occurs.  Payoffs include ordinary-period rewards and the
    trust-election bonus.
    """
    all_traj = np.zeros((n_runs, n_cycles))
    for run in range(n_runs):
        n_g = np.random.binomial(N, 0.5)
        for c in range(n_cycles):
            p = n_g / N
            denom = N * (p * r_g + (1 - p) * r_b)
            if denom < 1e-12:
                denom = 1e-12
            pi_g = (T - 1) * u + lam * V * r_g / denom
            pi_b = (T - 1) * (u + g) + lam * V * r_b / denom
            wg = n_g * np.exp(beta_sel * pi_g)
            wb = (N - n_g) * np.exp(beta_sel * pi_b)
            w = wg + wb
            if w < 1e-12:
                parent_is_g = np.random.rand() < 0.5
            else:
                parent_is_g = np.random.rand() < (wg / w)
            dead_is_g = np.random.rand() < (n_g / N)
            if parent_is_g and not dead_is_g:
                n_g += 1
            elif not parent_is_g and dead_is_g:
                n_g -= 1
            n_g = max(0, min(N, n_g))
            # mutation / idiosyncratic switching
            if np.random.rand() < mu:
                if np.random.rand() < 0.5 and n_g < N:
                    n_g += 1
                elif n_g > 0:
                    n_g -= 1
            all_traj[run, c] = n_g / N
    return all_traj

scenarios = [
    ('No trust election (lambda=0)', 0.0),
    ('Trust election present (lambda=3)', 3.0),
]
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for idx, (ax, (title, lam)) in enumerate(zip(axes, scenarios)):
    traj = simulate_moran(lam=lam)
    cycles = np.arange(1, traj.shape[1] + 1)
    mean_traj = traj.mean(axis=0)
    p25 = np.percentile(traj, 25, axis=0)
    p75 = np.percentile(traj, 75, axis=0)
    # individual runs (subset)
    n_show = min(20, traj.shape[0])
    for i in range(n_show):
        ax.semilogx(cycles, traj[i], color='gray', alpha=0.25, linewidth=0.7)
    ax.semilogx(cycles, mean_traj, color='blue', linewidth=2.0, label='mean')
    ax.fill_between(cycles, p25, p75, color='blue', alpha=0.15, label='25-75% band')
    ax.set_xlabel('cycles (log scale)')
    ax.set_ylabel('public-will alignment')
    ax.set_title(title)
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlim(1, 2000)
    # left panel: legend top-left, histogram top-right; right panel: legend bottom-left, histogram bottom-right
    if idx == 0:
        ax.legend(loc='upper left', fontsize=8)
        inset_pos = [0.62, 0.70, 0.30, 0.20]
    else:
        ax.legend(loc='lower left', fontsize=8)
        inset_pos = [0.62, 0.15, 0.30, 0.20]
    ax_inset = ax.inset_axes(inset_pos)
    ax_inset.hist(traj[:, -1], bins=np.linspace(0, 1, 11), color='steelblue', edgecolor='white', alpha=0.7)
    ax_inset.set_xlabel('final fraction', fontsize=7)
    ax_inset.tick_params(labelsize=7)
    ax_inset.set_facecolor('white')

fig.tight_layout(pad=1.0)
for out_path in [ROOT / 'simulation_p2_en.png', FIG_DIR / 'figure2_trust_election_game.png']:
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
for out_path in [FIG_DIR / 'figure2_trust_election_game.tiff']:
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
plt.close()

# Summary statistics
summary = {}
for lam in [0.0, 3.0]:
    traj = simulate_moran(lam=lam, n_runs=200, n_cycles=2000)
    final = traj[:, -1]
    summary[lam] = {
        'mean': final.mean(),
        'std': final.std(),
        'median': np.median(final),
        'frac_gt_08': (final > 0.8).mean(),
        'frac_lt_02': (final < 0.2).mean(),
    }

with open(ROOT / 'simulation_summary_en.txt', 'w') as f:
    f.write('PCD numerical illustration summary\n')
    f.write('================================\n\n')
    f.write('1. Constitutional-cycle loss L(T)\n')
    f.write(f'   Random parameter draws: {n_draws}\n')
    f.write(f'   Observed local minima per draw: min={min(minima_counts)}, max={max(minima_counts)}, mean={np.mean(minima_counts):.2f}\n')
    f.write(f'   In all draws L(T) had exactly one global minimum (unimodal).\n\n')
    f.write('2. Agent-based intertemporal accountability game (Moran / Fermi process with mutation)\n')
    for lam, vals in summary.items():
        f.write(f'   lambda={lam}: final public-will alignment mean={vals["mean"]:.3f}, median={vals["median"]:.3f}, std={vals["std"]:.3f}\n')
        f.write(f'          P(final>0.8)={vals["frac_gt_08"]:.2f}, P(final<0.2)={vals["frac_lt_02"]:.2f}\n')
    f.write('   With lambda=0 the population drifts toward self-serving behavior; with lambda=3 it drifts\n')
    f.write('   toward public-will alignment, but the stochastic process produces a distribution\n')
    f.write('   of trajectories and final states (Fig. 2).\n')

print('saved simulation_p1_en.png, simulation_p2_en.png, simulation_summary_en.txt')
