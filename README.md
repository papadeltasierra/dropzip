# dropzip
Download [Dropbox] archives via ZIP files

## Usage
```
C:\Users\Someone\git\dropzip>poetry run python src\dropzip\dropzip.py --help
usage: dropzip.py [-h] [-v] [-d] -a ACCESS_TOKEN [-s SOURCE] -t TARGET [-u] [-k]

Application to download Dropbox files and folders

options:
  -h, --help            show this help message and exit
  -v, --verbose         Move verbose reporting of actions
  -d, --debug           Enable detailed 'debug' tracing
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        Dropbox 'access token'
  -s SOURCE, --source SOURCE
                        Root Dropbox folder from which to begin downloads
  -t TARGET, --target TARGET
                        Root directory into which to download files & folders
  -u, --unzip           Unzip all ZIPped folders after all downloads have completed
  -k, --skip            Skip folders for which a ZIPfile already exists
```

## Overview
This tool uses the [Dropbox for Python Developers] API to download files and folders
from a Dropbox account.  The process is roughly as follows:

- Starting from a [Dropbox] folder
  - Download folders as ZIPfiles and optionally unzip them after all downloads have completed
  - If a folder cannot be downloaded as a ZIPfile directly, then recursively
    - Download files in the folder as individual files
    - Attempt to download subfolders as ZIPfiles, unless they also cannot be downloaded in which case recurse to download these.

[Dropbox] folders cannot be downloaded directly as a ZIPfile for two main reasons:

1. The resulting ZIPfile would be too large
1. The [Dropbox] folder contains too many files.

If either of these conditions are encountered then `dropzip` tries to download the files and sub-folders from the folder individually.

## Network Errors!
It has been observed that the [Dropbox for Python Developers] APIs sometimes hit
a _remote network disconnect_ exception.  This could be a problem at the [Dropbox] server or perhaps
one of the underlying Pythion libraries used by [Dropbox for Python Developers].
In any case when this happens, `dropzip` will make 5 (five) attempts to retry the file/folder download before it gives up and fails that particular download.


[Dropbox]: https://dropbox.com
[Dropbox for Python Developers]: https://www.dropbox.com/developers/documentation/python#overview