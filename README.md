

# DEBUGGER
Intended for running a code on a remote ec2 - given you are using Pycharm Community edition.

## Installation
Just run
```bash
pip install git+ssh://git@github.com/[this repo]
```


## Setup

- Make sure you have aws conigs properly setup


before moving forward (else it will remind you).

## Usage

        debugger [some python command]

## Repository Structure

```
|- debugger/    # Primary folder for code
|  |- instance_manager
      # handles instance creation only
|  |- pipeline_runner
      # handles instance later life and running on it
```

