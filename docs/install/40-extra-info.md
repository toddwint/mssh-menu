# Extra Info

## History file

The selections are saved in a history file. The location of the history file is:

- `$HOME/.local/share/${script}/${script}.json`

You can delete this file to clear your history. 

This folder is not automatically removed on program uninstallation. You can manually delete it without issues.


## Shell Completions

This program includes shell completions which should be installed by default to your local user's share directory (e.g. `$HOME/.local/share`).

  - `bash`
    - `$HOME/.local/share/bash-completion/completions/${script}`
  - `zsh`
    - `$HOME/.local/share/zsh/site-functions/_${script}`
  - `fish`
    - `$HOME/.local/share/fish/vendor_completions.d/${script}.fish`

If shell completions are not working, this program includes an option to provide the shell completion to stdout.

Run the command:

```sh
${script} --completion <shell>
```

Where `<shell>` is the name of your shell.

Using shell redirection you can place these commands in a file where your shell looks for shell completions. This part you will have to research for your shell.


## TMUX defaults

Here is my default `.tmux.conf` file for reference.

`mssh-menu` will automatically take care of setting the `base-index` and `pane-base-index` to 1.

`mssh-menu` will not configure the `default-terminal`, `history-limit`, or `mouse` options. If you want those options, create a `.tmux.conf` file in your user's home directory, and add the contents below to that file.

```
# Improve colors
set -g default-terminal screen-256color

# Set scrollback buffer to 10000
set -g history-limit 10000

# Enable mouse mode (tmux 2.1 and above)
set -g mouse on

# Set first windows and pane to index of 1 (instead of zero)
set -g base-index 1
set -g pane-base-index 1
```
