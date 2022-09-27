import sys
import boto3
import getpass
import logging


logger = logging.getLogger('PipelineRunner')

instance_username = "ubuntu"
local_username = getpass.getuser()

session = boto3.Session(region_name='us-east-1')
EC2 = session.resource("ec2")

Filter = [
            {"Name": "tag:UserCreated", "Values": [local_username]},
            {"Name": "instance-state-name", "Values": ["pending",
                                                       "running",
                                                       "shutting-down",
                                                       "stopping",
                                                       "stopped"]},

        ]


def get_instance():
    """
    :returns: The EC2 instance
    """
    instance_objects = []
    instances = EC2.instances.filter(
        Filters=Filter
    )

    for page in instances.pages():
        for obj in page:
            instance_objects.append(obj)

    if len(instance_objects) == 1:
        return next(iter(instance_objects))

    elif len(instance_objects) > 1:
        logger.exception(f"Multiple instances with tag:UserCreated={local_username} "
                         f"please login to web UI and sort it out")
        sys.exit(0)
