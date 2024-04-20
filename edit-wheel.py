#!/usr/bin/env python3
import sys
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


def _repack_wheel(src_dir: Path, dest_dir: Path):
    run(["wheel", "pack", "--dest-dir", dest_dir, src_dir])


def preprocess(wheel, dest_dir):
    """
    Remove extra lib files installed by LLVM. These are normally symlinks but the become files
    in the wheel. We can't just not install them as otherwise the _lldb lib ins not installed
    which we need. Also move lldb-server to its expected location relative to the library
    """
    with TemporaryDirectory() as tmp:
        wheel_dir = _unpack_wheel(Path(wheel), Path(tmp))
        data_dir = _find_file_or_folder(wheel_dir, "data")
        for extra_lib in _extra_libs(data_dir):
            print(f"removing extra library {extra_lib}")
            os.remove(extra_lib)

        site_packages_dir = _find_file_or_folder(wheel_dir, "site-packages")
        print(f"moving bin folder")
        shutil.move(data_dir / "bin", site_packages_dir)

        os.makedirs(dest_dir, exist_ok=True)
        _repack_wheel(wheel_dir, dest_dir)


def _modified_dependencies(shared_lib) -> Iterable[Path]:
    """
    a generator returning the names of library paths that the delocate tool
    has modified
    """
    result = run(["otool", "-L", shared_lib], check=True, capture_output=True, text=True)
    rows = result.stdout.splitlines()
    # skip the header
    for row in rows[1:]:
        # each entry is of the form '<lib path> <compatibility info>'
        lib_path = Path(row.lstrip().split()[0])
        if "lldb_python.dylibs" in lib_path.parts:
            yield lib_path.name


def _lib_install_names(otool_output, lib_dependencies):
    for row in otool_output.splitlines():
        elements = row.strip().split()
        if "name" in elements:
            lib = elements[1].split("/")[-1]
            for lib_base in lib_dependencies:
                if lib_base in lib:
                    yield lib, elements[1]


def _update_shared_lib_paths_macos(shared_lib: Path):
    otool_output = run(["otool", "-l", shared_lib], check=True, capture_output=True, text=True)
    dependencies = list(_modified_dependencies(shared_lib))
    old_entries = {lib: entry for lib, entry in _lib_install_names(otool_output.stdout, dependencies)}

    for lib, lib_path in old_entries.items():
        new_lib_path = f"@loader_path/../lldb_python.dylibs/{lib}"
        print(f"{shared_lib.name}: Fixing {lib} to {new_lib_path}")
        run(["install_name_tool", "-change", lib_path, new_lib_path, shared_lib], check=True)


def _update_shared_lib_paths_linux(shared_lib: Path):
    print(f"Updating shared library paths in {shared_lib}")
    run(["patchelf", "--set-rpath", "$ORIGIN/../lldb_python.libs", shared_lib], check=True)


def postprocess(wheel, dest_dir):
    """
    ``delocate`` doesn't take account of the data folder
    (see `Issue 149 <https://github.com/matthew-brett/delocate/issues/149>`_) when calculating library paths,
    so fix them up here. Also remove the reference to `Python`, as it will be found automatically in the environment
    """
    _update_shared_lib_paths = _update_shared_lib_paths_macos if sys.platform.lower() == "darwin" else _update_shared_lib_paths_linux
    with TemporaryDirectory() as tmp:
        wheel_dir = _unpack_wheel(Path(wheel), Path(tmp))
        shared_lib = _find_file_or_folder(wheel_dir, "*.so")
        _update_shared_lib_paths(shared_lib)
        lldb_server = _find_file_or_folder(wheel_dir, "lldb-server")
        _update_shared_lib_paths(lldb_server)
        os.makedirs(dest_dir, exist_ok=True)
        _repack_wheel(wheel_dir, dest_dir)


def main():
    parser = ArgumentParser("edit the generated wheel")
    subparsers = parser.add_subparsers(required=True)

    preprocess_parser = subparsers.add_parser("preprocess")
    preprocess_parser.add_argument("wheel")
    preprocess_parser.add_argument("--dest-dir", default=None)
    preprocess_parser.set_defaults(func=preprocess)

    postprocess_parser = subparsers.add_parser("postprocess")
    postprocess_parser.add_argument("wheel")
    postprocess_parser.add_argument("--dest-dir", default=None)
    postprocess_parser.set_defaults(func=postprocess)

    args = parser.parse_args()
    if Path(args.wheel).is_dir():
        wheel = _find_file_or_folder(args.wheel, "lldb_python*.whl")
    else:
        wheel = args.wheel

    dest_dir = args.dest_dir or os.path.dirname(wheel)
    args.func(wheel, dest_dir)


if __name__ == "__main__":
    main()
