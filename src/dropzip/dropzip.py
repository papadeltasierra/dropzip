"""dropzip - tool for downloading Dropbox archives"""

import sys
import os
import logging
from argparse import Namespace, ArgumentParser
from typing import List
from dropbox import Dropbox
from dropbox.files import ListFolderResult, DownloadZipError
from requests.models import Response
from zipfile import is_zipfile, ZipFile

log = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter(fmt="%(message)s")
handler.setFormatter(log_formatter)
log.addHandler(handler)


def init_logging(args: Namespace) -> None:
    # !!PDS: Want to add file logging too.
    log.setLevel(logging.WARNING)
    if args.verbose:
        log.setLevel(logging.INFO)
    if args.debug:
        log.setLevel(logging.DEBUG)


def parse_args(argv: List[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-a", "--access-token", required="true")
    parser.add_argument("-s", "--source", default=".")
    parser.add_argument("-t", "--target", required="true")
    parser.add_argument("-u", "--unzip", action="store_true")

    args = parser.parse_args(argv)
    return args


def download_file(args: Namespace, dbx: Dropbox, source: str) -> None:

    log.debug("Downloading file '%s'...", source)
    rsp: Response
    _, rsp = dbx.files_download(source)

    # Write the result of the response to the target file.
    target: str = os.path.join(args.target, source)
    target = target.replace("/", "\\")
    with open(target, "r") as t:
        t.write(rsp.content)


def download_contents(args: Namespace, dbx: Dropbox, source: str) -> None:
    log.info("Downloading contents below '%s'...", source)
    for entry in dbx.files_list_folder(source).entries:
        item: str = source + "/" + entry.name
        if isinstance(entry, dropbox.files.FileMetadata):
            download_file(args, dbx, item)
        elif isinstance(entry, dropbox.files.FolderMetadata):
            download_folder(args, dbx, item)
        else:
            log.warning("Unrecognised item type: '%s', unable to download", type(entry))


def download_folder(args: Namespace, dbx: Dropbox, folder: str) -> None:
    # Warning; folders contain '/' separators to need to be converted to '\'
    # if downloading to Windows.
    target: str = os.path.join(args.target, folder)
    target = target.replace("/", "\\")

    log.info("Downloading folder '%s'...", folder)
    try:
        dbx.files_download_zip_to_file(target, folder)
        log.debug("Download was successful")

    except DownloadZipError as dze:
        if dze.is_too_many_files():
            log.warning("Download of '%s' failed (Too many files), trying to split...", folder)
            download_contents(args, dbx, folder)

        elif dze.is_too_large():
            log.warning("Download of '%s' failed (ZIP file is too large), trying to split...", folder)

            # Assume this is a nested folder and try to download the sub-folders.
            download_contents(args, dbx, folder)

        else:
            log.warning("Download of '%s' failed (%s), trying to split...", folder, str(dze))


def unzip_all_files(args: Namespace) -> None:
    dirpath: str
    dirfiles: List[str]
    for dirpath, _, dirfiles in os.walk(args.target):
        filename: str
        for filename in dirfiles:
            if filename.endswith(".zip"):
                fullname:str  = os.path.join(dirpath, filename)
                if is_zipfile(filename):
                    zp: ZipFile = ZipFile(filename)
                    zp.extractall()

                    # Not deleting the ZIPfile at present.
                else:
                    log.warning("File '%s' is not a valid ZipFile.", fullname)


def main(argv: List[str]) -> int:
    args: Namespace = parse_args(argv)
    init_logging(args)

    log.info("Downloading files/folders starting from '%s'", args.source)
    log.info("Storing files/folders below '%s'", args.target)

    # Validate dropbox.
    log.info("Connecting to dropbox...")
    dbx: Dropbox = Dropbox(args.access_token)
    dbx.users_get_current_account()

    # We will download all the directories found below the source folder,
    # recursing if requireq because the folder is too large.
    download_contents(args, dbx, args.source)

    if args.unzip:
        # Attempt to unzip all ZIP files below the target directory.
        unzip_all_files(args)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
