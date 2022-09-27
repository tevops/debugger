

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
- Make sure you have your **analytics.pem** file and **run**


```bash
export ANALYTICS_PEM=/path/to/your/analytcs.pem
```
before moving forward (else it will remind you).

## Usage

        debugger create_ec2 [kind] [environment]
where

        kind: can be either of analytics_[size] 
        environment: is by default 'release'
        
Currently supported values for argument [kind]


             [kind]                      [ami]                      [ec2]
        deep_learning |        ami-0b325837d9a2eac7f  |        p2.xlarge
        mapping       |        ami-08334eb14669f724e  |        m5.4xlarge
        analytics_xs  |        ami-05d5bc4e39832cd00  |        c5.large
        analytics_s   |        ami-05d5bc4e39832cd00  |        m5.large
        analytics_l   |        ami-05d5bc4e39832cd00  |        m5.2xlarge
        analytics_m   |        ami-05d5bc4e39832cd00  |        m5.xlarge
        analytics_xl  |        ami-05d5bc4e39832cd00  |        m5.4xlarge
        analytics_xxl |        ami-05d5bc4e39832cd00  |        m5.8xlarge
        equipment     |        ami-05d5bc4e39832cd00  |        m5.2xlarge
        default       |        ami-05d5bc4e39832cd00  |        c5.large


Creates an EC2 instance (so that debugging can be run on that)

        debugger start_ec2
        debugger stop_ec2
        debugger kill_ec2 


Do the things according to their names

        debugger run [flight_code] [pipeline] [environment]

where

        pipeline: is by default deepLearning (i.e. runs deepLearning.py of image-processing)
        environment: is by default 'prod' (i.e. where the imagery is read from)



## Repository Structure

```
|- debugger/    # Primary folder for code
|  |- instance_manager
      # handles instance creation only
|  |- pipeline_runner
      # handles instance later life and running on it
```

