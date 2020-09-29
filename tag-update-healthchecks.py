#!/usr/bin/env python3

import boto3
import json
import awsfunctions as aws
import ipaddress
from datetime import datetime


# compute name for healthchecks
def compute_new_hc_name(ip, fqdn):
    third_octet = ip.split('.')[2]
    site_mapping = {
        '144':'IAD',
        '145':'LVS',
        '146':'MSP',
        '148':'POR',
    }
    return(fqdn + '_STG_' + site_mapping[third_octet])

# Defines stg networks, and return ips for all colos
def find_all_ips_stg_ranges():
    iad_stg_net = '170.176.144.144/28'
    por_stg_net = '170.176.148.144/28'
    msp_stg_net = '170.176.146.144/28'
    lvs_stg_net = '170.176.145.144/28'

    all_stg_ips = []
    for every_host in ipaddress.ip_network(iad_stg_net).hosts():
        all_stg_ips.append(str(every_host))
    for every_host in ipaddress.ip_network(por_stg_net).hosts():
        all_stg_ips.append(str(every_host))
    for every_host in ipaddress.ip_network(msp_stg_net).hosts():
        all_stg_ips.append(str(every_host))
    for every_host in ipaddress.ip_network(lvs_stg_net).hosts():
        all_stg_ips.append(str(every_host))

    return(all_stg_ips)

# Given a list, prints info of those healthcehcks in the list
def print_hc_info(hc_list):
    print('These healthchecks will be updated:')
    for index,hc in enumerate(hc_list):
        hc_fqdn = ''
        hc_path = ''
        if 'FullyQualifiedDomainName' in hc['HealthCheckConfig']:
            hc_fqdn = hc['HealthCheckConfig']['FullyQualifiedDomainName']
        if 'ResourcePath' in hc['HealthCheckConfig']:
            hc_path = hc['HealthCheckConfig']['ResourcePath']
        hc_type = hc['HealthCheckConfig']['Type']

        # gets tag info for given helthcheck
        tag_info = client.list_tags_for_resource(
            ResourceType='healthcheck',
            ResourceId=hc['Id']
        )

        # ptocess tag info for the hc
        for every_tag in tag_info['ResourceTagSet']['Tags']:
            if every_tag['Key'] in 'Name':
                name_tag_value = every_tag['Value']

        #print('> ' + f"{name_tag_value: <50}" + ' ' + hc['HealthCheckConfig']['IPAddress'] + ' ' + f"{hc['HealthCheckConfig']['Type']: <5}" + ' ' + hc['Id'] + ' ' + hc_fqdn + hc_path)
        #new_hc_name = compute_new_hc_name(hc['HealthCheckConfig']['IPAddress'], hc_fqdn)
         print('' + hc['Id'] + ',' + hc['HealthCheckConfig']['IPAddress'] + ',' + hc['HealthCheckConfig']['Type'] + ',' + name_tag_value + ',' + new_hc_name)
        #print('' + hc['Id'] + ',' + name_tag_value)
    print(f"- Total of {index+1} healthchecks.")

# apply changes or just test
# TRUE for testing
dry_run = True

# creates aws api sessions params
session = boto3.session.Session(profile_name='aws-prd')
client = session.client('route53')

# search for matching healthchecks
stg_net_ips_list = find_all_ips_stg_ranges()
found_healthchecks = aws.get_healthchecks(stg_net_ips_list, session)
#found_healthchecks = aws.get_all_healthchecks(session)

print_hc_info(found_healthchecks)

#lm_tag = {'Key':'ExportToLogicMonitor','Value':'True'}
#accepted_healthcheck_types = ['HTTP', 'HTTPS']
#for every_hc in found_healthchecks:
#    # print(every_hc['HealthCheckConfig']['Type'])
#    if every_hc['HealthCheckConfig']['Type'] in accepted_healthcheck_types:
#        new_name = compute_new_hc_name(every_hc['HealthCheckConfig']['IPAddress'], every_hc['HealthCheckConfig']['FullyQualifiedDomainName'])
#        #new_tags = [{'Key':'Name', 'Value':new_name}, lm_tag]
#        new_tags = [lm_tag]
#
#        response = client.change_tags_for_resource(
#                        ResourceType='healthcheck',
#                        ResourceId=every_hc['Id'],
#                        AddTags = new_tags
#                    )
