#!/usr/bin/env python3
import boto3
import json
import awsfunctions as aws
from datetime import datetime
import argparse


# Given a list, prints info of those healthcehcks in the list
def print_hc_info(hc_list):
    print('These healthchecks were found:')
    for index,hc in enumerate(hc_list):
        hc_fqdn = ''
        hc_path = ''
        if 'FullyQualifiedDomainName' in hc['HealthCheckConfig']:
            hc_fqdn = hc['HealthCheckConfig']['FullyQualifiedDomainName']
        if 'ResourcePath' in hc['HealthCheckConfig']:
            hc_path = hc['HealthCheckConfig']['ResourcePath']
        hc_type = hc['HealthCheckConfig']['Type']

        print('> ' + hc['HealthCheckConfig']['IPAddress'] + ' ' + f"{hc['HealthCheckConfig']['Type']: <5}" + ' ' + hc['Id'] + ' ' + hc_fqdn + hc_path)
    print(f"\nTotal Healthchecks = {index+1}")

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

def main(account_profile, ip_list):
    # creates aws api sessions params
    session = boto3.session.Session(profile_name=account_profile)
    client = session.client('route53')
    # search for matching healthchecks
    found_healthchecks = aws.get_healthchecks(ip_list, session)
    print_hc_info(found_healthchecks)



if __name__ == '__main__':
    # --ip
    # --ip-list <read-from-file>
    # --net
    # --net-list <read-from-file>
    # --output csv|txt|...


    parser = argparse.ArgumentParser(description='DESCRIPTION put something here')
    parser.add_argument('--ip', nargs='*', required=False, help='write help', )
    parser.add_argument('--profile-name', default='default', type=str, required=True, help='write help')


    args = parser.parse_args()
    print('Searching this ip/ranges for healthchecks:')
    print(args.ip, '\n')
    main(args.profile_name, args.ip)
