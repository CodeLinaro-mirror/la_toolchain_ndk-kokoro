#
# Copyright 2026 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import enum
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from typing import List, Union
import zipfile

@enum.unique
class Host(enum.Enum):
    """Enumeration of supported hosts."""
    Darwin = 'darwin'
    Linux = 'linux'
    Windows = 'windows'


def get_default_host() -> Host:
    """Returns the Host matching the current machine."""
    if sys.platform.startswith('linux'):
        return Host.Linux
    if sys.platform.startswith('darwin'):
        return Host.Darwin
    if sys.platform.startswith('win'):
        return Host.Windows
    raise RuntimeError(f'Unsupported host: {sys.platform}')


def create_new_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def run_cmd(args: List[Union[str, Path]], cwd: Path = None) -> None:
    if cwd is not None:
        print(f'cd {cwd}')
    str_args = [str(arg) for arg in args]
    if get_default_host() == Host.Windows:
        print(subprocess.list2cmdline(str_args))
    else:
        print(' '.join([shlex.quote(arg) for arg in str_args]))
    sys.stdout.flush()
    subprocess.run(str_args, cwd=cwd, check=True)


def zip_dir(root: Path, out_file: Path) -> None:
    """Zip a folder with archive paths relative to the root to a zip file at the given path"""
    with zipfile.ZipFile(out_file, 'w', zipfile.ZIP_DEFLATED) as zip_obj:
        zip_dir_to_zip(root, zip_obj)


def zip_dir_to_zip(root: Path, zip_obj: zipfile.ZipFile) -> None:
    """Zip a folder with archive paths relative to the root to zip file handle"""
    for parent, _, files in os.walk(root):
        for file in files:
            install_file = Path(parent) / file
            rel_file = install_file.relative_to(root)
            zip_obj.write(install_file, rel_file)
