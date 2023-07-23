from pathlib import Path


def test_aws_setup():
    assert Path('~/.aws/config').exists()
    assert Path('~/.aws/credentials').exists()
