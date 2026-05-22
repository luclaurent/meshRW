# Changelog

All notable changes to this project are documented below by date.

Format: chronological timeline with release/tag milestones and notable repository changes.

## 2026-05-22

### Documentation and CI improvements (working tree)

- Added missing public docstrings in package entry points and VTK helper compatibility API.
- Reworked README structure with clearer quick-start, format notes, and documentation links.
- Added detailed project documentation pages under `docs/` and switched to a Sphinx configuration.
- Added documentation build workflow (`CI-docs.yml`) and improved test CI robustness.
- Updated packaging extras to support docs/dev workflows.

## 2025-12-12

### Release tags

- `v1.5.3`

### Changed

- Added writer methods for MSH/VTK workflows.
- Improved homogeneous data handling on MSH output.

## 2025-10-09

### Release tags

- `v1.5.2`

### Changed

- Added optional creation/check of missing output folders before writing files.
- Updated README.

## 2025-06-30

### Release tags

- `v1.5.0`
- `v1.5.1`

### Changed

- Added new options to `msh2`, including control over node reclassification.
- Improved homogeneous data loading and removed-points management when reclassification is enabled.
- Fixed workflow syntax issues.

## 2025-05-13

### Release tags

- `v1.4.0rc0`
- `v1.4.0`
- `v1.4.1`

### Changed

- Added substantial new tests.
- Expanded documentation.
- Improved reader node access based on element tags.

## 2025-02-14

### Release tags

- `v1.3.1rc0`
- `v1.3.1rc1`
- `v1.3.1rc2`
- `v1.3.1rc3`
- `v1.3.1`

### Changed

- Fixed `Mesh.Binary` option syntax.
- Switched version-tag handling to Hatch.

## 2025-02-11

### Changed

- Added optional binary writing support for Gmsh files.
- Disabled binary writing when requested options are incompatible.

## 2025-02-08

### Changed

- Improved input data adaptation before writing.

## 2025-01-24

### Fixed

- Fixed issues in field data analysis.

## 2025-01-21

### Changed

- Removed global Loguru verbosity manipulation to avoid side effects.

## 2025-01-17

### Changed

- Improved time-series management for MSH output.

### Fixed

- Fixed syntax for time-series data handling.

## 2025-01-11

### Release tags

- `v1.3.0rc0`
- `v1.3.0rc1`
- `v1.3.0`

### Changed

- Released 1.3.0 line after RC stabilization.

## 2025-01-10

### Added

- Verbosity options across writer classes.

### Fixed

- Fixed geometrical entity creation issues in Gmsh-backed writing.

## 2025-01-09

### Added

- Added fallback behavior when no physical group is provided.

### Changed

- Normalized element type adaptation.
- Improved entity creation according to element dimension.

## 2024-12-19

### Release tags

- `v1.2.0`
- `v1.2.1rc0`
- `v1.2.2rc0`
- `v1.2.3rc0`

### Added

- Added adaptation procedure to handle inconsistent input data.
- Added tests for VTK writer adaptation behavior.

### Changed

- Improved file-writing logs.
- Improved diagnostics for invalid field type declarations.

### Fixed

- Fixed logging formatting issues.
- Fixed time formatting in temporal exports.

## 2024-12-18

### Release tags

- `v1.0.0rc0`
- `v1.0.0rc1`
- `v1.0.0rc2`
- `v1.0.0rc3`
- `v1.0.0rc4`
- `v1.0.0rc5`
- `v1.0.0rc6`
- `v1.0.0rc7`
- `v1.0.0`
- `v1.1.0`

### Added

- Added coverage badge publication.
- Added package publishing workflow.
- Added `AUTHORS` and `CITATION.cff` metadata.

### Changed

- Strengthened CI around version detection and release automation.
- Updated README and DOI badges.
- Updated VTK version dependency handling.

### Fixed

- Fixed multiple GitHub Actions syntax/release upload issues during release pipeline stabilization.

## 2024-12-17

### Changed

- Refactored writer base class to an abstract (`ABC`) architecture.

## 2024-12-13

### Changed

- Migrated tests to pytest and split test modules.
- Finalized first `msh2` implementation for fields and physical groups.
- Continued stabilization of v2 syntax and payload cleanup.

### Fixed

- Fixed VTK generation issues from the first implementation.
- Performed broad typo/syntax cleanups.

## 2024-12-12

### Changed

- Added new VTK and MSH functionality built on `vtk` and Gmsh APIs.
- Migrated build/project management tooling (Hatch adoption).
- Updated README.

## 2022-08-28

### Fixed

- Fixed typo in `fileio`.

## 2022-08-27

### Release tags

- `v0.2`

### Changed

- Applied multiple fixes and version bump updates.
- Restored missing tests file.

## 2022-04-14

### Changed

- Applied a batch of incremental maintenance updates.

## 2021-10-20

### Changed

- Improved 2D MSH reading behavior.
- Renamed mesh test files and improved tests.
- Updated README.

## 2021-10-18

### Added

- Initial project import and baseline files from SILEXlib.
- Initial MSH/VTK debug scripts and early tests.

### Fixed

- Corrected early MSH payload/file issues and missing files.

### Added

- Documentation site scaffold with MkDocs.
- Contribution guide and development docs.
- CI workflow for strict documentation build.

### Changed

- README reorganized with quickstart and clearer project structure.
- CI test workflow modernized and hardened.
- Missing public docstrings completed.
