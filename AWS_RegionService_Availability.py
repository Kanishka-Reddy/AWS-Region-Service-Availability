import collections
import requests
import json
from pandas import json_normalize
import pandas as pd

url = 'https://api.regional-table.region-services.aws.a2z.com/index.json'

def handler(event, context):

    """
    First we create a lookup table of services per region using an external API. Then we parse the input json to see which services are available 
    in each given region, and return a response that consists of the 2 lists: "available" and "not_available", that have a list of available services and
    unavailable services respectively for each region.

    """

    #start creating a lookup of services for each region
    source = requests.get(url).json()
    source_to_df = source['prices']
    df = json_normalize(source_to_df)   #creating a pandas dataframe to work with the data
    df.drop(['attributes.aws:serviceUrl','id'], axis=1, inplace=True)   #dropping unwanted columns in pandas
    df.rename(columns = {'attributes.aws:region':'region', 'attributes.aws:serviceName':'service'}, inplace = True) #renaming some columns in pandas

    #create a list of all the different regions from the given pandas dataframe
    list_of_regions = df.region.unique()
    list_of_regions = list_of_regions.tolist()

    #find all the available services for each region and put it into a dictionary called 'services_for_each_region' with region names as keys and a list of services as values
    services_for_each_region = {}
    for region in list_of_regions:
        if region not in services_for_each_region:
            services_for_each_region[region] = set()
        
        servicesinregion = df[df['region'] == region]['service'].tolist()

        for service in servicesinregion:
            services_for_each_region[region].add(service)
     
    
    #start parsing input json for list of services to find and list of regions to search
    services_to_find = json.loads(event['services_query'])
    regions_to_query = json.loads(event['regions_query'])

    #create new dictionary "availability" that contains regions as keys
    availability = {}

    for region in regions_to_query:

        availability[region] = {'available': [], 'not_available': []}
        services_available = services_for_each_region[region]

        for service in services_to_find:
            if service not in services_available:
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
    "services_query" : '["AWS CloudFormation", "AWS Batch"]',
    "regions_query" : '["ap-east-1"]'
}       
c = []
demo_input = json.dumps(demo_input)
p = handler(json.loads(demo_input), c)
print(p)
            

#Output format:
#{'statusCode': 200, 'body': '{"service_availabilty": {"ap-east-1": {"available": ["AWS CloudFormation", "AWS Batch"], "not_available": []}}}'}