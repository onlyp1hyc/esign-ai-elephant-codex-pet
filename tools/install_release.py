#!/usr/bin/env python3
"""Download and install the accepted v1.2 pet using Python's standard library."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import zipfile

VERSION = 'v1.2.0'
RELEASE_URL = 'https://github.com/onlyp1hyc/esign-ai-elephant-codex-pet/releases/download/v1.2.0/esign-ai-elephant-codex-v2.zip'
EXPECTED_SHA256 = 'faacd5cf746abadc9653d7e0d610fe99df82b83b3a8460fe3ecc5173381409ba'
MAX_DOWNLOAD_BYTES = 2 * 1024 * 1024
PET_ID = 'esign-ai-elephant'
FILES = ('pet.json', 'spritesheet.webp')


def verified_files(data):
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise ValueError('安装包 SHA-256 不匹配，已停止安装。')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        expected = {PET_ID + '/' + name for name in FILES}
        if len(archive.infolist()) != 2 or set(archive.namelist()) != expected:
            raise ValueError('安装包目录结构不符合预期。')
        if any(entry.file_size > 4 * 1024 * 1024 for entry in archive.infolist()):
            raise ValueError('安装包文件大小不符合预期。')
        files = {name: archive.read(PET_ID + '/' + name) for name in FILES}
    pet = json.loads(files['pet.json'])
    if (set(pet) != {'id', 'displayName', 'description', 'spriteVersionNumber', 'spritesheetPath'}
            or pet['id'] != PET_ID or pet['spriteVersionNumber'] != 2
            or pet['spritesheetPath'] != 'spritesheet.webp'):
        raise ValueError('安装包不是预期的 Codex V2 小象。')
    return files


def install(data, pets_dir):
    files = verified_files(data)
    target = Path(pets_dir).expanduser().resolve() / PET_ID
    if os.path.lexists(target):
        if (not target.is_symlink() and target.is_dir()
                and all((target / name).is_file() and not (target / name).is_symlink()
                        and (target / name).read_bytes() == content for name, content in files.items())):
            return target, False
        raise ValueError('已有同名宠物，内容不同或路径异常；请先备份并重命名，再重新安装。')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()  # Refuse a target created concurrently; never overwrite it.
    created = []
    try:
        for name, content in files.items():
            path = target / name
            with path.open('xb') as output:
                created.append(path)
                output.write(content)
    except OSError:
        for path in created:
            path.unlink()
        target.rmdir()
        raise
    return target, True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='Use a previously downloaded release ZIP; still verifies SHA-256.')
    parser.add_argument('--pets-dir', type=Path,
                        default=Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex') / 'pets')
    args = parser.parse_args(argv)
    try:
        if args.archive:
            with args.archive.open('rb') as source:
                data = source.read(MAX_DOWNLOAD_BYTES + 1)
        else:
            print('正在下载 eSign AI 小象 ' + VERSION + '（约 1.55 MB）…', flush=True)
            request = urllib.request.Request(RELEASE_URL, headers={'User-Agent': 'esign-elephant-pet-installer'})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(MAX_DOWNLOAD_BYTES + 1)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise ValueError('下载内容超过安装包大小限制，已停止安装。')
        target, created = install(data, args.pets_dir)
    except (ValueError, OSError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print('安装失败：' + str(error), file=sys.stderr)
        return 1
    print(('已安装到：' if created else '相同版本已安装：') + str(target))
    print('SHA-256 校验通过。请在 Codex「Settings → Pets / 设置 → 宠物」刷新并选择「eSign AI 小象」。')
    print('个人非官方、非商业作品；公司吉祥物及品牌资产不包含在 MIT 许可中。')
    return 0


if __name__ == '__main__':
    sys.exit(main())
