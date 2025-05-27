## Linux

Open a `terminal` window.

Use python pip to uninstall the program with the following command:

```sh
python3 -m pip uninstall ${script}
```


### Externally managed base environments

For externally managed base environments, use one of the following.


#### VENVs

For virtual environments, first activate the virtual environment.

Then run the command:

```sh
pip uninstall ${script}
```


#### PIPX

For pipx installs, uninstall with:

```sh
pipx uninstall ${script}
```


#### Python altinstall

For python `altinstall`s, substitute python3 with your version of python (e.g. python3.13)

Here is an example:

```sh
python3.13 -m pip uninstall ${script}
```
