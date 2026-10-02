# eSign AI Elephant Codex Pet V1.2 — Resource Manifest

This personal, unofficial project uses company mascot artwork. All artwork and brand identifiers are excluded from MIT; see [BRAND_ASSETS.md](./BRAND_ASSETS.md).

## Accepted baseline

V1.2 retains the approved upper-right source and final up/down source artwork. Source hashes are recorded in `source/revision-v3-generation.json` and `source/final-vertical-generation.json`. The maintainer confirmed successful real-client installation and manual acceptance before public release preparation on 2026-10-02.

| Resource | Actual count / size |
| --- | --- |
| High-resolution master | 1 PNG |
| Standard master + state portraits | 1 + 9, 512 × 512 |
| Semantic playback frames | 58, 512 × 512 RGBA PNG |
| Movement frames | 8 left + 8 right |
| Look frames | 16 clockwise directions, 22.5° steps |
| Total frame files | 90; 88 distinct images, 2 intentional repeats |
| Small semantic frames | 58 each at 64 / 96 / 128 px, 174 PNGs |
| Animated previews | 9 semantic animations + 1 direction review |
| Native V2 atlas | 1536 × 2288, 8 × 11 grid, 192 × 208 cells |
| Occupied native cells | 57 animation + 1 neutral + 16 look = 74 |
| Empty native cells | 14, fully transparent |
| Semantic atlas | 768 × 864, 8 × 9 grid, 96 px cells |

The earlier “89 frames” shorthand is not supported by the retained resources. The public documentation corrects the count without changing the accepted files. Greeting and working each deliberately reuse one frame for return motion / looping.

## Native contract and mapping

`pet.json` contains exactly five fields: `id`, `displayName`, `description`, `spriteVersionNumber`, `spritesheetPath`. The version is explicitly 2. Native rows are idle, running-right, running-left, waving, jumping, failed, waiting, running, review, look A and look B. Neutral is row 0, column 6. Look starts at 0° up; 180° is down.

| Semantic state | Frames | Native mapping |
| --- | ---: | --- |
| greeting | 6 | waving |
| idle | 6 | idle |
| task_received | 6 | jumping |
| thinking | 6 | review (approximate) |
| working | 8 | running |
| waiting_approval | 6 | waiting |
| success | 6 | jumping (approximate) |
| error | 8 | failed |
| long_task | 6 | running (approximate) |

The recorded client is 26.928.40906 / build 12694 / prod. Its bundled `hatch-pet` contract, row definitions and atlas validator are identified by SHA-256 in [source/client-compatibility.json](./source/client-compatibility.json). The offered 26.930.21537 / build 12776 update was not installed or runtime-tested. Other hosts and web-upload formats are outside the verified scope.

## Revalidation

[README development instructions](./README.md#development) run the existing 1,953 resource checks, demo logic tests, approved-source regression checks, packaging and archive validation. Automated reports in local `qa/` describe only what those tools test; `runtimeTested: false` in a tool report means that tool does not operate the client UI. Maintainer-reported runtime acceptance is recorded separately.

The primary ZIP contains only `esign-ai-elephant/pet.json` and `esign-ai-elephant/spritesheet.webp`. Public-release preparation preserves the accepted ZIP and runtime bytes. The optional full archive includes retained build inputs, tools, documentation, MIT license and brand notice; private references, prompts, job logs, drafts and local reports are excluded.
