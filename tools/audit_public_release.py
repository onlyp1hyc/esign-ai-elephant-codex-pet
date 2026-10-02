#!/usr/bin/env python3
"""Audit publishable files and ZIPs; report locations/categories, never matched values.

This is a project-specific hygiene check, not a guarantee that no secret exists.
Git-ignored private records are excluded. Sensitive-looking paths are rejected
without opening them. Review staged changes and use a dedicated secret scanner
as an additional release gate.
"""
from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from urllib.parse import urlsplit, unquote
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_HOSTS = {'github.com', 'learn.chatgpt.com', 'json-schema.org'}
PRIVATE_PARTS = {'.git', '.archive', 'qa', 'refs', 'review-samples', '__pycache__',
                 'node_modules', 'secrets', 'credentials', '.ssh', '.aws', '.gnupg',
                 '.venv', 'venv', '.idea', '.vscode'}
TEXT_SUFFIXES = {'.md', '.json', '.py', '.cjs', '.js', '.html', '.txt'}
PATTERNS = {
    'private-key': r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'github-token': r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b',
    'api-token': r'\b(?:sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|xox[baprs]-[A-Za-z0-9-]{15,}|AKIA[A-Z0-9]{16})\b',
    'jwt': r'\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b',
    'credential-assignment': r'''(?i)(?:api[_-]?key|access[_-]?token|password|secret|cookie|authorization)["']?\s*[:=]\s*["'][A-Za-z0-9+/=_ .-]{12,}["']''',
    'personal-path': r'(?:/Users/|/home/)[A-Za-z0-9._-]+/[^\s"\'<>]*|[A-Z]:\\Users\\[^\s]+|file:[/]{2}',
    'private-job-id': r'\bexec-[0-9a-f]{8}-[0-9a-f-]{27,}',
    'private-network': r'\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b',
    'internal-host': r'(?i)\b(?:[\w-]+\.)+(?:internal|intranet|local|corp)\b',
    'email-address': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}
issues = []
counts = {'files': 0, 'images': 0, 'archiveEntries': 0, 'markdownLinks': 0}

def issue(location, kind):
    issues.append({'location': location, 'category': kind})

def blocked(name):
    p = PurePosixPath(name)
    n = p.name.lower()
    return (p.is_absolute() or '..' in p.parts or any(x in PRIVATE_PARTS for x in p.parts)
            or p.parts[:1] == ('config',) or p.parts[:2] == ('deploy', 'config')
            or n.startswith('.env') or p.suffix.lower() in {'.env', '.pem', '.key', '.p12', '.pfx', '.log', '.pyc'}
            or any(word in n for word in ('token', 'credential', 'secret', 'password', 'api_key', 'private_key'))
            or n.startswith(('id_rsa', 'id_ed25519')) or n in {'auth.json', '.ds_store'})

def inspect_text(name, content):
    for label, pattern in PATTERNS.items():
        for m in re.finditer(pattern, content):
            issue(name + ':' + str(content.count('\n', 0, m.start()) + 1), label)
    for m in re.finditer(r'https?://[^\s<>"\')]+', content):
        parsed = urlsplit(m.group(0).rstrip('.,;'))
        if parsed.hostname not in PUBLIC_HOSTS or parsed.username or parsed.password:
            issue(name, 'unreviewed-url')

def inspect(name, data):
    suffix = PurePosixPath(name).suffix.lower()
    if suffix in {'.png', '.webp', '.jpg', '.jpeg', '.gif'}:
        with Image.open(io.BytesIO(data)) as im:
            keys = set(im.info) - {'duration', 'loop', 'background', 'timestamp', 'transparency', 'aspect', 'version', 'bbox', 'blend', 'disposal', 'extension'}
            if keys or im.getexif(): issue(name, 'image-metadata-requires-review')
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
        counts['images'] += 1
    elif suffix in TEXT_SUFFIXES or PurePosixPath(name).name in {'LICENSE', '.gitignore'}:
        inspect_text(name, data.decode('utf-8'))
    else:
        issue(name, 'unreviewed-file-type')
    counts['files'] += 1

def main():
    # Tracked AND candidate untracked files; --exclude-standard respects .gitignore.
    result = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
                            cwd=ROOT, capture_output=True, check=True)
    names = sorted(set(result.stdout.decode().strip('\0').split('\0')))
    names = [name for name in names if name]
    if not names: raise SystemExit('No public candidate files found; run from a Git checkout.')
    for name in names:
        p = ROOT / name
        if blocked(name) or p.is_symlink():
            issue(name, 'forbidden-path'); continue
        data = p.read_bytes()
        inspect(name, data)
        if p.suffix == '.md':
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', data.decode()):
                if target.startswith(('https://', '#')): continue
                dest = unquote(target.split('#')[0])
                link = (p.parent / dest).resolve()
                if not link.is_file() or not link.is_relative_to(ROOT) or link.relative_to(ROOT).as_posix() not in names:
                    issue(name, 'missing-or-private-markdown-target')
                counts['markdownLinks'] += 1
    archives = []
    for p in sorted((ROOT / 'dist').glob('*.zip')):
        with zipfile.ZipFile(p) as z:
            if z.comment: issue(p.name, 'zip-comment')
            if z.testzip() is not None: issue(p.name, 'zip-integrity')
            for entry in z.infolist():
                relative = PurePosixPath(entry.filename)
                if len(relative.parts) < 2 or blocked(str(PurePosixPath(*relative.parts[1:]))):
                    issue(p.name, 'forbidden-archive-path'); continue
                if relative.is_absolute() or '..' in relative.parts or ((entry.external_attr >> 16) & 0o170000) == 0o120000:
                    issue(p.name, 'unsafe-archive-entry'); continue
                if entry.comment or entry.extra: issue(p.name, 'zip-extra-metadata')
                inspect(p.name + ':' + entry.filename, z.read(entry))
                counts['archiveEntries'] += 1
        archives.append({'name': p.name, 'bytes': p.stat().st_size,
                         'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    report = {'ok': not issues, 'scope': 'Git public candidate files and dist ZIP contents; ignored private material not opened',
              'checks': counts, 'issues': issues, 'archives': archives}
    (ROOT / 'qa').mkdir(exist_ok=True)
    (ROOT / 'qa/public-release-audit.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 1 if issues else 0

if __name__ == '__main__':
    sys.exit(main())
