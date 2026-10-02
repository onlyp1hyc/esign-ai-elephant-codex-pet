# V1.2 Visual Notes

V1.2 was installed and manually accepted by the maintainer before public-release preparation. The public release retains the accepted character artwork and runtime assets.

## Retained revisions

- The upper-right source `source/revisions/look-v3/002.png` is the approved reference.
- The final up/down sources are `source/revisions/look-v3/000.png` and `008.png`: the nose follows the vertical face axis, with a connected two-lobed tip. Up uses two small nostril strokes; down has none.
- Direction sources use the same foot-width and baseline normalization. Left/right walking sources are separate, avoiding mirrored shirt lettering.
- The V1.1 direction and posture revision changed 19 frame files; V1.2 subsequently changed only the two vertical look frames and their native atlas cells. Private comparison archives are not required to build the public project.

Approved source hashes are in [source/revision-v3-generation.json](./source/revision-v3-generation.json) and [source/final-vertical-generation.json](./source/final-vertical-generation.json).

## Visual limitations

These are independent AI-generated poses, not a skeletal animation or exact 3D turntable. Small changes in outlines, lettering, eye shape, hands and prop contact remain between frames. Walking and blinking have restrained motion; 64 px shirt text is not guaranteed to be individually legible. Acceptance of this personal pet does not imply an official company brand review.

## Review assets

[State overview](./preview.png) · [Direction overview](./direction-preview.png) · [Clockwise direction review](./previews/look-clockwise.webp)

Open `demo/index.html` for frame stepping and light / dark backgrounds. Run `python3 tools/review_visuals.py` to generate local contact sheets under `qa/`; those files are intentionally not distributed. Resource validation checks format, transparency and pixel consistency, not artistic quality.
