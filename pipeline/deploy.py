"""Explicit reviewed Git publication. Success here is not Vercel acceptance."""
import argparse
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_DIR / 'scripts'))


def git_push(commit_msg, *, paths=None, date_str=None):
    if not paths or not date_str:
        print('blocked: select individual reviewed docs files and an issue date')
        return False

    def git(*args):
        return subprocess.run(['git', '-C', str(REPO_DIR), *args], capture_output=True, text=True)

    for name in paths:
        relative = Path(name)
        target = REPO_DIR / relative
        if relative.is_absolute() or '..' in relative.parts or not relative.parts or relative.parts[0] != 'docs':
            print('blocked: publication paths must be individual files below docs')
            return False
        if not target.is_file() or target.is_symlink() or not target.resolve().is_relative_to((REPO_DIR / 'docs').resolve()):
            print('blocked: selected file is missing, a directory, or redirected')
            return False
    branch = git('branch', '--show-current')
    origin = git('remote', 'get-url', 'origin')
    expected_origins = ('https://github.com/s-yamanaka-droid/luna-news.git',
                        'https://github.com/s-yamanaka-droid/luna-news',
                        'git@github.com:s-yamanaka-droid/luna-news.git')
    if branch.returncode or branch.stdout.strip() != 'main' or origin.returncode or origin.stdout.strip() not in expected_origins:
        print('blocked: reviewed publication requires main and the existing luna-news origin')
        return False
    if git('diff', '--cached', '--quiet').returncode != 0:
        print('blocked: preexisting staged changes must be reviewed separately')
        return False
    changed = git('diff', '--name-only', '-z', 'HEAD', '--', 'docs')
    untracked = git('ls-files', '--others', '--exclude-standard', '-z', '--', 'docs')
    selected = {Path(name).as_posix() for name in paths}
    if changed.returncode or untracked.returncode or (
            set(filter(None, (changed.stdout + untracked.stdout).split('\0'))) - selected):
        print('blocked: unselected docs changes would make validation differ from publication')
        return False
    if git('add', '--', *paths).returncode:
        print('failed: selected file staging')
        return False
    if git('diff', '--quiet', '--', 'docs').returncode != 0:
        print('blocked: docs changed during staging; inspect the selected stage before retrying')
        return False
    from issue_check import check_local
    if not check_local(REPO_DIR / 'docs', date_str).get('ok'):
        print('blocked: issue technical validation failed; selected files remain staged for review')
        return False
    if git('diff', '--quiet', '--', 'docs').returncode != 0:
        print('blocked: docs changed during validation; inspect the selected stage before retrying')
        return False
    staged = git('diff', '--cached', '--quiet').returncode
    if staged not in (0, 1):
        print('failed: staged change inspection')
        return False
    if staged == 1 and git('commit', '-m', commit_msg).returncode:
        print('failed: commit or hook; publication stopped')
        return False
    # An unchanged index can still have an unpushed HEAD.
    if git('push', 'origin', 'HEAD:main').returncode:
        print('failed: push; production and seen state are unconfirmed')
        return False
    head = git('rev-parse', 'HEAD')
    remote = git('ls-remote', 'origin', 'refs/heads/main')
    if head.returncode or remote.returncode or not remote.stdout.split():
        print('failed: remote revision readback')
        return False
    if head.stdout.strip() != remote.stdout.split()[0]:
        print('failed: remote main differs from selected HEAD')
        return False
    print('git publication verified; production readback is a separate step')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true', required=True)
    parser.add_argument('--path', dest='paths', action='append', required=True)
    parser.add_argument('--date', required=True)
    parser.add_argument('--message', required=True)
    args = parser.parse_args()
    return 0 if git_push(args.message, paths=args.paths, date_str=args.date) else 1


if __name__ == '__main__':
    raise SystemExit(main())
