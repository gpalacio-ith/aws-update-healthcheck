#!/usr/bin/env python3

# Standard imports
import boto3
import json

# Third party imports

# Local imports

#
def get_zone_id(zone_name, session):
    list_of_zones = get_list_of_zones(session)
    for each_zone in list_of_zones:
        if zone_name in each_zone['Name']:
            return each_zone['Id']

# Return list of zones with filtered info, only ids and name
def get_list_of_zones(session):
    client = session.client('route53')

    # pag objects in case there's more than 100 zones
    paginator = client.get_paginator('list_hosted_zones')
    response_iterator = paginator.paginate(
                            PaginationConfig={
                                'MaxItems': 500,
                                'PageSize': 500
                            }
    )

    list_of_zones = []
    # iterates over each zone in each page
    # extracs id and adds only name and id to results
    for page in response_iterator:
        for each_zone in page['HostedZones']:
            zone_name = each_zone['Name']
            zone_id = each_zone['Id'].split('/')[-1]
            list_of_zones.append({'Name':zone_name, 'Id':zone_id})
    return(list_of_zones)

# Return a list of records
def get_list_of_records(zone_id, session):
    # set pag objects
    client = session.client('route53')
    paginator = client.get_paginator('list_resource_record_sets')
    response_iterator = paginator.paginate(HostedZoneId=zone_id)

    # iterates through pages and records
    list_of_records = []
    for page in response_iterator:
        for record in page['ResourceRecordSets']:
            list_of_records.append(record)
    return(list_of_records)

# Check if ip is actually returned by DNS (i.e. healthcheck is ok)
def is_ip_healthy(zone_id, record_name, record_type, ip_addr, session):
    client = session.client('route53')
    query_response = client.test_dns_answer(
        HostedZoneId=zone_id,
        RecordName=record_name,
        RecordType=record_type)
    if ip_addr in query_response['RecordData']:
        return(True)
    else:
        return(False)


# Given a list of one or more ips, return all the found healthchecks
def get_healthchecks(ip_list, session):
    client = session.client('route53')
    paginator = client.get_paginator('list_health_checks')
    response_iterator = paginator.paginate(
                            PaginationConfig={
                                'MaxItems': 500,
                                'PageSize': 500
                        })

    all_healthchecks = []
    for index, each_page in enumerate(response_iterator):
        for each_healthcheck in each_page['HealthChecks']:
            all_healthchecks.append(each_healthcheck)

    healthchecks_found_for_ip= []
    for entry in all_healthchecks:
        if 'IPAddress' in entry['HealthCheckConfig']:
            entry_ip = entry['HealthCheckConfig']['IPAddress']

            # if it's one of the interesting ips...
            if entry_ip in ip_list:
                healthchecks_found_for_ip.append(entry)
                # collects info
                # entry_id = entry['Id']
                # entry_type = entry['HealthCheckConfig']['Type']
                # if 'FullyQualifiedDomainName' in entry['HealthCheckConfig']: entry_fqdn = entry['HealthCheckConfig']['FullyQualifiedDomainName']
                # else: entry_fqdn = ''
                # if 'ResourcePath' in entry['HealthCheckConfig']: entry_path = entry['HealthCheckConfig']['ResourcePath']
                # else: entry_path = ''
                #
                # process entry found
                # print('> ' + entry_ip + '   ' +  entry_id + '   ' + entry_fqdn)

    return(healthchecks_found_for_ip)

def search_records(target_ip_list, record_type, session):
    def evaluate_record(record):
        record_ips = [ip['Value'] for ip in each_record['ResourceRecords']]
        found_ip = any(x in record_ips for x in target_ip_list)
        return(found_ip)

    list_of_zones = get_list_of_zones(session)

    results_list = []
    for each_zone in list_of_zones:
        list_of_records = get_list_of_records(each_zone['Id'], session)
        for each_record in list_of_records:
            # if it's not an alias target and record type is A, process record
            if not 'AliasTarget' in each_record and each_record['Type'] in record_type:
                if evaluate_record(each_record):
                    each_record['ZoneId'] = each_zone['Id']
                    results_list.append(each_record)
    return(results_list)






#session = boto3.session.Session(profile_name='aws-prd')
# print(get_list_of_records('Z1PT33YEIWOBV4', session))
#list_of_zones = get_list_of_zones('aws-prd')
#print(json.dumps(list_of_zones,indent=4))