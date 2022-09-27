import os
import sys

__version__ = "1.0"

from debugger.pipeline_runner.runner import PipelineRunner
from debugger.pipeline_runner.manager import InstanceManager
from debugger.pipeline_runner.runner import (directory, logger, tmp_storage)


def get_runner() -> PipelineRunner:
    pem_file = PipelineRunner.get_analytics_pem()
    return PipelineRunner(pem_file=pem_file)


def run(flight_code: str, pipeline: str = "deepLearning", agmri_env: str = "prod"):
    runner = get_runner()
    if runner.instance_state != "running":
        runner.start_ec2()

    runner.update()
    out, err = runner.run(cmd=runner.sync_input_json(
        folder=tmp_storage,
        flight=flight_code,
    ))

    input_json = f"{os.path.join(tmp_storage, flight_code)}.json"
    if not err:
        out, err = runner.run(cmd=f"cd {directory}; "
                                  f"export AWS_DEFAULT_REGION='us-east-1';"
                                  f"export PYTHONPATH=.;"
                                  f"python3 pipelines/{pipeline}.py "
                                  f"--input_json {input_json} "
                                  f"--local_dir {tmp_storage} "
                                  f"--environment {agmri_env} "
                                  f"--runtime local "
                                  f"--enable_caching ")

    logger.info(" --------------- COMPLETE --------------- ")


def create_ec2(kind: str, env: str):
    manager = InstanceManager()
    manager.create_ec2(kind=kind, env=env)


def start_ec2():
    runner = get_runner()
    runner.start_ec2()


def stop_ec2():
    runner = get_runner()
    runner.stop_ec2()


def kill_ec2():
    runner = get_runner()
    runner.kill_ec2()


manager_commands = ["create_ec2"]
runner_commands = ["kill_ec2", "stop_ec2", "start_ec2"]


def cli():
    try:
        cmd = sys.argv[1]
        if cmd in manager_commands:
            create_ec2(kind=sys.argv[2], env=sys.argv[3])

        elif cmd in runner_commands:
            globals()[cmd]()

        elif cmd == "run":
            run(*sys.argv[2:])

        else:
            logger.info(f"No such command {cmd} defined in debugger")

    except (KeyError, IndexError):
        raise LookupError(
            f"Invalid command passed - unavailable options: {sys.argv}"
        )

    except Exception:
        raise
