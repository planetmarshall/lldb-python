#!/usr/bin/env python3

from argparse import ArgumentParser
from fnmatch import fnmatch
from glob import glob
from pathlib import Path
import os
import re
import shutil
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Iterable


def postprocess():
    pass


def _unpack_wheel(wheel_file: Path, destination: Path) -> Path:
    run(["wheel", "unpack", str(wheel_file), "--dest", destination], check=True)
    pattern = "lldb_python*"
    wheel_dir = glob(str(destination / pattern))
    if len(wheel_dir) == 0:
        raise RuntimeError("wheel folder not found")

    return Path(os.path.realpath(wheel_dir[0]))


def _find_file_or_folder(wheel_dir: Path, pattern) -> Path:
    for root, folders, files in os.walk(wheel_dir):
        for folder in folders:
            if fnmatch(folder, pattern):
                return Path(root) / folder

        for file_name in files:
            if fnmatch(file_name, pattern):
                return Path(root) / file_name

    raise RuntimeError(f"{pattern} not found under {wheel_dir}")


def _extra_libs(data_dir: Path) -> Iterable[Path]:
    for root, folders, files in os.walk(data_dir):
        for filename in files:
            if fnmatch(filename, "liblldb*"):
                yield Path(root) / filename


def _fixup_record_file(wheel_dir: Path):
    def updated_records(rows: Iterable[str], lldb_server_path):
        for row in rows:
            if "liblldb" in row:
                continue

            if "lldb-server" in row:
                yield re.sub(r"^\S+lldb-server", lldb_server_path, row.strip(), 1)
            else:
                yield row.strip()

    record_file = _find_file_or_folder(wheel_dir, "RECORD")
    new_lldb_server_path = _find_file_or_folder(wheel_dir, "lldb-server")
    new_lldb_server_relative_path = os.path.relpath(new_lldb_server_path, wheel_dir)
    with open(record_file, 'r') as fp:
        records = fp.readlines()

    with open(record_file, 'w') as fp:
        fp.writelines(updated_records(records, new_lldb_server_relative_path))


def _repack_wheel(src_dir: Path, dest_dir: Path):
    run(["wheel", "pack", "--dest-dir", dest_dir, src_dir])


def preprocess(args):
    with TemporaryDirectory() as tmp:
        wheel_dir = _unpack_wheel(Path(args.wheel), Path(tmp))
        data_dir = _find_file_or_folder(wheel_dir, "data")
        for extra_lib in _extra_libs(data_dir):
            print(f"removing extra library {extra_lib}")
            os.remove(extra_lib)

        site_packages_dir = _find_file_or_folder(wheel_dir, "site-packages")
        print(f"moving bin folder")
        shutil.move(data_dir / "bin", site_packages_dir)

        _fixup_record_file(wheel_dir)
        os.makedirs(args.dest_dir, exist_ok=True)
        _repack_wheel(wheel_dir, args.dest_dir)


def main():
    parser = ArgumentParser("edit the generated wheel")
    subparsers = parser.add_subparsers(required=True)

    preprocess_parser = subparsers.add_parser("preprocess")
    preprocess_parser.add_argument("wheel")
    preprocess_parser.add_argument("--dest-dir", default=os.getcwd())
    preprocess_parser.set_defaults(func=preprocess)

    postprocess_parser = subparsers.add_parser("postprocess")
    postprocess_parser.add_argument("wheel")
    postprocess_parser.set_defaults(func=postprocess)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
