# ricercar plugins

A community index of **source plugins** for
[ricercar](https://github.com/ricercar-player/ricercar), the bit-perfect music player
for Linux. Plugins add catalogues (music services, remote libraries,
podcasts…) through the [plugin protocol](https://github.com/ricercar-player/ricercar/blob/main/docs/plugins.md).

**This repository hosts no plugin code.** Each entry is a small file that
points at its author's repository and at the binaries the author publishes.

> [!WARNING]
> Plugins are written by third parties. They are **not reviewed** by the
> ricercar project, and a listing is not an endorsement. A plugin runs with
> your permissions: install only plugins you trust. Each author is
> responsible for their plugin, and for respecting the terms of the services
> it uses; so is each user who installs one.

## Installing a plugin

- **In ricercar (0.4.0 and later):** open **Plugins** in the sidebar, pick an
  entry and click **Install**. ricercar downloads the binary for your
  computer from the author's link, checks it against the SHA-256 written in
  the entry, and asks you first. Updates and removal happen on the same page.
- **By hand:** follow the plugin's own instructions, then declare it in
  `~/.config/ricercar/config.toml`:

  ```toml
  [[plugins]]
  id = "example"
  command = "/path/to/example-plugin"
  ```

## Catalogue

<!-- catalogue:begin -->
| Plugin | Description | Author | Licence | Version | Builds |
|---|---|---|---|---|---|
| [Demo Music (reference)](https://github.com/ricercar-player/ricercar) | Reference implementation of the plugin protocol, for plugin authors. Serves generated test tones from your own computer; sign-in code DEMO. | ricercar | MIT | 1.0.0 | from source |
| [Jellyfin](https://github.com/ricercar-player/ricercar-jellyfin) | Browse, search and play the music of your own Jellyfin server: albums, artists, playlists, favourites and folders, in ricercar's library next to your local music. Original files, bit for bit; FLAC transcode only when your DAC cannot take a file's rate. Sign in with Quick Connect or your password. | ricercar-player | MIT | 0.2.0 | x86_64, aarch64 |
| [Live Music Archive](https://github.com/ricercar-player/ricercar-archive) | Hundreds of thousands of concert recordings from the Internet Archive's Live Music Archive, free to share, most of them lossless. Browse popular, recent and on-this-day shows or an artist's recordings, search, and keep favourites in your library. No account. Original FLAC files, bit for bit. | ricercar-player | MIT | 0.2.0 | x86_64, aarch64 |
| [Plex](https://github.com/ricercar-player/ricercar-plex) | Browse, search and play the music of your own Plex Media Server. Albums, artists and playlists merged into your library, recent albums on Home, favourites shared with Plex; plays show on the server. Original files, bit for bit; FLAC at a rate your DAC takes when it cannot play the file's. | ricercar-player | MIT | 0.2.0 | x86_64, aarch64 |
| [Qobuz (unofficial)](https://github.com/anon7627/ricercar-qconnect) | Browse and search your Qobuz library, and stream it at the best quality your DAC plays natively. Qobuz Connect support: pick your player from the Qobuz app and control it from your phone. Unofficial, uses the Qobuz web API; needs a Qobuz subscription. | anon7627 | MIT | 0.1.3 | x86_64 |
| [Subsonic](https://github.com/ricercar-player/ricercar-subsonic) | Browse, search and play the music of your own Subsonic-compatible server: Navidrome, Gonic, Airsonic-Advanced, LMS, Ampache. Albums, artists, playlists and starred items, merged into your library, and Home shelves of recent, most played and random albums. Original files, bit for bit; FLAC at a rate your DAC takes when the server can transcode (Navidrome 0.64+). | ricercar-player | MIT | 0.2.0 | x86_64, aarch64 |
<!-- catalogue:end -->

## Adding your plugin

Open a pull request that adds `plugins/<id>.toml`:

```toml
id = "example"                 # [a-z0-9-], unique, used in plugin:// URIs
name = "Example Music"
description = "One or two sentences, 400 characters at most."
author = "your name or handle"
license = "MIT"                # your plugin's licence
repository = "https://github.com/you/ricercar-example"
homepage = "https://example.org"   # optional
version = "1.2.0"              # the release the assets below come from
protocol = 1                   # plugin protocol version
capabilities = ["auth", "browse", "search", "resolve"]
args = []                      # optional, passed to the binary

# One prebuilt, self-contained executable per architecture, published by
# you (a GitHub release asset, for example). Without assets the entry is
# listed and users build or install it themselves.
[[assets]]
arch = "x86_64"
url = "https://github.com/you/ricercar-example/releases/download/v1.2.0/example-x86_64"
sha256 = "…"                   # sha256sum example-x86_64

[[assets]]
arch = "aarch64"
url = "https://github.com/you/ricercar-example/releases/download/v1.2.0/example-aarch64"
sha256 = "…"
```

Then run `python3 scripts/build.py`, which checks every entry and updates
`index.json` and the table above, and commit the result. CI runs the same
check on every pull request.

To publish a new version, update `version` and the assets in your entry.
Users see an **Update** button in ricercar.

Entries are merged when they are well-formed and the links work. Nobody here
reviews what a plugin does. An entry can be removed at its author's request,
or when its links are dead or it is shown to be malicious.

## Format notes

- `capabilities`: `auth`, `browse`, `search`, `resolve`, `favorites`,
  `reporting`, `remote_control`, `library` (see the protocol).
- All URLs are `https`. Digests are lowercase hex SHA-256 of the exact file
  behind `url`.
- `index.json` is generated: ricercar reads it from
  `https://raw.githubusercontent.com/ricercar-player/ricercar-plugins/main/index.json`
  only when its Plugins page opens.

## Licence

The index and scripts are under the MIT licence. Each plugin keeps its own
licence, stated in its entry.
