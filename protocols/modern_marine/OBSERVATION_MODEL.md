# Modern marine observation model

**Biological process**: whether predator distributions track prey fields
(Type B trophic propagation) or merely share environmental forcing (Type A).

**Observation process** (per spec §11):
- survey/sensor structure: ACCESS tow-anchored matched units; TOPP tag
  telemetry; ERDDAP environmental forcing
- spatial matching: tow-anchored matching rules in ecomega `02_build_units.py`
- temporal matching: event separation windows (3/7/14 d)
- observation depth: euphotic pelagic — subsurface prey unobserved
- environmental forcing: upwelling indices from ERDDAP
- detection process: visual sightings / tag uplinks — effort- and
  platform-dependent
- marine connectivity: continuous medium — discrete "locality" is a matched
  survey unit, not a patch

**Known verdicts**: ecomega = COMMON-ENVIRONMENT DOMINATED (Type A);
capelin positive control = WEAK (framework partially validated).
