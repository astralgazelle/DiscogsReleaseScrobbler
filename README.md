# DiscogsReleaseScrobbler
A Discogs release scrobbler for Last.fm. It allows you to scrobble individual tracks or full releases. You can also scrobble directly from local files in popular formats: .mp3, .flac, .wav, .ogg, .m4a, and .opus.

The program **supports scrobbling tracks shorter than 30s** by automatically rounding up their length to 30 seconds.

![discogs_release_scrobbler](https://i.imgur.com/21BgIvm.gif)

## Instruction for Windows users (compiled release)
1.  [Download](https://github.com/astralgazelle/DiscogsReleaseScrobbler/releases) **both** the `DiscogsReleaseScrobbler.exe` file and the `config.ini` file. Place them in the **same folder**.
3.  Open `config.ini` with a text editor and fill in your [Last.fm API keys](https://www.last.fm/api/account/create), your [Discogs token](https://www.discogs.com/settings/developers) and your Last.fm login and password.
4.  Run `DiscogsReleaseScrobbler.exe`.

---

## Instruction for source files:
1.  Install Python 3.10 (currently supported version).
2.  Install required libraries:
    ```bash
    py -3.10 -m pip install PySide6 mutagen discogs-client pylast
    ```
3.  Open `config.ini` with a text editor and fill in your [Last.fm API keys](https://www.last.fm/api/account/create), your [Discogs token](https://www.discogs.com/settings/developers) and your Last.fm login and password.
4.  Run the program with terminal:
    ```bash
    pyw -3.10 main.py
    ```

#### Optional `.bat` file:
To run the app from a shortcut, you can create a `.bat` file in the same folder with this content:

```bat
@echo off
start "" pyw -3.10 "%~dp0main.py"
```





