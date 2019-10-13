#!/usr/bin/env python3

import os
import yaml
import git
import socket
import time

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
    repo = git.Repo(path)
    reponame = path.split(os.sep)[-1]
    updates = list()
    for remote in repo.remotes:
        for fetch in remote.fetch():
            if fetch.note:
                updates.append(fetch.note)
    if not updates:     # The list holding updates remained empty
        return None
    else:
        return { "name": reponame,
                 "path": path,
                 "updates": updates }

def drop_updates(update_dict, maildir_path):
    now = time.localtime()
    filename = "{}_{}.{}".format(
        time.strftime("%s", now),
        update_dict["name"],
        socket.gethostname()
    )
    tmp_mailfile = os.path.join(maildir_path, "tmp", filename)
    new_mailfile = os.path.join(maildir_path, "new", filename)
    with open(tmp_mailfile) as f:
        f.writelines([
            "Date: {}".format(time.strftime("%a, %d %b %Y %H:%M:%S %z"), now),
            "From: repodrop@{}".format(socket.gethostname()),
            "Subject: [{}] {} remote updates".format(
                update_dict["name"],
                len(update_dict["updates"])
            ),
            ""
        ])
    for note in update_dict["updates"]:
        f.writeline(note)
    f.writeline()
    f.writeline("Repo path: {}".format(update_dict["path"]))
    os.rename(tmp_mailfile, new_mailfile)   # Maildir convention

def ensure_maildir(path):
    for subdir in ["cur", "new", "tmp"]:
        subdir = os.path.join(path, subdir)
        os.makedirs(subdir, exist_ok=True)

if __name__ == "__main__":
    config = read_config()
    ensure_maildir(config["maildir"])
    updates = map(fetch_updates, config["git-repositories"])
    updates = filter(lambda x: x != None, updates)
    for update_dict in updates:
        drop_updates(update_dict, config["maildir"])
