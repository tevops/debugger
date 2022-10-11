import os
import sys
import logging
import subprocess

from scp import SCPClient
from botocore.exceptions import ClientError
from paramiko import RSAKey, SSHClient, AutoAddPolicy

from typing import Tuple, List, Union

from .utils import get_instance, instance_username


tmp_storage = "tmp_storage"
pem_variable = "PEM_FILE_PATH"
directory = "[DIRECTORY]"
PROD_REPO = "[PROD REPO]"

# The logger
logger = logging.getLogger('PipelineRunner')


class PipelineRunner:

    def __init__(self, pem_file: str, username: str = instance_username):
        """
        Args:
            pem_file: The path to your analytics.pem file
            username: The username to use to ssh to instance

        """

        self.pem_file = pem_file
        self.username = username
        self.es2_instance = get_instance()

        self.instance_id = None
        self.instance_ip = None
        self.instance_state = None
        self.intance_environment = None

        self.get_instance_details()
        self.runner: SSHClient = None

    def get_instance_details(self):
        data = self.es2_instance.meta.data
        self.instance_id = data['InstanceId']
        self.instance_ip = data['NetworkInterfaces'][0]['PrivateIpAddress']
        self.intance_environment = [tag['Value'] for tag in data['Tags'] if tag['Key'] == "Environment"]

    def start_ec2(self):
        if self.es2_instance.state['Name'] == "stopped":
            try:
                self.es2_instance.start()
                logger.info(f'[debugger]: Started instance {self.instance_id}')

            except ClientError as err:
                logger.exception(err)
                raise
        else:
            logger.warning(f"[debugger]: Cannot start instance {self.instance_id} from state:{self.instance_state}")

    def stop_ec2(self):
        if self.es2_instance.state['Name'] in ("running", "pending"):
            try:
                self.es2_instance.stop()
                logger.info(f'[debugger]: Instance {self.instance_id} successfully stopped')

            except ClientError as err:
                logger.exception(err)
                raise
        elif self.instance_state in ("stopping", "stopped"):
            logger.warning(f'[debugger]: Instance {self.instance_id} is at state:{self.instance_state}')

    def kill_ec2(self):
        if self.es2_instance.state['Name'] == "stopped":
            try:
                self.es2_instance.terminate()
                logger.info(f'[debugger]: Instance {self.instance_id} successfully terminated')

            except ClientError as err:
                logger.exception(err)
                raise
        else:
            logger.warning(f'[debugger]: Instance {self.instance_id} cannot be terminated from state:{self.instance_state}')

    @classmethod
    def sync_input_json(cls, flight: str, folder: str):
        """
        Downloads the input.json of the flight from s3
        Args:
            flight: the flight code
            folder: the directory to download the flight into
        """
        return f"aws s3 cp {PROD_REPO}/{flight}/input.json {directory}/{folder}/{flight}.json"

    @classmethod
    def get_analytics_pem(cls) -> Union[str, None]:
        try:
            pem_path = os.environ['ANALYTICS_PEM']
            if os.path.exists(pem_path):
                return pem_path
            else:
                logger.info(f"[debugger]: No such file as {pem_variable} - please check.")
                sys.exit()

        except KeyError:
            logger.info(f"[debugger]: Please run 'export {pem_variable}=/path/to/your/analytics.pem' ")
            sys.exit()

    def prepare_client(self):
        """ Runs the command on ec2 and returns the logs"""
        client, key = self._load_client_and_key()
        # Connect/ssh to an instance
        try:
            client.connect(hostname=self.instance_ip,
                           username=self.username, pkey=key)
            self.runner = client

        except Exception as err:
            logger.exception(err)
            sys.exit(0)

    def _load_client_and_key(self) -> Tuple[SSHClient, RSAKey]:
        """
        Loads the paraminko client for further operations with the ec2.
        """
        try:

            key = RSAKey.from_private_key_file(self.pem_file)
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            return client, key

        except FileNotFoundError:
            logger.fatal(f"[debugger]: No such pem file as {self.pem_file}")

    @staticmethod
    def _line_buffered(f):
        """
        For parsing the logs from remote machine.
        """

        line_buf = ""
        while not f.channel.exit_status_ready():
            line_buf += f.read(1).decode('utf-8')
            if line_buf.endswith('\n'):
                yield line_buf
                line_buf = ''

    def run(self, cmd: str):
        """
        Args:
            cmd - the command to run on the remote machine.
        """
        self.prepare_client()
        logger.info(f"[debugger]: Running {cmd}")
        stdin, stdout, stderr = self.runner.exec_command(cmd)
        for line in self._line_buffered(stdout):
            logger.info(line.strip('\n'))

        (stdout, stderr) = (std.read().decode('utf-8').strip('\n') for std in (stdout, stderr))
        if stderr:
            logger.fatal(f"[debugger]: {stderr}")
        if stdout:
            logger.info(f"[debugger]: OUT: {stdout}")
        return stdout, stderr

    def upload(self, files: List[Tuple[str, str]]):
        """
        Uploads the file to the remote machine
        """
        with SCPClient(self.runner.get_transport()) as scp:
            for file, dest in files:
                logger.info(f"[debugger]: Uploading {file} to {dest}")
                scp.put(file, dest)

    @staticmethod
    def get_git_diff():
        """
        Lists the files that are touched
        """
        git_diff, _ = subprocess.Popen('git diff --name-only',
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, shell=True).communicate()
        return git_diff.decode("utf-8").strip('\n').split('\n')

    def update(self):
        if os.path.basename(os.getcwd()) == directory:
            files = self.get_git_diff()
            if len(files) > 1:
                self.upload(files=[(file, f"~/{directory}/{file}") for file in files])
        else:
            logger.warning(f"[debugger]: Navigate to {directory} - where command 'git diff' would be meaningful.")
            sys.exit()
