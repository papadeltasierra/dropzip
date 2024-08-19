# dropzip
Download [Dropbox] archives via ZIP files.

This tool can download everything below a [Dropbox] folder (including the _top-most_ root folder) in a single action.  The overview below explains what it does.

# Your Dropbox Access Rights?
In order to download folders from [Dropbox], you need permissions to access them
and to do this for your Team's folders, it appears that you need _Administrator_ permissions.

When you come to select the permissions for the [Dropzip] application below,
select the permissions based on what permissions your account has.

# Installing This App
> In the ideal world, this would be a neatly packaged Python package but I wrote this in a rush to help someone download their files before their [Dropbox] subscription expired.  So here it is, if it is useful to you then great, but I'm not going to be maintaining this myself.

- If you have never used [Python], [Poetry], [Github] or [Git] before, stop now and go and learn about them before continuing.
- You will need [Python] v3, [Poetry] and [Git] installed on your computer
- Make a directory for [Dropzip]
- Clone [Dropzip]
- Update the dependencies for [Dropzip]
- Run [Dropzip]

Linux/bash...
```
$ mkdir dropzip
$ cd dropzip
$ git clone https://github.com/papadeltasierra/dropzip
$ poetry update
$ poetry run python src/dropzip/dropzip.py
```

Windows/cmd...
```
c:\users\someone> mkdir dropzip
c:\users\someone> cd dropzip
c:\users\Someone\dropzip> git clone https://github.com/papadeltasierra/dropzip
c:\users\Someone\dropzip> poetry update
c:\users\Someone\dropzip> poetry run python src/dropzip/dropzip.py
```

# Registering This App/Generating Access Token
## Registering the App
Before you can download any files or folders, you need to register this app. with your [Dropbox] account  You do this as follows:

- Login to [Dropbox] using your usual login credentials
- On the menu list down the left of the page, click on the _3x3 grid_ above **More**
- On the resulting pop-up, scroll down below **Explore more** and select **App Center** or just click on this link: [App Center]
- From the [App Center] page, on menu down the left side, select **Build an app**
- From the next page, there are two horizontal menus and the second one has an item **App Console** - click on this to open the next page
- Now click the blue box on the top-right that says **Create app**; you will see a new page **Create a new app on the DBX Platform**

> At this point don't worry - you really don't have to write the app but you do need to tell [Dropbox] that you are happy for the [Dropzip] app. to have access to your files.

- Below **1. Choose an API** click the **Scoped access New** element
- Choose access **Full Dropbox...**
- Give the app a suitable name; this is the name that [Dropbox] will know [Dropzip] as and [Dropbox] is a little picky about naming conventions.  I suggest you use **Folder and filename downloader** as the name.
- You are now presented with a configuration page for the app that has that has **Settings**, **Permissions**, **Branding** and **Analytics** tabs
- Select the **Permissions** tab
- If you are an **Adminstrator**, select these permissions and the hit **Submit** to request them:
    - `account_info.read`
    - `files.metadata.read`
    - `files.content.read`
    - If you also want to download your Team's files and folders...
       - `team_info.read`
       - `team_data.member`
       - `team_data.content.read`
       - `files.team_metadata.read`
- If you are **not an Adminstrator**, select these permissions
    - account_info.read
    - files.metadata.read
    - files.content.read
- Click **Submit** to request the permissions and this should work

## Generating An Access Token
An `access token` is effectively a _name and password_ in a single very long string and it is how the [Dropzip] box _logs on_ to [Dropbox] and how [Dropbox] knows that this instance of [Dropzip] is allowed to acces your files, **and only your files!**

> Note that access tokens are _time-limited_ meaning that the token you use today, might not work tomorrow and you might need to generate a new one.
>
> The instructions below follows on naturally from the instructions above if you are doing this for the first time.

Create an access token as follows.

- If you are not already on the setting page for the app (i.e. you are not doing this for the first time) then...
    - Login to [Dropbox] using your usual login credentials
    - On the menu list down the left of the pag, left handClick on the _3x3 grid_ above **More**
    - On the resulting pop-up, scroll down from **Explore more** and select **App Center** or just click on [App Center] here
    - From the [App Center] page, on menu down the left side, select **Build an app**
    - From this page, there are two horizontal menus and the second one has an item **App Console** - click on this
    - You should see your app here; click on it and you will get to the configuration page that has **Settings**, **Permissions**, **Branding** and **Analytics** tabs
- Select the **Settings** tab and scroll down to find **Generated access token**
- Press **Generate token** and a very long string, probably beginning `sl...`, will appear; this is your access token and [Dropzip] needs to know this in order to read the files and folders from [Dropbox]
- Click on the string to highlight it and use `Ctrl-C` to copy it
- Now make an environment variable containing this string to save having to keep copying it:

For Linux/bash...
```bash
$ ACCESS_TOKEN="<paste-your-long-string-here>"
```

For Windows/cmd...
```
C:\users\someone> set ACCESS_TOKEN="<paste-your-long-string-here>"
```

You are now ready to use the app. in anger.

# Usage
```
C:\Users\Someone\git\dropzip>C:\Users\PDS\git\dropzip>poetry run python src\dropzip\dropzip.py --help
usage: dropzip.py [-h] [-v] -a ACCESS_TOKEN [-s SOURCE] -t TARGET [-u] [-k] [-l LOG_FILE]

Application to download Dropbox files and folders

options:
  -h, --help            show this help message and exit
  -v, --verbose         More verbose reporting of actions; provide this option twice to see debug output.
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        Dropbox 'access token'
  -s SOURCE, --source SOURCE
                        Root Dropbox folder from which to begin downloads
  -t TARGET, --target TARGET
                        Root directory into which to download files & folders
  -u, --unzip           Unzip all ZIPped folders after all downloads have completed
  -k, --skip            Skip folders for which a ZIPfile already exists
  -l LOG_FILE, --log-file LOG_FILE
                        Debugging logfile
```

> Recomended: I suggest always using the `-v` or `--verbose` option as this will show you what [dropzip] is up to and gives you that _warm fuzzy feeling_ as you see it is downloading your files and folders.  Without this option, [dropzip] will silently do its work and it could be hours before _just finishes_.
>
> Note that **source** name always begins with a `/`.  [Dropbox] gives a slightly obtuse error if you don't obey this.

Assuming you set-up an environment variable for the access token, you might use the application like this:

Linux/bash...
```bash
$ poetry run python src/dropzip/dropzip.py -a $ACCESS_TOKEN -s '/My Name Here' -d ~/dropzip-contents -v -u
```

Windows/cmd
```
C:\users\Someone\dropzip> $ poetry run python src\dropzip\dropzip.py -a %ACCESS_TOKEN% -s '/My Name Here' -d D:\dropzip-contents -v -u
```
## Unzipping Files
I have observed that sometimes the standard Windows unzip mechanism cannot handle the files that [Dropzip] creates.  I recommend downloading the [7-zip] tool if you find this is a problem.

## Overview (or what does Dropzip actually do!)
This tool uses the [Dropbox for Python Developers] API to download files and folders
from a [Dropbox] account.  The process is roughly as follows:

- Starting from a [Dropbox] folder
  - Download folders as ZIPfiles and optionally unzip them after all downloads have completed
  - If a folder cannot be downloaded as a ZIPfile directly, then recursively
    - Download files in the folder as individual files
    - Attempt to download subfolders as ZIPfiles, unless they also cannot be downloaded in which case recurse to download these.

[Dropbox] folders cannot be downloaded directly as a ZIPfile for two main reasons:

1. The resulting ZIPfile would be too large
1. The [Dropbox] folder contains too many files.

If either of these conditions are encountered then [Dropzip] tries to download the files and sub-folders from the folder individually.

[Dropzip] can also use file and folder names that are invalid as Windows (and maybe Linux) file or folder names.  [Dropzip] uses the [pathvalidate] [Python] package to
sanitise names into a form that Windows is happy with.

## Debugging
If things go wrong then errors will appear on screen and they might explain what has happened but if not, and you need to ask folks perhapp using [Stackoverflow] or[Dropbox]'s own community pages, then you can capture diagnostics using one of these two options:

1. Add `-vv` or `--verbose --verbose` to the command line which will result in full debug output appearing on screen or
1. Add `-l <a-filename>` or `--logfile <a-filename>` which will write all the debugging information to the file names `a-filename`.<br/>**This is the recommended apporoach**

### Network Errors!
It has been observed that the [Dropbox for Python Developers] APIs sometimes hit
a _remote network disconnect_ exception.  This could be a problem at the [Dropbox] server or perhaps
one of the underlying Pythion libraries used by [Dropbox for Python Developers].
In any case when this happens, [Dropzip] will make 5 (five) attempts to retry the file/folder download before it gives up and fails that particular download.  This appears to be sufficient for downloads to be completed successfully and I have managed to download 10s GB of files in a single session.

### Dropbox Issue?
When attempting to download an entire set of Dropbox folders (personal and Team
folders as a single action), the error below was encountered.

This error has been reported to Dropbox who are investigating under this bug report: [Consistent 500 error, no status text, from files_download_zip_to_file].

```
File "C:\Users\Someone\git\dropzip\src\dropzip\dropzip.py", line 176, in download_folder
    dbx.files_download_zip_to_file(target, folder)
  File "C:\Users\Someone\AppData\Local\pypoetry\Cache\virtualenvs\dropzip-ocl8TPfY-py3.11\Lib\site-packages\dropbox\base.py", line 1525, in files_download_zip_to_file
    r = self.request(
        ^^^^^^^^^^^^^
  File "C:\Users\Someone\AppData\Local\pypoetry\Cache\virtualenvs\dropzip-ocl8TPfY-py3.11\Lib\site-packages\dropbox\dropbox_client.py", line 326, in request
    res = self.request_json_string_with_retry(host,
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Someone\AppData\Local\pypoetry\Cache\virtualenvs\dropzip-ocl8TPfY-py3.11\Lib\site-packages\dropbox\dropbox_client.py", line 476, in request_json_string_with_retry
    return self.request_json_string(host,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Someone\AppData\Local\pypoetry\Cache\virtualenvs\dropzip-ocl8TPfY-py3.11\Lib\site-packages\dropbox\dropbox_client.py", line 595, in request_json_string
    self.raise_dropbox_error_for_resp(r)
  File "C:\Users\Someone\AppData\Local\pypoetry\Cache\virtualenvs\dropzip-ocl8TPfY-py3.11\Lib\site-packages\dropbox\dropbox_client.py", line 620, in raise_dropbox_error_for_resp
    raise InternalServerError(request_id, res.status_code, res.text)
dropbox.exceptions.InternalServerError: InternalServerError('8cb6778eb30e4e658477df2c9c58a7cc', 500, '')
```


[Dropzip]: https://github.com/papadeltasierra/dropzip
[Dropbox]: https://dropbox.com
[App Center]: https://www.dropbox.com/apps
[Dropbox for Python Developers]: https://www.dropbox.com/developers/documentation/python#overview
[Consistent 500 error, no status text, from files_download_zip_to_file]: https://www.dropboxforum.com/t5/Discuss-Dropbox-Developer-API/Consistent-500-error-no-status-text-from-files-download-zip-to/td-p/787563
[Python]: https://www.python.org/
[Poetry]: https://python-poetry.org/
[Git]: https://git-scm.com/
[GitHub]: https://github.com
[stackoverflow]: https://stackoverflow.com
[7-zip]: https://www.7-zip.org/
[pathvalidate]: https://pypi.org/project/pathvalidate/
