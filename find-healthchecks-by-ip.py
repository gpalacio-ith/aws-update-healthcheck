#!/usr/bin/env python3
import boto3
import json
import awsfunctions as aws
from datetime import datetime
import argparse
import ipaddress as ipaddr

# Given a list, prints info of those healthcehcks in the list
def print_hc_info(hc_list):
    # if the list is empty
    if not hc_list:
        print("\nNo healthchecks were found for the given IP(s)/range(s).")
    else:
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

# Çhecks if IP is valid ipv4
def validate_ip_addresses(ip):
    try:
        ipaddr.IPv4Address(ip)
    except ValueError:
        raise ValueError(f'>>> Invalid IP address: {each_ip}. Quitting...')

# Çhecks if IP is valid ipv4 and mask is correct
def validate_net_ranges(net):
    # avoid generating millions of IPs when calculating IPs within a range
    valid_masks = {'20', '21', '22', '23', '24', '26', '27', '28', '29', '30', '31', '32'}

    try:
        net_range = ipaddr.IPv4Network(net, strict=False)
    except ValueError:
        raise ValueError(f'>>> {each_net_range}: Wrong IP or Network Mask.')
    else:
        if str(net_range.prefixlen) not in valid_masks:
            raise ValueError(f'>>> {net_range}: Mask needs to be between /20 .. /32')

# Read objects from file
def read_from_file(file_name):
    try:
        with open(file_name, 'r') as f:
            return(f.read().splitlines())
    except FileNotFoundError:
        pass

def process_input_arg(list_of_arguments):
    list_of_ips = []

    # itereates over single ips from arguments
    if 'ip' in  list_of_arguments:
        for each_ip in list_of_arguments.ip:
            validate_ip_addresses(each_ip)
            list_of_ips.append(each_ip)

    # itereates over network ranges from arguments
    # and generates IPs from the net
    if 'net' in  list_of_arguments:
        for each_net in list_of_arguments.net:
            validate_net_ranges(each_net)
            for addr in ipaddr.IPv4Network(each_net, strict=False):
                list_of_ips.append(str(addr))

    return list_of_ips
    # if 'ip_list' in  list_of_arguments:
    #     list_of_ips = read_from_file(list_of_arguments.ip_list)
    # if 'net_list' in  list_of_arguments:
    #     print('an net-list was passed')


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

    # input arguments
    parser = argparse.ArgumentParser(description='DESCRIPTION put something here')

    # group of arguments, only one accepted
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ip', nargs='*', help='write help', default=argparse.SUPPRESS)
    group.add_argument('--ip-list', help='write help', default=argparse.SUPPRESS)
    group.add_argument('--net', nargs='*', help='write help', default=argparse.SUPPRESS)
    group.add_argument('--net-list', help='write help', default=argparse.SUPPRESS)

    # other arguments
    parser.add_argument('--profile-name', default='default', type=str, required=False, help='write help')

    # parse arguments
    args = parser.parse_args()

    # process the different options
    try:
        list_of_ips = process_input_arg(args)
        print('> Searching Healthchecks for these IPs:')
        for each_ip in list_of_ips:
            print('  - ', each_ip)
        print()
    except ValueError as e:
        print(e)

    # executes main logic
    main(args.profile_name, list_of_ips)
