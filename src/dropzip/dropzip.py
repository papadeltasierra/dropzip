"""dropzip - tool for downloading Dropbox archives"""

import sys
import os
import logging
from argparse import Namespace, ArgumentParser
from typing import List
from dropbox import Dropbox  # type: ignore[import-untyped]
from dropbox.files import (  # type: ignore[import-untyped]
    ListFolderResult,
    FileMetadata,
    FolderMetadata,
)
from dropbox.common import PathRoot  # type: ignore[import-untyped]
from dropbox.exceptions import ApiError  # type: ignore[import-untyped]
from dropbox.users import FullAccount  # type: ignore[import-untyped]
from requests.models import Response
from requests.exceptions import ConnectionError
from zipfile import is_zipfile, ZipFile
from time import sleep
from pathvalidate import sanitize_filepath  # type: ignore[import-untyped]
import platform

# Ensure all downloaded dropbox ZIPfiles can be identified.
DOT_DROPBOX_ZIP = ".dp.zip"

log = logging.getLogger(__name__)
console = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter(fmt="%(message)s")
console.setFormatter(console_formatter)
log.addHandler(console)
log.setLevel(logging.DEBUG)


def init_logging(args: Namespace) -> None:
    """Initialize console logging levels based on user input."""
    console.setLevel(logging.WARNING)
    if args.verbose:
        console.setLevel(logging.INFO)
    if args.debug:
        console.setLevel(logging.DEBUG)
    if args.log_file:
        logging.basicConfig(filename=args.log_file, level=logging.DEBUG)


def parse_args(argv: List[str]) -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(
        description="Application to download Dropbox files and folders"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Move verbose reporting of actions"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable detailed 'debug' tracing"
    )
    parser.add_argument(
        "-a", "--access-token", required=True, help="Dropbox 'access token'"
    )
    parser.add_argument(
        "-s",
        "--source",
        default="",
        help="Root Dropbox folder from which to begin downloads",
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Root directory into which to download files & folders",
    )
    parser.add_argument(
        "-u",
        "--unzip",
        action="store_true",
        help="Unzip all ZIPped folders after all downloads have completed",
    )
    parser.add_argument(
        "-k",
        "--skip",
        action="store_true",
        help="Skip folders for which a ZIPfile already exists",
    )
    parser.add_argument(
        "-l",
        "--log-file",
        help="Debugging logfile",
        default=""
    )

    args = parser.parse_args(argv)

    # Determine platform target and make useful for sanitize_filepath.
    platform_system: str = platform.system()
    if platform_system not in ["Windows", "Linux"]:
        platform_system = "universal"

    setattr(args, "platform", platform_system)

    return args


def download_file(args: Namespace, dbx: Dropbox, source: str) -> None:
    """Download a single file from a Dropbox folder"""
    log.info("Downloading file '%s'...", source)
    rsp: Response
    _, rsp = dbx.files_download(source)

    # Write the result of the response to the target file.
    sources: List[str] = source.split("/")
    target: str = os.path.join(args.target, *sources)
    target = sanitize_filepath(target, platform=args.platform)

    dirname: str = os.path.dirname(target)
    try:
        os.makedirs(dirname)
    except FileExistsError:
        pass

    with open(target, "wb") as t:
        t.write(rsp.content)


def download_contents(args: Namespace, dbx: Dropbox, source: str) -> None:
    """Download everything below a folder"""
    log.info("Downloading contents below '%s'...", source)

    listFolderResult: ListFolderResult
    listFolderResult = dbx.files_list_folder(source)
    while True:
        for entry in listFolderResult.entries:
            log.debug("Entry metadata: %s", str(entry))
            item: str = source + "/" + entry.name

            if isinstance(entry, FileMetadata):
                download_file(args, dbx, item)
            elif isinstance(entry, FolderMetadata):
                download_folder(args, dbx, item)
            else:
                log.warning(
                    "Unrecognised item type: '%s', unable to download", type(entry)
                )

        if listFolderResult.has_more:
            log.debug("is_more is True")
            listFolderResult = dbx.files_list_folder_continue(listFolderResult.cursor)
        else:
            break


def download_folder(args: Namespace, dbx: Dropbox, folder: str) -> None:
    """Download a folder, ideally as a ZIPfile else as subfolders and files"""
    # Warning; folders contain '/' separators to need to be converted to '\'
    # if downloading to Windows.
    # Also strip leading "/" from folder name as this confuses os.path.join().
    folders: list[str] = folder[1:].split("/")
    target: str = os.path.join(args.target, *folders)
    target = target + DOT_DROPBOX_ZIP
    target = sanitize_filepath(target, platform=args.platform)
    log.debug("Folder: %s", folder)
    log.debug("Target: %s", target)

    download: bool = True
    if args.skip:
        try:
            status: os.stat_result = os.stat(target)
            if status.st_size > 0:
                log.info("Folder ZIPfile exists so skip downloading (again)")
                download = False
        except FileNotFoundError:
            pass

    if download:
        # Repeat the download attempt up to 5 times to handle network errors
        # as well as handling Dropbox errors that require the folder to be
        # downloaded in pieces.
        attempt: int = 1
        while True:
            log.info("Downloading folder '%s'...", folder)
            try:
                dirname: str = os.path.dirname(target)
                try:
                    os.makedirs(dirname)
                except FileExistsError:
                    pass

                dbx.files_download_zip_to_file(target, folder)
                log.debug("Download was successful")
                break

            except ApiError as dze:
                if dze.error.is_too_many_files():
                    log.warning(
                        "Download of '%s' failed (Too many files), trying to split...",
                        folder,
                    )
                    download_contents(args, dbx, folder)
                    break

                elif dze.error.is_too_large():
                    log.warning(
                        (
                            "Download of '%s' failed (ZIP file is too large), "
                            "trying to split..."
                        ),
                        folder,
                    )

                    # Assume this is a nested folder and try to download the
                    # sub-folders.
                    download_contents(args, dbx, folder)
                    break

                else:
                    log.warning(
                        "Download of '%s' failed (%s), trying to split...",
                        folder,
                        str(dze),
                    )

            except ConnectionError as rd:
                log.warning("Remote disconnected (attempt %d)...", attempt)
                attempt = attempt + 1
                if attempt >= 5:
                    log.error("Too many remote disconnections - failed")
                    raise rd

                sleep(2)


def unzip_all_files(args: Namespace) -> None:
    """Search for all files '*.zip' and unzip any found."""
    dirpath: str
    dirfiles: List[str]
    for dirpath, _, dirfiles in os.walk(args.target):
        filename: str
        for filename in dirfiles:
            if filename.endswith(DOT_DROPBOX_ZIP):
                fullname: str = os.path.join(dirpath, filename)
                if is_zipfile(filename):
                    zp: ZipFile = ZipFile(filename)
                    zp.extractall()

                    # Not deleting the ZIPfile at present.
                else:
                    log.warning("File '%s' is not a valid ZipFile.", fullname)


def main(argv: List[str]) -> int:
    """Mainline process to download as requested by user."""
    args: Namespace = parse_args(argv)
    init_logging(args)

    log.info("Downloading files/folders starting from '%s'", args.source)
    log.info("Storing files/folders below '%s'", args.target)

    # Validate dropbox.
    log.info("Connecting to dropbox...")
    dbx: Dropbox = Dropbox(args.access_token)

    # The default Dropbox access is only at the scope of the user who provided
    # the access token and cannot see the shared "team" folder.  So we have to
    # create a new Dropbox at root scope to enable the shared folders to also
    # be downloaded.
    fullAccount: FullAccount = dbx.users_get_current_account()
    log.debug("root namespace ID: %s", fullAccount.root_info.root_namespace_id)
    pathroot: PathRoot = PathRoot("root", fullAccount.root_info.root_namespace_id)
    dbx_root: Dropbox = dbx.with_path_root(pathroot)

    # We will download all the directories found below the source folder,
    # recursing if requireq because the folder is too large.
    download_contents(args, dbx_root, args.source)

    if args.unzip:
        # Attempt to unzip all ZIP files below the target directory.
        log.info("Unzipping all ZIPfiles below the target directory")
        unzip_all_files(args)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
