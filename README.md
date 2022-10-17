# Python Proxmox Client
A CLI Proxmox client to interract with Proxmox REST API

## Requirements

- A Proxmox Server, installed and configured.
- An authentication Token on your proxmox server.
- [Python3](https://www.python.org/downloads/), with pip

***
## Installation
1. Download the repository :
```
git clone https://github.com/danglock/Python-Proxmox-Client
```
2. Install the requirements :
```
cd Python-Proxmox-Client
pip install -r requirements.txt
```

***
## Usage

You launch the script without argument to load the default profile.
```
python3 .\main.py
```
> Note : if default profile doesn't exists, the script will create it.

Or you can specify a profile

```
python3 .\main.py -p "profilename"
```

> Note : if you sepcify an unexisting profile, the script will ask you to create a new one or choose another existing profile.



***
## Arguments

| Argument      | Description       |
|---------------|-------------------|
| -h --help     | Show help message |
| -p --profile  | Select a profile  |
