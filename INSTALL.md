# Installation

This guide covers installing oMLX into Sublime Text 4 on macOS, Linux, and Windows. For configuration and usage after install, see the [README](README.md).

## Requirements

- **Sublime Text 4, build 4050 or newer.** The plugin uses the Python 3.8 plugin host introduced in build 4050. Check your build with `Help -> About Sublime Text` (macOS: `Sublime Text -> About Sublime Text`).
- **Network access** if you plan to use a hosted provider (OpenAI, Anthropic, OpenRouter, DeepSeek, or a custom OpenAI-compatible endpoint). No network is required for oMLX.
- **Required for default setup: [oMLX](https://github.com/jundot/omlx)** for optimized Mac inference (or skip to Path B for hosted providers).

## Installation methods

### Package Control (recommended)

Once sublime-oMLX is listed on [Package Control](https://packagecontrol.io):

1. Open the command palette (`Ctrl+Shift+P` / `Cmd+Shift+P`).
2. Run `Package Control: Install Package`.
3. Search for `oMLX` and install.
4. Restart Sublime Text.

### Manual install (development / pre-release)

To install from the git repository directly:

#### Locate your Packages directory

The Sublime `Packages` directory is where third-party packages live. From inside Sublime, run `Preferences -> Browse Packages...` to open it. The default paths are:

- **macOS:** `~/Library/Application Support/Sublime Text/Packages/`
- **Linux:** `~/.config/sublime-text/Packages/`
- **Windows:** `%APPDATA%\Sublime Text\Packages\`

These paths are referenced as `<Packages>` below.

#### Option A — clone directly into the Packages directory

```sh
cd <Packages>
git clone https://github.com/xraid/sublime-omlx.git sublime-omlx
```

#### Option B — clone elsewhere and symlink

Useful if you want the working copy somewhere outside Sublime's Packages directory (for example, alongside your other repos).

```sh
git clone https://github.com/xraid/sublime-omlx.git ~/git/sublime-omlx
ln -s ~/git/sublime-omlx '<Packages>/sublime-omlx'
```

On Windows, use `mklink /D` from an elevated `cmd.exe`:

```cmd
mklink /D "%APPDATA%\Sublime Text\Packages\sublime-omlx" "C:\path\to\your\clone"
```

#### Restart Sublime Text

After cloning or symlinking, restart Sublime Text so the plugin host loads the package.

## Verify the install

1. Open the command palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and type `oMLX:`. You should see entries like `oMLX: Open Chat`, `oMLX: Choose Provider`, `oMLX: Show Status`.
2. Run `oMLX: Open Chat`. A new tab named **oMLX Chat** should appear with a `<user> ` prompt at the bottom.
3. Run `oMLX: Show Status`. The status panel should report the active provider, model, base URL, and a list of available models.

If any of these fail, open the Sublime console with ``Ctrl+` `` and look for `sublime-llm` log lines.

## First-time setup

### Path A — local with oMLX (optimized for Mac)

1. Install [oMLX](https://github.com/jundot/omlx) and start the server (follow oMLX documentation for your setup).
2. Generate an API key in the oMLX admin interface.
3. Copy `config.example.json` to `~/.config/sublime-omlx/config.json` and add your oMLX API key:

   ```sh
   mkdir -p ~/.config/sublime-omlx
   cp <Packages>/sublime-omlx/config.example.json ~/.config/sublime-omlx/config.json
   chmod 600 ~/.config/sublime-omlx/config.json
   [subl|vim|nano] ~/.config/sublime-omlx/config.json
   ```

   Add your oMLX API key in the `omlx` provider block (see example below).

4. In Sublime: `Tools -> oMLX: Open Chat` or command palette: `oMLX: Open Chat`.
5. Type a message in the chat view's input region and press `Ctrl+Enter` (macOS: `Cmd+Enter`) to send.

### Path B — hosted provider (OpenAI, Anthropic, OpenRouter, DeepSeek, custom)

1. Open `Preferences -> Package Settings -> oMLX -> Settings` and set `provider` and `model`. Example:

   ```json
   {
     "provider": "anthropic",
     "model": "claude-opus-4-7"
   }
   ```

2. Provide an API key. The recommended path is the external config file at `~/.config/sublime-omlx/config.json` (macOS/Linux) or `%APPDATA%\sublime-omlx\config.json` (Windows). A template is shipped at [`config.example.json`](config.example.json) at the repo root — copy it into place and edit:

   ```sh
   mkdir -p ~/.config/sublime-omlx
   cp <Packages>/sublime-omlx/config.example.json ~/.config/sublime-omlx/config.json
   chmod 600 ~/.config/sublime-omlx/config.json
   [subl|vim|nano] ~/.config/sublime-omlx/config.json
   ```

   The shape stores provider-level settings under `providers.<name>`:

   ```json
   {
     "active_provider": "omlx",
     "providers": {
       "omlx": {
         "api_key": "your-key-from-omlx-admin",
         "base_url": "http://localhost:8000/v1",
         "model": "Qwen2.5-Coder-1.5B-Instruct-MLX-8bit"
       },
       "anthropic": {
         "api_key": "sk-ant-...",
         "model": "claude-opus-4-7"
       }
     }
   }
   ```

   Any value containing `REPLACE_ME` is treated as a placeholder and ignored, so an unedited copy is harmless. The plugin enforces `0600` permissions on this file when it writes it. Existing legacy key-only `secrets.json` installs are still readable for backward compatibility. See the [README](README.md#external-provider-config-and-api-keys) for the full key-resolution chain.

3. Run `oMLX: Show External Config Status` to confirm the key was picked up.
4. Send a test message via `oMLX: Open Chat`.

## Updating

### Package Control

Updates land automatically. Run `Package Control: Upgrade Package` to pull the newest tagged release immediately.

### Manual install

Pull from the clone:

```sh
cd '<Packages>/sublime-omlx'   # or wherever your clone lives
git pull
```

Sublime auto-reloads the plugin on file change.

## Uninstall

### Package Control

Run `Package Control: Remove Package` and pick `LLM`.

### Manual install

Remove the directory or symlink from the Packages directory:

```sh
rm -rf '<Packages>/sublime-omlx'   # or `unlink` if it's a symlink
```

Optional cleanup of user state:

- Per-project chat transcripts: `<Packages>/User/sublime-omlx/chats/`
- User overrides: `<Packages>/User/oMLX.sublime-settings`
- External config file: `~/.config/sublime-omlx/config.json` (macOS/Linux) or `%APPDATA%\sublime-omlx\config.json` (Windows)
- Legacy key-only file: existing `secrets.json` installs are still readable for backward compatibility; new installs should use `config.json`

## Troubleshooting

**Commands don't appear in the palette.** Confirm the directory under `<Packages>` is named exactly `sublime-omlx` and that you restarted Sublime after install.

**`failed to assign ChatMarkdown syntax` in the console.** Same root cause — the syntax file is loaded by the path `Packages/sublime-omlx/ChatMarkdown.sublime-syntax`. Rename the directory to `sublime-omlx`.

**`oMLX is not running`.** Start the oMLX server following the [oMLX documentation](https://github.com/jundot/omlx) and confirm it's reachable at `http://localhost:8000/v1` (or your configured `omlx_base_url`). Run `oMLX: Show Status` to check the provider health.

**`MISSING_CREDENTIAL` or `BAD_CREDENTIAL` for a hosted provider.** Run `oMLX: Show External Config Status` to see where each key was resolved from. On macOS, GUI apps launched from the Dock or Spotlight don't inherit your shell's environment variables — use the external config file instead, or launch Sublime from a terminal with `subl`.

For other issues, see the [Troubleshooting section of the README](README.md#troubleshooting).
