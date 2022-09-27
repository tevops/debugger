from pathlib import Path
from debugger.pipeline_runner.runner import get_analytics_pem


def test_aws_setup():
    assert Path('~/.aws/config').exists()
    assert Path('~/.aws/credentials').exists()


def test_agmri_setup():
    assert Path('~/.agmri.cfg').exists()


def test_os_env():
    pem_path = get_analytics_pem()
    assert Path(pem_path).exists()