import boto3
import botocore
import click
# import sys

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state =='pending'

@click.group()
def cli():
    "Shotty commands"

@cli.group('snapshots')
def snapshots():
    'Commands for snapshots'

@snapshots.command('list')
@click.option('--project', default=None, help = 'Snapshots for project (tag Project:<name>)')
@click.option('--all', 'list_all', default=False, is_flag=True, help = 
'List all snapshots for each volume, not just the most recent')
# if --all is set this means list_all flag is True, otherwise false
def list_snapshots(project, list_all):
    "List of Snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(','.join((
                    s.id,
                    v.id,
                    i.id,
                    s.progress,
                    s.start_time.strftime('%c')
                )))
                if s.state == 'completed' and not list_all:
                    break
                # if s.state == 'completed'
                # if completed then get out of the loop and jump to next volume. Thus
                # giving the recent snapshot from the previous volume instead of all snapshots
                # s.state == 'completed' and not list_all
                # if the state is completed and list_all flag not set then print just the recent snapshot
    return

@cli.group('volumes')
def volumes():
    "Commands for volumes"

@volumes.command('list')
@click.option('--project', default=None, help = 'Volumes for project (tag Project:<name>)')
def list_volumes(project):
    "List of volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(','.join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))


    return

@cli.group('instances')
def instances():
    "Commands for instances"

@instances.command('list')
# script accepts list as first argument
@click.option('--project', default=None, help = 'Instances for project (tag Project:<name>)')
def list_instances(project):
    "List of instances"

    instances = filter_instances(project)

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

    instances = filter_instances(project)

    for i in instances:
        print('Stopping {0}'.format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print('Could not stop {0}'.format(i.id) + str(e))
            continue
        # try: try to stop. If there is an botocore.exceptions.ClientError exception give a name e
        # then print message and contiue the loop goind to the next instance
    return

@instances.command('start')
@click.option('--project', default=None, help = 'Instances for project (tag Project:<name>)')
def start_instances(project):
    "stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('Starting {0}'.format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print('Could not start {0}.'.format(i.id) + ' ' + str(e))
            continue    
    return

@instances.command('snapshot')
@click.option('--project', default=None, help = 'Snapshot for instances (tag Project:<name>)')
def snapshot_instances(project):
    "Take snapshot"

    instances = filter_instances(project)

    for i in instances:
        print('Stopping {0}'.format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print('Skipping {0}, snapshot already in progress.'.format(v.id))
                continue
                
            print('Creating snapshot for {0}'.format(v.id))
            v.create_snapshot(Description='created by script')
            print('Starting {0}'.format(i.id))
            i.start()
            i.wait_until_running()
    print('All done')
    return

if __name__ == '__main__':
    #print(sys.argv)
    cli()