#!/usr/bin/env python3
import boto3
import json
import awsfunctions as aws
from datetime import datetime

# Given a list, prints info of those healthcehcks in the list
def print_hc_info(hc_list):
    print('These healthchecks will be updated:')
    for hc in hc_list:
        hc_fqdn = ''
        if 'FullyQualifiedDomainName' in hc['HealthCheckConfig']:
            hc_fqdn = hc['HealthCheckConfig']['FullyQualifiedDomainName']
        hc_type = hc['HealthCheckConfig']['Type']
        print('> ' + hc['HealthCheckConfig']['IPAddress'] + ' ' + f"{hc['HealthCheckConfig']['Type']: <5}" + ' ' + hc['Id'] + ' ' + hc_fqdn)

def read_user_input():
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}
    user_input = ''
    while user_input not in yes or user_input not in no:
        user_input = input().lower()
        if user_input in yes:
           return True
        elif user_input in no:
           return False
        else:
           print("Please respond with 'y|yes' or 'n|no':", end=' ')

# apply changes or just test
# TRUE for testing
dry_run = True

# creates aws api sessions params
session = boto3.session.Session(profile_name='aws-prd')
client = session.client('route53')

# search for matching healthchecks
target_ip_list = ['170.176.144.40']
found_healthchecks = aws.get_healthchecks(target_ip_list, session)

# write to (log) file before applying any change
time_now = datetime.now().strftime('%Y_%m_%d_%H%M%S')
log_filename_b = 'before_update_' + time_now
with open(log_filename_b, 'w') as file:
    file.write(json.dumps(found_healthchecks, indent=4))

# new parameters for target healthchecks
new_ip = '170.176.144.40'
new_regions = ['us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1']

# Print messages
print_hc_info(found_healthchecks)
print('\nAll the previous healthchecks will be updated with this new config: ')
print('  - new ip       =', new_ip)
print('  - new regions  =', new_regions)
print('\nDo you wish to proceed? [y/n]:', end=' ')
user_choice = read_user_input()

print('Choice ====', user_choice)

# update all found healthhecks
if not dry_run and user_choice:
    updated_healthcehcks = []
    for healthcheck in found_healthchecks:
        update_response = client.update_health_check(
                                HealthCheckId = healthcheck['Id'],
                                IPAddress = new_ip,
                                Regions = new_regions
                          )
        updated_healthcehcks.append(update_response)
    # write changes to (log) file
    log_filename_a = 'after_update_' + time_now
    with open(log_filename_a, 'w') as file:
        file.write(json.dumps(updated_healthcehcks, indent=4))

