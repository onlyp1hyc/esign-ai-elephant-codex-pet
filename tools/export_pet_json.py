#!/usr/bin/env python3
"""导出本机 Codex V2 的最小真实 manifest；业务映射另存。"""
from build_package import export_manifest
if __name__ == '__main__':
    print(export_manifest())
