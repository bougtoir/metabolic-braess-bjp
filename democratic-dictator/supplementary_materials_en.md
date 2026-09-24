# Supplementary Materials

## Periodic Constitutional Dictatorship: Simulation Protocol and Robustness Notes

This document supports the research article "The Ballot Is Not Democracy: Periodic Constitutional Dictatorship, Intertemporal Accountability, and the Long-Run Survival of Democratic Polities." All figures and numerical summaries in the main text are generated from the code in the `simulation_en.py` script (Python 3, fixed random seed 42).

---

### 1. Constitutional-cycle loss L(T)

**Model.** The loss function reported in Figure 1 is

    L(T) = A (T - 1)^alpha + B / (T - 1)^beta + C

where T = 2, 3, ..., 50, and A, B, C, alpha, beta are positive shape parameters. The first term captures the cumulative cost of institutional sclerosis during ordinary democratic periods; the second term captures the expected cost of the PCD phase; the third term is a fixed institutional cost. The optimum is

    T* = 1 + (Bbeta / (Aalpha))^{1/(alpha + beta)}.

**Simulation protocol.** For each of 200 independent draws, A, B, C, alpha, beta were drawn from uniform distributions with ranges that keep L(T) convex and unimodal in the displayed range (A in [0.05, 0.15], B in [0.5, 2.0], C in [0.1, 0.5], alpha in [1.0, 1.5], beta in [0.8, 1.2]). In every draw the function L(T) had exactly one global minimum over the integer grid 2 <= T <= 50.

**Robustness.** The unimodal shape is preserved as long as the sclerosis term is increasing and convex in T and the PCD-cost term is decreasing and convex in T. If alpha or beta are below 1 the function can become monotonic or have boundary minima, which underlines the importance of curvature in the hazards.

---

### 2. Agent-based trust-election game

**Population structure.** N = 30 agents, each either a cooperator (G) or a defector (B). Evolution follows a Moran process with Fermi selection and mutation.

**Payoffs.** In each normal period an agent plays a one-shot pairwise public-goods interaction. Cooperators pay a cost c and generate a benefit b for their interaction partner; defectors pay no cost and receive whatever benefit the partner provides. Baseline values: c = 1.0, b = 1.0, so mutual cooperation yields payoff 1.0 and mutual defection yields 0.0.

**Trust-election bonus.** A trust election occurs at the end of every cycle of length T = 5 normal periods. The bonus is proportional to the fraction of cooperators in the population at the end of the cycle and is weighted by lambda:

    trust_bonus_i = lambda * (number of G agents / N)

where lambda = 0 for the baseline scenario and lambda = 3 for the trust-election scenario. The bonus is added to every agent's payoff in the election period.

**Selection.** In each step one parent is selected with probability proportional to exp(beta_sel * payoff_i), where beta_sel = 0.15. A randomly chosen agent is then replaced by the parent's type. A small mutation probability mu = 0.03 flips the copied type, preserving polymorphism and preventing permanent fixation.

**Runs.** The simulation was run for n_runs = 50 independent replicates, each for n_cycles = 2000 cycles (a cycle equals T normal periods plus one trust-election round). The final cooperation fraction is the share of G agents at the end of the last cycle.

**Summary statistics.**

- lambda = 0.0: final cooperation mean = 0.014, median = 0.000, std = 0.028, P(final > 0.8) = 0.00, P(final < 0.2) = 1.00.
- lambda = 3.0: final cooperation mean = 0.917, median = 0.967, std = 0.098, P(final > 0.8) = 0.82, P(final < 0.2) = 0.00.

**Interpretation.** The result is a comparative-statics claim: holding the stochastic environment constant, a sufficiently large trust-election premium shifts the long-run distribution of cooperation toward high levels. It does not imply deterministic convergence because finite population size and mutation keep the process stochastic.

**Robustness checks performed.**

- Varying N from 20 to 100 preserves the qualitative shift when lambda is large enough relative to normal-period payoffs.
- Varying T from 3 to 10 leaves the direction of the shift unchanged, although the speed of convergence is sensitive to T.
- Lowering beta_sel to 0.05 slows convergence but does not remove the high-cooperation basin when lambda = 3.
- Raising mu to 0.05 raises variance but leaves the mean final cooperation above 0.7 for lambda = 3.

---

### 3. Figure generation

- Figure 1: `simulation_p1_en.png`, produced by the `plot_constitutional_cycle()` function.
- Figure 2: `simulation_p2_en.png`, produced by the `plot_trust_election()` function. The horizontal axis is shown on a logarithmic scale to display both early convergence and the long-run distribution. The inset histograms show the distribution of final cooperation fractions across the 50 replicates.

---

### 4. Reproducibility

The fixed random seed (42) and deterministic parameter table allow the exact figures in the paper to be reproduced by running:

```bash
python3 simulation_en.py
```

The code does not use any external empirical datasets; all numerical illustrations are generated from symbolic parameter values and the agent-based model described above.

---

### 5. Acknowledgment of limits

The simulation is deliberately stylized. It is not intended to forecast behavior in a real polity. Its purpose is to show that a high-stakes trust election can, in a minimal evolutionary setting, alter the long-run distribution of trustworthy behavior in the expected direction.
