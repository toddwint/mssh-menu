## Linux

Install the prerequisites using the instructions on the respective websites.

The program is installed using `python` and the `pip` module. There are no Python dependencies to this program. All code utilizes only the Python standard library.

If you do not wish to install this package to your system, a Python zipapp is included (`.pyz`). If you system has Python installed, the Pyzip zipapp can simply be downloaded and ran. It is located in the `releases` folder or on the github releases page and is named `${script}.pyz`.

Two installation files are included in the `releases` folder or on the github releases page. One is a Python "wheel" file (`.whl`) and the other one is a compressed `tar` file (`.tar.gz`). Either file can install the program, although it is recommended to install the `.whl`. The following are insturctions to install the `.whl`.

Open a `terminal` window.

Install with the following command:

```sh
python3 -m pip install <${script}-{version}-py3-none-{platform}.whl>
```

Python `pip` installs the program, the `man` page, and shell completions.


### Externally Managed Base Environments

On newer distributions of Debian, Ubuntu, and more [PEP 668](https://peps.python.org/pep-0668/) introduces challenges to the user to install Python packages, even if they do not modify the system packages.

If you are on one of these systems (you most likely are), you will receive a message like the following:

```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make
    sure you have python3-full installed.

    If you wish to install a non-Debian packaged Python application,
    it may be easiest to use pipx install xyz, which will manage a
    virtual environment for you. Make sure you have pipx installed.

    See /usr/share/doc/python3.12/README.venv for more information.

note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.
hint: See PEP 668 for the detailed specification.
```

There are a few ways to work around this. Because there is not a `.deb` or `.rpm` created for this project you cannot install this program using your system package manager. That leaves creating a virtual environment, using `pipx`, or installing an `altinstall` of python.


#### VENV Install

A virtual environment can be created for installing this program. The downside to this method is the user must activate the virtual environment before being able to access the program. Once the virtual environment is activated the program and the man page are available to the user. However, I notice the shell completions are not automatically working as the virtual environment does not set the proper paths for shell-completions. More on this later.

To install using a virtual environment, first install `python3-venv`.

```sh
sudo apt update
sudo apt install python3-venv
```

Then create the virtual environment like this:

```sh
python3 -m venv $HOME/.venv/python3
```

Activate the `venv`:

```sh
source $HOME/.venv/python3/bin/activate
```

Then install this program using `pip`.

```sh
pip install <${script}-{version}-py3-none-{platform}.whl>
```

In my observations, the `venv`'s `activate` script does not set the paths needed for shell-completions. You can run the following commands at the command line for your respective shell to set the correct path and remove any existing completions for this program.

`bash`
```sh
complete -r ${script}
XDG_DATA_DIRS="$VIRTUAL_ENV/share:$XDG_DATA_DIRS"
```

`zsh`
```sh
FPATH="$VIRTUAL_ENV/share/zsh/site-functions:$FPATH"
compinit
```

`fish`
```sh
set -gx fish_complete_path $VIRTUAL_ENV/share/fish/vendor_completions.d $fish_complete_path
```

I will leave it to you to decide if and how to modify the python venv activate script to avoid typing these commands every time.


#### PIPX Install

PIPX has the benefit of installing the program into a virtual environment without forcing the user to run a command to enter the virtual environment. PIPX handles creating the virtual environment for the program and running the program in the virtual environment transparently. PIPX installs the program and the man pages. The shell-completions are copied over, but will not work as the location is not on the path. More on this later.

To install using `pipx` first install `pipx` on your system with the commands:

```sh
sudo apt update
sudo apt install pipx
pipx ensurepath
```

Then install this package with this command:

```sh
pipx install <${script}-{version}-py3-none-{platform}.whl>
```

One way to make shell-completions work is to add the pipx path to this programs's share folder and remove any existing completions for this program:

`bash`
```sh
complete -r ${script}
XDG_DATA_DIRS="$HOME/.local/share/pipx/venvs/${script}/share:$XDG_DATA_DIRS"
```

`zsh`
```sh
FPATH="$HOME/.local/share/pipx/venvs/${script}/share/zsh/site-functions:$FPATH"
compinit
```

`fish`
```sh
set -gx fish_complete_path $HOME/.local/share/pipx/venvs/${script}/share/fish/vendor_completions.d $fish_complete_path
```

I will leave it to you to decide if and how to modify your system to avoid typing these commands every time.

Another way to make shell-completions work with pipx is to run the `${script} --completion <shell>` option. For details on this method see the section below [Shell Completions](#shell-completions)


#### Python Altinstall

Python altinstall installs an alternate version of Python on your system by compiling the python source and then performing an `altinstall`. Use this method if you want a user version of Python on your system that isn't externally managed by your Linux distribution's package manager, and you don't care to create a virtual environment to run this program. You can use the altinstall of Python for anything Python related. The altinstall method will install the program, man pages, and shell-completions.

You should reference [Building Python (Python docs)](https://docs.python.org/3/using/unix.html#building-python) for instructions.

Here I will summarize the steps for an example system.

Install the prerequisites:

```sh
sudo apt update
sudo apt install build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev
```

Download the Python source from [Python](https://www.python.org/downloads/).

Extract the archive and cd into the created directory.

```sh
tar -xvf Python-MAJOR.MINOR.PATCH.tar.xz
cd Python-MAJOR.MINOR.PATCH
```

Then use these steps to build python.

```sh
./configure --enable-optimizations
make
make test
sudo make altinstall
```

You should now have an alternate installation of Python on your system.

Install this package by replacing `python3` with your alternate installation version of Python (e.g. `python3.13`).

Here is an example how to do that.

```sh
python3.13 -m pip install --upgrade pip
python3.13 -m pip install <${script}-{version}-py3-none-{platform}.whl>
```
