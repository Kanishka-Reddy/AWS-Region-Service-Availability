import requests
import json
from pandas import json_normalize
import pandas as pd

url = 'https://api.regional-table.region-services.aws.a2z.com/index.json'

def handler(event, context):

    """
    First we create a lookup table of services per region using an external API. Then we parse the input json to see if all the services are available 
    in each region, and return a response that consists of the list of all regions and a boolean.

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
     
    
    #start parsing input json for list of services to find
    services_to_find = json.loads(event['body'])

    #create new dictionary are_services_available that contains regions as keys and a boolean as values that shows whether all the services are available in a particular region
    are_services_available = {}
    for key, val in services_for_each_region.items():
        available = True
        for service in services_to_find:
            if service not in val:
                available = False
        are_services_available[key] = available

    response = {
        'statusCode': 200,
        'body': json.dumps({ 'result': are_services_available })
    }

    return response

#demo_input = { 
#    "statusCode": 200,
#    "body" : '["AWS CloudFormation", "AWS Batch"]'
#}       
#c = []
#demo_input = json.dumps(demo_input)
#p = handler(json.loads(demo_input), c)
#print(p)
            
#Output format:
#{'statusCode': 200, 'body': '{"result": {"ap-east-1": true, "ap-northeast-1": true, "ap-northeast-2": true, "ap-south-1": true, 
# "ap-southeast-2": true, "ca-central-1": true, "eu-west-2": true, "eu-west-3": true, "us-east-1": true, "us-east-2": true, 
# "ap-southeast-1": true, "eu-central-1": true, "eu-north-1": true, "eu-west-1": true, "us-gov-west-1": true, "us-west-1": true, 
# "us-west-2": true, "af-south-1": true, "ap-northeast-3": true, "cn-north-1": true, "sa-east-1": true, "ap-southeast-3": true, 
# "eu-south-1": true, "me-central-1": false, "me-south-1": true, "cn-northwest-1": true, "us-gov-east-1": true}}'}

