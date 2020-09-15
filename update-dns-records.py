#!/usr/bin/env python3
import boto3
import json
import awsfunctions as aws
from datetime import datetime

# apply changes or just test
dry_run = True

# creates aws api sessions params
session = boto3.session.Session(profile_name='aws-prd')
client = session.client('route53')

print('------------------------------')
print('   BEFORE Updating RECORDS    ')
print('------------------------------')

# search for matching healthchecks
target_ip_list = ['170.176.144.41']
record_type = 'A'
found_records = aws.search_records(target_ip_list, record_type, session)
print(json.dumps(found_records, indent=4))




new_ip = '170.176.144.40'
new_ip_as_list = [{'Value': new_ip}]

print('------------------------------')
print('   AFTER Updating RECORDS     ')
print('------------------------------')

for record in found_records:
    new_ip_as_list = [{'Value': new_ip}]
    change_to_dns = {
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': record['Name'],
                    'Type': record['Type'],
                    'TTL': record['TTL'],
                    'ResourceRecords': new_ip_as_list,
                    'MultiValueAnswer': record['MultiValueAnswer'],
                    'SetIdentifier': record['SetIdentifier']
                }
            }
        ]
    }

    # some records dont have healthchechs assigned to them
    if 'HealthCheckId' in record:
        change_to_dns['Changes'][0]['ResourceRecordSet']['HealthCheckId'] = record['HealthCheckId']

    response = client.change_resource_record_sets(
                    ChangeBatch=change_to_dns,
                    HostedZoneId=record['ZoneId']
               )
    print(json.dumps(change_to_dns, indent=4))

