# DiscogsReleaseScrobbler

1. Install Python 3.10 (currently supported version).
2. Install libraries `PySide6`, `mutagen`, `discogs_client` and `pylast`:

```bash
py -3.10 -m pip install --user PySide6 mutagen discogs_client pylast
```

3. Fill in your your last.fm credentials, last.fm API keys and Discogs Personal Access Token in the config.ini file.

4. Run program using terminal:

```bash
py -3.10 main.py
```
Or create and run a `.bat` file with this content:

```bash
@echo off
py -3.10 "%~dp0main.py"
pause
```
