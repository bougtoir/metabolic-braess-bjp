# GEB abstract skeleton (6 parts — no polished prose yet)

1. **Background problem**: species distributions are forecast as functions of
   contemporary environment; adding lagged occurrence/abundance improves
   prediction and is commonly interpreted as memory, inertia, hysteresis, or
   delayed climate tracking.
2. **Why lagged distributions may mislead**: lagged state also encodes
   persistent spatial heterogeneity — a consistently suitable site produces
   lag-1 predictability without any path dependence. The two are confounded
   unless static structure is explicitly removed.
3. **Dataset and scope**: North American Breeding Bird Survey, [years],
   [routes] routes, 116 widespread breeding-bird species; ridge-regression
   family M0–M3 with lagged-state terms; retrospective (leave-one-year-out)
   and prospective (forward-chaining, train-only preprocessing) evaluation.
4. **Main spatial-persistence decomposition**: apparent history gain is large
   without spatial control (median ≈ 0.30) and collapses after route
   demeaning (forward + demean median ≈ 0.006); the residual prospective
   signal is small though mostly positive; occupancy hysteresis is
   unsupported (matched-environment contrast = 0 in all definable species).
5. **Occupancy vs abundance contrast**: abundance retains strong temporal
   state dependence (median ≈ +0.63 log-count, 40/41 definable species
   CI > 0) under the same design — demographic continuity, not spatial
   memory.
6. **Broader implication**: lagged-state predictors in distribution models
   and biogeographical forecasts should not be interpreted as memory or
   delayed tracking until persistent spatial heterogeneity is separated;
   distribution persistence and population state dependence are distinct
   phenomena.
