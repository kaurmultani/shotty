# shotty
uses boot3 to manage Ec2 instances snapshots

aws configure --profile shotty

pipenv run python shotty/shotty.py <command>  <--project=PROJECT>

command = list, start, stop
project is optional

pipenv run python shotty/shotty.py --help
pipenv run python shotty/shotty.py list --help
