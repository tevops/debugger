import boto3
import base64
import docker
import getpass
import logging

from typing import Dict

logger = logging.getLogger('InstanceManager')
logging.basicConfig(level=logging.INFO, format='%(message)s')

REPO = '752038878129.dkr.ecr.us-east-1.amazonaws.com/automation'
TAG = 'dockerized_manage_py_latest'


def get_docker_auth() -> Dict:
    ecr = boto3.client('ecr')
    auth_creds = ecr.get_authorization_token()['authorizationData'][0]
    username, password = base64.b64decode(auth_creds['authorizationToken']).decode('utf-8').split(':')
    return {
        'username': username,
        'password': password
    }


class InstanceManager:
    """
    A temporary solution to handle machine creation. There manage.py from automation repo
    is dockerized and pushed to ECR. This class pulls that image - creates a container from
    it and the from inside the container manages ec2 type instances  - (create, destroy) to
    which are used for debugging the image processing pipeline.
    """

    def __init__(self):
        self.client = docker.client.from_env()
        self.session = boto3.Session()
        self.credentials = self.session.get_credentials().get_frozen_credentials()
        self.docker_auth = get_docker_auth()

    def pull_image(self):
        try:
            logger.info(f'[debugger]: Pulling docker image = {REPO}:{TAG}')
            self.client.images.pull(REPO, tag=TAG, auth_config=self.docker_auth)
        except docker.errors.APIError:
            logger.info(f'[debugger]: Failed to pull {REPO}:{TAG}, attempting to get new credentials')
            self.docker_auth = get_docker_auth()
            try:
                self.client.images.pull(REPO, tag=TAG, auth_config=self.docker_auth)
            except docker.errors.APIError as e:
                logger.exception(e, exc_info=True)
                return f'Failed to pull docker image={REPO}:{TAG}'

        return None

    def get_kwargs(self) -> Dict:
        return {
            'image': f'{REPO}:{TAG}',
            'shm_size': '1GB',
            'environment': {
                'AWS_ACCESS_KEY_ID': self.credentials.access_key,
                'AWS_SECRET_ACCESS_KEY': self.credentials.secret_key,
                'AWS_SESSION_TOKEN': self.credentials.token if self.credentials.token else ''},
            'detach': True,
        }

    def run_manager(self, cmd: str):
        run_kwargs = self.get_kwargs()
        run_kwargs.update({"command": cmd})

        container = self.client.containers.run(**run_kwargs)
        logs = container.logs(stream=True)
        for log in logs:
            logger.info(log.decode('utf-8').strip('\n'))

    def create_ec2(self, kind: str = 'analytics_xs', env: str = 'release', priority: str = 'high'):
        """
        Args:
            kind: should be either of 'deep_learning' and 'analytics'
            env: the environment to create the machine in
            priority: by default (implied) and set to high
        """
        self.run_manager(cmd=f"python manage.py "
                             f"-a create -t {kind} -e {env} "
                             f"-p {priority} -u {getpass.getuser()}")

    def stop_ec2(self, instance_id: str, env: str, priority: str = 'high'):
        """
        Args:
            instance_id: the id of the instance to stop
            env: the environment the instance is in
            priority: high by default
        """
        self.run_manager(cmd=f"python manage.py -a stop "
                             f"-u {getpass.getuser()} "
                             f"-e {env} -p {priority} "
                             f"--instance_ids {instance_id} ")

    def start_ec2(self, instance_id: str, env: str, priority: str = 'high'):
        """
        Args:
            instance_id: the id of the instance to start
            env: the environment the instance is in
            priority: high by default

        """
        self.run_manager(cmd=f"python manage.py -a start "
                             f"-u {getpass.getuser()} "
                             f"-e {env} -p {priority} "
                             f"--instance_ids {instance_id} ")

    def terminate_ec2(self, instance_id: str,  env: str, priority: str = 'high'):
        """
        Args:
            instance_id: the id of the instance to terminate
            env: the environment the instance is in
            priority: high by default

        """
        self.run_manager(cmd=f"python manage.py -a terminate "
                             f"-u {getpass.getuser()} "
                             f"-e {env} -p {priority} "
                             f"--instance_ids {instance_id} ")

