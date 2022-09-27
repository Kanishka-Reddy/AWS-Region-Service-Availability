import json
import boto3

def handler(event, context):

    """
    First we create a lookup table of services per region using boto3. Then we parse the input json to see which services are available 
    in each given region, and return a response that consists of the 2 lists: "available" and "not_available", that have a list of available services and
    unavailable services respectively for each region.

    """
    all_services = boto3.session.Session().get_available_services() #list of ALL services in the whole of AWS

    #find all the available services for each region and put it into a dictionary called 'services_for_each_region' with region names as keys and a list of services as values
    list_of_regions = boto3.session.Session().get_available_regions('ec2')

    services_for_each_region = {}
    for region in list_of_regions:
        session = boto3.Session(region_name=region).get_available_services() # returns list of services per region
        
        services_for_each_region[region] = session

     
    services_to_find = event['services_query']
    regions_to_query = event['regions_query']

    if len(regions_to_query) == 0:
        return {
            'statusCode': 500
        }

    #create new dictionary "availability" that contains regions as keys
    availability = {}

    for region in regions_to_query:

        availability[region] = {'available': [], 'not_available': []}
        services_available = services_for_each_region[region]

        for service in services_to_find:
            if service not in all_services:
                return {
                    'statusCode': 500,
                    'body': json.dumps({'no_such_service_exists': [service]})
                }

            elif service not in services_available:
                availability[region]['not_available'].append(service)
                
            else:
                availability[region]['available'].append(service)

    response = {
        'statusCode': 200,
        'body': json.dumps({'service_availabilty': availability})
    }

    return response



demo_input = { 
    "statusCode": 200,
    "services_query" : ["kms", "cloudwatch"],
    "regions_query" : ["ap-east-1"]
}       
c = []
p = handler(demo_input, c)
print(p)
            

#Output format:
#{'statusCode': 200, 'body': '{"service_availabilty": {"ap-east-1": {"available": ["kms", "cloudwatch"], "not_available": []}}}'}