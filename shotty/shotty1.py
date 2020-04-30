import boto3
import click
# import sys

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.group()
def instances():
    "Commands for instances"

@instances.command('list')
# script accepts list as first argument
@click.option('--project', default=None, help = 'Instances for project (tag Project:<name>)')
def list_instances(project):
    "List of instances"
    instances = []

    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        # if list of tags is empty, boto3 returns None so that type(i.tags) is None Type
        # if there are tags, i.tags will be a list
        # so if i.tags is not a list it will return [] (i.tags or [])
        print(','.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            # <no project> is a default value
        )))
    return

@instances.command('stop')
@click.option('--project', default=None, help = 'Instances for project (tag Project:<name>)')
def stop_instances(project):
    "stop EC2 instances"
    instances = []

    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    
    for i in instances:
        print('Stopping {0}'.format(i.id))
        i.stop
        
    return



if __name__ == '__main__':
    #print(sys.argv)
    instances()