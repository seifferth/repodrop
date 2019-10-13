# RepoDrop

RepoDrop is a python script that fetches all remote heads for local
git repositories and, in case there were remote updates, delivers an
overview to some local maildir folder. It does with git repositories
what [rssdrop](https://github.com/petronny/rssdrop) does with rss and
atom feeds.

## Dependencies

- git

## Installing

`repodrop.py` is a standalone script that only relies on the python3
standard library. Copying it into some folder included in `PATH`
and marking it as executable should suffice for installing. Renaming
the executable to `repodrop` (i. e. removing the `.py`-Extension) is
encouraged.

## Configuration

The configuration file is located at `~/.config/repodrop/config.yaml`. It
contains two entries: The mailfolder notifications should be delivered
to and a list of paths to local git repositories that should be checked
for remote updates. An example configuration file could look like this:

```yaml
maildir: /home/user/mail/repodrop

git-repositories:
  - /full/path/to/first/repo
  - /full/path/to/second/repo
  - /full/path/to/third/repo
```
