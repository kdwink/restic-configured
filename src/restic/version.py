import os
import re


def read_version():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{src_dir}/version.txt", 'rb') as f:
        read_bytes = f.read()
        text = read_bytes.decode('utf-8')
        version = re.search(r"version=(\d+)", text).group(1)
        git_hash = re.search(r"hash=(.*)$", text).group(1)
        return f"version={version} hash={git_hash}"

