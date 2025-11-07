# DiscogsReleaseScrobbler
Discogs release scrobbler for Last.fm. You can scrobble individual tracks or the whole release. You can also use it to scrobble tracks from files in popular formats: .mp3 .flac .wav .ogg .m4a .opus.

![discogs_release_scrobbler](https://i.imgur.com/21BgIvm.gif)

## For Windows users (compiled release)
1.  [Download](https://github.com/astralgazelle/DiscogsReleaseScrobbler/releases) **both** the `.exe` file and the `config.ini` file. Place them in the **same folder**.
3.  Open `config.ini` with a text editor and fill in your API keys and login details.
4.  Run `DiscogsReleaseScrobbler.exe`.

---

## Using `.py` files (from source):
1.  Install Python 3.10 (currently supported version).
2.  Install required libraries:
    ```bash
    py -3.10 -m pip install PySide6 mutagen discogs-client pylast
    ```
3.  Open `config.ini` with a text editor and fill in your API keys and login details.
4.  Run the program **without a console window** using `pyw`:
    ```bash
    pyw -3.10 main.py
    ```

### Optional `.bat` file:
To run the app from a shortcut, you can create a `.bat` file in the same folder with this content:

```bat
@echo off
start "" pyw -3.G10 "%~dp0main.py"
```
