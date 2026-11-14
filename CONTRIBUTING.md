# Engineering changes

Original content is all rights reserved. This document does not grant an open-source license or additional usage rights. Contact the rights holder before external use or contribution; if already authorized, follow these conventions.

1. State units, coordinates and datums when changing dimensions. Update parameters, hole tables, BOM, assembly instructions and affected simulation parameters together.
2. Record manufacturing settings and measured evidence. Do not describe digital checks or assumed simulation parameters as physical validation.
3. Run `python tools/validate_repository.py` and relevant module checks. CAD changes require geometry and export checks, including configuration readback.
4. Preserve supplier provenance, revisions, fingerprints and attribution. Reference meshes are not manufacturing data; third-party rights remain unchanged.
5. Mark PCB or firmware work complete only when the native project and checked outputs actually exist.
6. English is the default project language. Keep Spanish and Chinese README entry points aligned with the current assembly, dimensions, maturity and rights statements. Preserve existing mechanical part IDs.
