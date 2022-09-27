from setuptools import setup, find_packages

CLASSIFIERS = [
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.8",
]

setup(name="debugger",
      version="1.0",
      zip_safe=False,
      license="GNU-GPL",
      author="intelinair",
      packages=find_packages(),
      url="https://github.com/tevops/debugger",
      install_requires=['boto3',
                        'botocore',
                        'docker',
                        'paramiko',
                        'scp',
                        'setuptools'],
      description="Debugger of image_processing repo",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      classifiers=CLASSIFIERS,
      entry_points={"console_scripts": ["debugger = debugger.main:cli"]},

      )
