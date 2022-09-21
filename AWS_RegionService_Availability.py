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
    s = source['prices']

    df = json_normalize(s)
    df.head()

    df.drop(['attributes.aws:serviceUrl','id'], axis=1, inplace=True)

    df.rename(columns = {'attributes.aws:region':'region', 'attributes.aws:serviceName':'service'}, inplace = True)

    rlist = df.region.unique()
    rlist = rlist.tolist()

    regionmapping = {}
    for r in rlist:
        if r not in regionmapping:
            regionmapping[r] = set()
        servicesinregion = df[df['region'] == r]['service'].tolist()
        for s in servicesinregion:
            regionmapping[r].add(s)
     
    
    #start parsing input json for list of services and map if all services are available in a particular region
    selected_services = json.loads(event['body'])

    avail_regions = {}
    for key, val in regionmapping.items():
        available = True
        for serv in selected_services:
            if serv not in val:
                available = False
        avail_regions[key] = available

    response = {
        'statusCode': 200,
        'body': json.dumps({ 'result': avail_regions })
    }

    return response

#demo = { 
#    "statusCode": 200,
#    "body" : '["AWS CloudFormation", "AWS Batch"]'
#}       
#c = []
#demo = json.dumps(demo)
#p = handler(json.loads(demo), c)
#print(p)
            


