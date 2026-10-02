# Retained Artwork and Build Inputs

`generated/character_master.png` is the high-resolution master. `sheets/` contains nine semantic and two movement sheets. `revisions/` contains the final 16 direction sources and three posture corrections. `artwork.json` defines selection, extraction, duration and normalization; the root-level portraits are derived images.

`generation-record.json` provides sanitized provenance. Revision records retain the approved source hashes used by the regression validator. Private prompts, conversation excerpts, job identifiers and machine paths are kept out of the public repository and archives.

`client-compatibility.json` records the checked installed-client version, V2 contract hashes and maintainer-reported manual acceptance. The available newer version was not runtime-tested.

Rebuilding uses these retained images and does not call an image model or read credentials. All mascot artwork and derivatives remain company / respective rights-holder assets and are excluded from MIT. See [BRAND_ASSETS.md](../BRAND_ASSETS.md).
