

# DEBUGGER
Intended for easy debugging of image-processing repo. 
It is based on manage.py [for ec2 creation]. These are the commands

## Installation
Just run
```bash
pip install git+ssh://git@github.com/[this repo]
```


## Setup

- Make sure you have aws conigs properly setup


before moving forward (else it will remind you).

## Usage

Creates an EC2 instance (so that debugging can be run on that)

        debugger start_ec2
        debugger stop_ec2
        debugger kill_ec2 



## Repository Structure

```
|- debugger/    # Primary folder for code
|  |- instance_manager
      # handles instance creation only
|  |- pipeline_runner
      # handles instance later life and running on it
```

