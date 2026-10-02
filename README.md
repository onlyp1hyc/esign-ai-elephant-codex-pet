# eSign AI Elephant Codex Pet

A personal, unofficial and non-commercial Codex desktop pet project based on the company's elephant mascot.

个人制作的 eSign AI 小象桌面宠物，用于个人作品展示、实验及内部交流。

**[Download v1.2 installation ZIP](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/download/v1.2.0/esign-ai-elephant-codex-v2.zip)** · [Release & checksums](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/tag/v1.2.0)

> [!IMPORTANT]
> This is a personal, unofficial and non-commercial project created for experimentation and internal sharing.
>
> The eSign AI mascot, company names, logos, trademarks and related brand assets are company assets or otherwise owned by their respective rights holder(s). They are not owned by the maintainer of this repository and are not licensed under this repository's open-source license.
>
> No copyright, trademark or other intellectual-property rights in those brand assets are transferred or granted by this repository. This project is not affiliated with, sponsored by, or endorsed by the company or OpenAI.
>
> 本项目为个人制作的非官方、非商业实验作品，主要用于个人作品展示及内部交流。
>
> 项目中涉及的 eSign AI 小象吉祥物、公司名称、Logo、商标及相关品牌视觉资产属于公司资产或相应权利人所有，并非本仓库维护者个人资产。
>
> 本仓库的开源许可证仅适用于维护者原创的代码、脚本、配置、构建工具、工程文件及原创文档内容，不包含上述品牌资产。本仓库不代表公司对相关品牌资产授予任何版权、商标或其他知识产权许可。“非商业”描述本项目的定位，不构成品牌使用许可。本项目未获公司或 OpenAI 的官方参与、赞助或背书。

## Preview

![Nine elephant work states](./preview.png)

| Idle | Thinking | Working |
| --- | --- | --- |
| ![Idle animation](./previews/idle.webp) | ![Thinking animation](./previews/thinking.webp) | ![Working animation](./previews/working.webp) |

[Direction overview](./direction-preview.png) · [16-direction review animation](./previews/look-clockwise.webp)

## Features

- Custom eSign AI elephant mascot artwork with transparent PNG / WebP assets.
- Nine semantic states: greeting, idle, task received, thinking, working, waiting for approval, success, error and long task.
- **90 playback frame files: 58 state frames + 16 movement frames + 16 look directions.** Two intentional repeats produce 88 distinct images. The earlier “89 frames” description was corrected by counting the accepted resources; no frame was added or removed.
- Codex desktop V2 pet contract: 1536 × 2288 atlas, 8 × 11 cells, explicit `spriteVersionNumber: 2`.
- Real-client installation and manual acceptance confirmed by the maintainer for V1.2.
- Offline demo, 64 / 96 / 128 px exports, repeatable builds and resource validators.

The complete demo exposes all nine semantic states. Codex uses fixed native rows: thinking maps to review; success and long task use approximate jumping / running fallbacks. The manifest does not add new host events or native states.

## Installation

1. Download **`esign-ai-elephant-codex-v2.zip`** from the [v1.2 Release](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/tag/v1.2.0) (about **1.55 MB**). No clone or Python installation is needed.
2. Unzip it. Keep the `esign-ai-elephant` folder with its two files together.
3. Place that folder in `~/.codex/pets/`. If `CODEX_HOME` is customized, use `$CODEX_HOME/pets/`. Back up and rename any existing same-name folder before replacing it.
4. In Codex, open **Settings → Pets**, refresh, and select **eSign AI 小象**.

```text
~/.codex/pets/esign-ai-elephant/
├── pet.json
└── spritesheet.webp
```

从 Release 下载小安装包 → 解压 → 把整个文件夹放进上述目录 → 设置中刷新并选择小象。安装包保持已验收版本的原始字节。

## Project Structure

| Path | Purpose |
| --- | --- |
| `pet.json` | Minimal five-field V2 manifest |
| `spritesheet.webp`, `spritesheet.json` | Native runtime atlas and layout / frame index |
| `frames/`, `native-frames/` | 58 semantic, 16 movement and 16 look frame files |
| `business-states.json`, `spritesheet_semantic.*` | Semantic event mapping and demo atlas |
| `source/` | Retained artwork, extraction settings and sanitized provenance |
| `exports/`, `previews/` | Small-size frames and animated previews |
| `demo/` | Offline interactive preview; open `demo/index.html` |
| `tools/`, `schemas/` | Build, installation and validation tools; local schema |
| `dist/` | Locally built ZIPs and checksums; binaries distributed through Releases |
| `qa/`, `.archive/`, `review-samples/`, `refs/` | Local reports, drafts and private references; excluded from Git and distribution |

See [manifest.md](./manifest.md) for exact counts and [visual-audit.md](./visual-audit.md) for retained visual limitations.

## Development

Python 3.9+ with Pillow WebP support is required for tooling; Node.js 18+ runs the demo logic test. Install dependencies in an environment of your choice:

```bash
python3 -m pip install -r requirements.txt
python3 tools/validate_package.py
node tools/test_demo.cjs
python3 tools/validate_revision.py
```

The resource validator checks 1,953 conditions, including manifest fields, alpha, dimensions, frame counts, atlas pixels, exports and safe installation into a temporary directory. Revision checks verify retained approved source hashes; comparisons to private old packages run only when those local archives exist. Automated checks do not perform interactive client testing. See [release-validation.json](./release-validation.json) for the public release check summary.

Rebuild from retained source artwork, without an image model or credentials, preferably in a separate checkout:

```bash
python3 tools/build_spritesheet.py
python3 tools/validate_package.py
node tools/test_demo.cjs
python3 tools/validate_revision.py
python3 tools/build_package.py --zip-only
python3 tools/validate_archives.py
python3 tools/audit_public_release.py
```

The build replaces derived files in that checkout. Compression-library versions can change file bytes, and font rendering may change preview labels; compare decoded runtime pixels when checking a rebuild. The accepted Release ZIP remains unchanged. `tools/export_pet_json.py` re-exports the manifest, and `tools/install_pet.py` installs the current source checkout while refusing to overwrite an existing pet.

The optional `esign-ai-elephant-complete.zip` can be built locally for development / archiving. It is not uploaded as a secondary Release asset because the repository already retains the build inputs. Both archives are checked; the full package includes the license and brand notice.

## Compatibility

V1.2 was accepted in the real Codex Desktop client by the maintainer. The recorded installed version is **26.928.40906 (build 12694, prod)**; its bundled V2 atlas validator passes. Evidence and contract hashes are retained in [source/client-compatibility.json](./source/client-compatibility.json).

At that check, **26.930.21537 (build 12776)** was offered as an update but was not installed or tested. Compatibility is not claimed for that version, later clients, web-upload formats, or other pet hosts. The schema in this repository is a local check derived from the recorded contract, not an OpenAI-published schema.

## License

Original code and tooling in this repository are licensed under the [MIT License](./LICENSE) unless otherwise noted. This also covers maintainer-authored configuration, engineering files and original documentation content.

**Brand assets are excluded from the MIT License.** Their presence in source files, previews or Release archives does not grant a brand-asset license.

See [BRAND_ASSETS.md](./BRAND_ASSETS.md) for details.
