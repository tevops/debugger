from pathlib import Path
from debugger.pipeline_runner.runner import get_analytics_pem


def test_aws_setup():
    assert Path('~/.aws/config').exists()
    assert Path('~/.aws/credentials').exists()
