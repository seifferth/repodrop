#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-3.0+

import sys
import os
import yaml
import socket
import time
import subprocess
import multiprocessing

config_file = os.path.join(
    os.environ['HOME'],
    ".config",
    "repodrop",
    "config.yaml"
)

def read_config():
    with open(config_file, "r") as f:
        return yaml.safe_load(f)

def fetch_updates(path):
    """
    Get remote updates for a git repository. This does not update remotes
    as a precaution, since the repodrop might still fail at this stage.
    """
    reponame = path.strip(os.sep).split(os.sep)[-1]
    updates = subprocess.run(
        ["git", "-C", path, "fetch", "--all", "--dry-run"],
        check=True,
        capture_output=True,
        text=True
    ).stderr
    if updates:     # String is not empty
        return { "name": reponame,
                 "path": path,
                 "updates": updates }
    else:
        return None

def update_remotes(path):
    """
    Do a real update to the remotes in a particular repo. This should
    be run after the notification has been delivered successfully.
    """
    subprocess.run(
        ["git", "-C", path, "fetch", "--all"],
        check=True,
        capture_output=True,
        text=True
    )

def drop_updates(update_dict, maildir_path):
    now = time.localtime()
    seconds = time.strftime("%s", now)
    rfc_time = time.strftime("%a, %d %b %Y %H:%M:%S %z", now)
    filename = "{}_{}.{}".format(
        seconds,
        update_dict["name"],
        socket.gethostname()
    )
    tmp_mailfile = os.path.join(maildir_path, "tmp", filename)
    new_mailfile = os.path.join(maildir_path, "new", filename)
    with open(tmp_mailfile, "w") as f:
        f.writelines([
            "Date: {}\n".format(rfc_time),
            "From: RepoDrop@{}\n".format(socket.gethostname()),
            "Subject: Remote updates for {}\n".format(update_dict["name"]),
            "\n"
        ])
        f.write(update_dict["updates"])
        f.write("\n")
        f.write("Repo path: {}\n".format(update_dict["path"]))
    os.rename(tmp_mailfile, new_mailfile)   # Maildir convention
    update_remotes(update_dict["path"])

def ensure_maildir(path):
    for subdir in ["cur", "new", "tmp"]:
        subdir = os.path.join(path, subdir)
        os.makedirs(subdir, exist_ok=True)

_cli_help = f"""
Usage: repodrop [--help]

This command takes no command line arguments. All configuration is read
from a configuration file at '{config_file}'.
""".lstrip()

if __name__ == "__main__":
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print(_cli_help)
        exit(0)
    config = read_config()
    if config.get("git-repositories") == None:
        exit(0)     # Skip everything if no repositories are specified
    ensure_maildir(config["maildir"])
    if "max-threads" not in config.keys():
        config["max-threads"] = 4
    threads = min(config["max-threads"], len(config["git-repositories"]))
    with multiprocessing.Pool(threads) as pool:
        updates = pool.map(fetch_updates, config["git-repositories"])
    updates = filter(lambda x: x != None, updates)
    for update_dict in updates:
        drop_updates(update_dict, config["maildir"])
