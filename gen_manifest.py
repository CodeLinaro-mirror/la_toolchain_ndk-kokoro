#!/usr/bin/env python3
#
# Copyright (C) 2021 The Android Open Source Project
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

# Generate a repo/pore manifest.xml from either a Kokoro multiscm checkout or
# from a local checkout of the aosp ndk-kokoro-main manifest branch. This file
# is uploaded as a build artifact to record which source repositories were
# used to build a binary.

from pathlib import Path
from textwrap import dedent
import argparse, os, re, subprocess, sys


def get_repo_revision(path: Path) -> str:
    """Given a path to a Git repository, return the SHA commit hash."""
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'],
                                   cwd=path, encoding='utf8').strip()


def get_repo_name(path: Path) -> str:
    """Given a path to a git repository, return the relative URL from the Git
    host to the repository.
    """
    git_remote_output = subprocess.check_output(['git', 'remote', '-v'],
                                                cwd=path, encoding='utf8')
    name_matches = set()
    for remote_line in git_remote_output.splitlines():
        # Currently, all ndk-kokoro-main repositories come from the AOSP
        # git-on-borg host.
        m = re.match(
            # remote name (probably 'aosp' or 'origin')
            r'[^\t]+\t'
            r'(?:rpc|sso|https|persistent-https)'
            r'://'
            # AOSP host
            r'(?:android|android\.googlesource\.com|android\.git\.corp\.google\.com)'
            r'/(.+) \((?:fetch|push)\)$',
            remote_line)
        if m: name_matches.add(m.group(1))
    if len(name_matches) != 1:
        # N.B. For local development, it may be useful to have extra repositories
        # that aren't from AOSP. To exempt them from this check, consider adding
        # a placeholder remote pointing at some non-existent AOSP repository.
        sys.exit(f"error: could not determine single AOSP URL for checkout "
                 f"'{path}'. 'git remote -v' output: {repr(git_remote_output)}")
    (name,) = name_matches
    return name


def git_add_safe_directory() -> None:
    path_to_add = '*'
    current_dump = subprocess.run(['git', 'config', '--global', 'safe.directory'],
                                  stdout=subprocess.PIPE, encoding='utf-8')
    if path_to_add in current_dump.stdout.splitlines():
        return

    # If the entry already exists, then invoking `git config --add` again will
    # add more and more entries.
    subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', path_to_add],
                   check=True)


def is_docker() -> bool:
    """Returns True when running within a docker container."""
    if Path("/.dockerenv").exists():
        return True

    # Windows doesn't include the same .dockerenv file at the root of the
    # drive. The most correct way to check this appears to be
    # HKLM\System\CurrentControlSet\Control\ContainerType, but who really wants
    # to deal with the registry? Windows+Kokoro is good enough for now.
    if sys.platform == 'win32' and os.getenv('KOKORO_JOB_NAME'):
        return True

    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='.')
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()

    root = Path(args.root).absolute()
    out = Path(args.output).absolute()

    text = dedent('''\
        <?xml version='1.0' encoding='UTF-8'?>
        <manifest>
          <remote name="aosp" fetch="https://android.googlesource.com/" review="https://android.googlesource.com/" />
          <remote name="aospsuperproject" fetch="https://android.googlesource.com/" review="https://android.googlesource.com/" revision="ndk-kokoro-main" />
          <default revision="master" remote="aosp" sync-j="4" />
          <superproject name="platform/superproject" remote="aospsuperproject" />
    ''')

    # Disable git's "safe directory" checking when running in a Docker
    # container. This is needed because the git directories belong to a
    # different user than the current one.
    if is_docker():
        git_add_safe_directory()

    os.chdir(root)
    repos = [Path(parent) for (parent, sub, _) in os.walk('.') if '.git' in sub and parent != './.repo/repo']

    for path in sorted(repos):
        revision = get_repo_revision(path)
        name = get_repo_name(path)

        if name == 'platform/manifest':
            # A local checkout will typically have this repo. A Kokoro build won't have it.
            continue

        xml_path = str(path).replace('\\', '/')
        text += f'  <project path="{xml_path}" name="{name}" revision="{revision}" />\n'

    text += '</manifest>\n'

    with open(out, 'w') as f:
        f.write(text)

if __name__ == '__main__':
    main()
