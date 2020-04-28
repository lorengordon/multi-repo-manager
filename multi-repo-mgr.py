import yaml
import os
import collections
import logging
import shutil
import subprocess

import git

DEFAULT_LOG_LEVEL = logging.DEBUG
LOG_LEVELS = collections.defaultdict(
    lambda: DEFAULT_LOG_LEVEL,
    {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }
)

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

log_file_name = ""
if not os.environ.get("AWS_EXECUTION_ENV"):
    log_file_name = 'multi-repo-mgr.log'

logging.basicConfig(
    filename=log_file_name,
    format='%(asctime)s.%(msecs)03dZ [%(name)s][%(levelname)-5s]: %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
    level=LOG_LEVELS[os.environ.get('LOG_LEVEL', '').lower()])
log = logging.getLogger(__name__)


# https://stackoverflow.com/a/13197763/12031185
class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def get_config():
    with open("config.yml", "r") as rl:
        return yaml.safe_load(rl.read())


def create_directory(path):
    try:
        os.mkdir(path)
        log.debug(f"created directory {path}")
    except OSError as e:
        log.error(f"Encountered error when creating {path}: {e}")
        return False


def add_content(repo, commit_message, branch_name):

    # add all files in working dir to a new commit in the newly created branch
    repo.git.add('--all')
    repo.git.commit(m=commit_message)

    # push the changes
    repo.git.push('--set-upstream', 'origin', branch_name)


def create_fork():
    # open a PR
    subprocess.check_call(['hub', 'fork', '--remote-name=origin'])


def clone_project(project_name, repos, github_org):
    if os.path.exists(project_name):
        for repo in repos:
            clone_path = f"{project_name}/{repo}"
            repo = f"git@github.com:{github_org}/{repo}.git"
            try:
                git.Repo.clone_from(repo, clone_path)
                log.debug(f"Cloned {repo} to {clone_path}")
            except git.exc.GitCommandError as e:
                # if the project has already been cloned, continue
                if "already exists" in e.stderr:
                    continue
                else:
                    log.error(f"git encountered an error: {e}")
    else:
        log.error("Project directory does not exist")


def create_branch(working_dir, branch_name):
    """Create a new branch."""
    # init the repo obj
    repo = git.Repo(working_dir)
    # create a new branch
    new_branch = repo.create_head(branch_name)
    # checkout the new branch
    new_branch.checkout()


def remove_dir(dir_name):
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)


if __name__ == "__main__":
    config = get_config()
    create_directory(config["project_name"])
    clone_project(**config)
    # for repo in config['repos']:
    #     working_dir = f"{config['project_name']}/{repo}"
    #     create_branch(working_dir, "ci-update")
    #     with cd(working_dir):
    #         create_fork()
