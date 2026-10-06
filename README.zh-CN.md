# eSign AI 小象 Codex Pet

一个基于公司小象吉祥物制作的个人、非官方、非商业 Codex 桌面宠物作品。让小象陪伴思考、工作、等待确认和任务完成。

**简体中文** · [English](./README.md) · [V1.2 下载与发行说明](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/tag/v1.2.0)

> [!IMPORTANT]
> 本项目用于个人作品展示、实验及内部交流，不属于公司正式产品或官方发布，也不表示公司或 OpenAI 的参与、赞助或背书。
>
> eSign AI 小象吉祥物及原始设计、公司及产品名称、Logo、商标，以及基于品牌材料制作或生成的衍生视觉，属于公司资产或相应权利人所有，并非仓库维护者个人资产。
>
> MIT 许可证仅适用于维护者原创的代码、脚本、配置、构建工具、工程文件及原创文档内容，不包含品牌资产。本仓库不代表公司授予相关品牌资产的复制、修改、再分发、再授权、商用或其他知识产权许可。“非商业”描述本项目的定位，不是品牌使用许可。详见 [BRAND_ASSETS.md](./BRAND_ASSETS.md)。

## 交给 Codex 安装（推荐）

在 **本机运行的 Codex** 中新建一个聊天，复制并发送下面这段话：

```text
请帮我安装 eSign AI 小象 Codex Pet V1.2：
https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet

先阅读 README.zh-CN.md，下载并检查 tools/install_release.py，再用 Python 3 执行该安装脚本。只下载约 1.55 MB 的 v1.2.0 发行安装包，无需克隆完整工程。校验脚本中固定的 SHA-256 后，安装到当前用户的 ${CODEX_HOME:-$HOME/.codex}/pets/esign-ai-elephant。如果相同版本已经安装，直接告诉我；如果同名目录内容不同，停止并保留原文件。请遵循当前 Codex 的网络和目录权限流程。完成后告诉我安装结果，并引导我在「设置 → 宠物」刷新、选择「eSign AI 小象」。
```

Codex 自动完成下载、校验和文件安装。最后在 **Settings → Pets / 设置 → 宠物** 中刷新并选择小象。安装位置是执行这段指令的那台电脑；远程环境或云端任务不会把文件自动装到你的本机。

安装脚本固定使用已验收的 V1.2 包，不需要 Pillow、API Key、GitHub 登录或图像生成。现有同名宠物不会被覆盖。

### 终端快捷命令

也可以在 macOS / Linux 终端执行下面的一行命令（需要 `curl` 和 Python 3.9+）：

```bash
curl -fsSL 'https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/raw/refs/heads/codex/asset-pack/tools/install_release.py' | python3 -
```

Windows 可让本机 Codex 下载并用 Python 3 执行同一个脚本。安装脚本同样支持 `CODEX_HOME`，也可用 `--pets-dir` 指定 pets 目录。

### 手动安装

1. 从 [Release](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/tag/v1.2.0) 下载 [esign-ai-elephant-codex-v2.zip](https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/download/v1.2.0/esign-ai-elephant-codex-v2.zip)（1,551,973 bytes，约 1.55 MB）。
2. 解压，将整个 `esign-ai-elephant` 文件夹放入 `~/.codex/pets/`；自定义 `CODEX_HOME` 时放入 `$CODEX_HOME/pets/`。已有同名目录时先备份并重命名。
3. 在 Codex「设置 → 宠物」刷新并选择「eSign AI 小象」。

```text
~/.codex/pets/esign-ai-elephant/
├── pet.json
└── spritesheet.webp
```

## 预览

![小象九种工作状态](./preview.png)

| 待机 | 思考 | 工作 |
| --- | --- | --- |
| ![待机动画](./previews/idle.webp) | ![思考动画](./previews/thinking.webp) | ![工作动画](./previews/working.webp) |

[方向总览](./direction-preview.png) · [16 方向轮换预览](./previews/look-clockwise.webp)

## 功能与资源

- 九种业务状态：欢迎、待机、收到任务、思考、工作、等待确认、完成、异常和长任务。
- 90 个播放帧文件：58 个业务帧、16 个移动帧和16个视线帧；包含两帧有意复用，共88张不同图像。此前“89帧”的说法已按实际资源数量更正。
- 透明 PNG / WebP、64 / 96 / 128 px 导出、离线交互 Demo。
- Codex V2 图集：1536 × 2288，8 × 11 网格，192 × 208 单元，明确声明 `spriteVersionNumber: 2`。
- V1.2 已由维护者在真实客户端安装并人工验收；1,953 项资源检查及 V2 图集校验通过。

Codex 宿主使用固定动画行。完整 Demo 可展示全部九种业务状态；思考近似映射为 review，完成和长任务分别近似映射为 jumping 和 running。`pet.json` 不会新增宿主事件或动画行。

## 项目结构

| 路径 | 内容 |
| --- | --- |
| `pet.json`、`spritesheet.webp` | 已验收的 V2 运行资源 |
| `frames/`、`native-frames/` | 业务、移动和视线帧 |
| `source/` | 保留原画、构建参数、脱敏来源与确认哈希 |
| `exports/`、`previews/` | 小尺寸导出与动画预览 |
| `demo/` | 双击 `demo/index.html` 打开离线预览 |
| `tools/`、`schemas/` | 构建、校验、安装脚本及本地 schema |
| `dist/` | 本地生成的 ZIP 与校验和；用户安装包通过 Release 下载 |
| `qa/`、`.archive/`、`refs/`、`review-samples/` | 本地报告、草稿和私有参考，不进入公开仓库和交付包 |

[资源清单](./manifest.md) · [视觉限制](./visual-audit.md) · [V1.2 验证摘要](./release-validation.json)

## 开发与验证

需要 Python 3.9+、支持 WebP 的 Pillow 和 NumPy；Demo 逻辑测试需要 Node.js 18+。发行包安装脚本只使用 Python 标准库。

```bash
python3 -m pip install -r requirements.txt
python3 tools/validate_package.py
node tools/test_demo.cjs
python3 tools/validate_revision.py
python3 -m unittest discover -s tools -p 'test_install_release.py'
```

在单独的开发副本中从保留原画重新构建，无需调用图像模型：

```bash
python3 tools/build_spritesheet.py
python3 tools/validate_package.py
python3 tools/validate_revision.py
python3 tools/build_package.py --zip-only
python3 tools/validate_archives.py
python3 tools/audit_public_release.py
```

重建会更新该副本中的派生文件。压缩库版本可能影响文件字节，字体渲染可能影响预览文字；比较重建结果时应核对解码后的角色和图集像素。已验收的 Release 安装包保持原样。完整开发 ZIP 可本地构建，未作为附加 Release 资产重复上传。

## 兼容性

V1.2 验收记录对应 **Codex Desktop 26.928.40906（build 12694，prod）**。当时提示的 **26.930.21537（build 12776）** 更新未安装或实测，不宣称已经验证后续客户端、其他宿主或网页上传规格。[兼容性记录](./source/client-compatibility.json)

自动校验检查文件、图集和工程约束；真实客户端的人工验收另行记录。AI 逐帧画面存在轻微线条、字形、手掌和道具接触差异，并非骨骼动画或精密 3D 转台。

安装后的刷新和选择步骤参考 [OpenAI 官方宠物说明](https://learn.chatgpt.com/docs/pets)。

## 许可证

维护者原创的代码、工具、工程文件及原创文档内容适用标准 [MIT License](./LICENSE)，另有注明的除外。

**公司吉祥物及相关品牌资产不包含在 MIT 中。** 公开仓库、预览和发行包的存在不会授予品牌资产许可。详见 [品牌资产说明](./BRAND_ASSETS.md)。
