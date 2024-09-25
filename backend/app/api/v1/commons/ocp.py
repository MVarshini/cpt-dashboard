from datetime import date
import pandas as pd
import app.api.v1.commons.utils as utils
from app.services.search import ElasticService
import json

async def getData(start_datetime: date, end_datetime: date, size:int, offset:int, sort:str, filter:str, configpath: str):
    try:
        query = {
            "query": {
                "bool": {
                    "filter":{
                        "range": {
                            "timestamp": {
                                "format": "yyyy-MM-dd"
                            }
                        }
                        
                    }
                }
            }
        }
        es = ElasticService(configpath=configpath)
        if sort:
            query.update({"sort": json.loads(sort)})
        if filter:
            filter_dict = json.loads(filter)
            
        # query['query']['bool']['must'][0].update({"terms":{"platform.keyword":["AWS","GCP"]}})
        print(filter_dict)

        response = await es.post(query=query, size=size, filterTerms=filter_dict, offset=offset, start_date=start_datetime, end_date=end_datetime, timestamp_field='timestamp')
        await es.close()
        tasks = [item['_source'] for item in response["data"]]
        jobs = pd.json_normalize(tasks)
        if len(jobs) == 0:
            return jobs

        jobs[['masterNodesCount', 'workerNodesCount',
            'infraNodesCount', 'totalNodesCount']] = jobs[['masterNodesCount', 'workerNodesCount', 'infraNodesCount', 'totalNodesCount']].fillna(0)
        jobs.fillna('', inplace=True)
        jobs[['ipsec', 'fips', 'encrypted',
            'publish', 'computeArch', 'controlPlaneArch']] = jobs[['ipsec', 'fips', 'encrypted',
                                                                    'publish', 'computeArch', 'controlPlaneArch']].replace(r'^\s*$', "N/A", regex=True)
        jobs['encryptionType'] = jobs.apply(fillEncryptionType, axis=1)
        jobs['benchmark'] = jobs.apply(utils.updateBenchmark, axis=1)
        jobs['platform'] = jobs.apply(utils.clasifyAWSJobs, axis=1)
        jobs['jobType'] = jobs.apply(utils.jobType, axis=1)
        jobs['isRehearse'] = jobs.apply(utils.isRehearse, axis=1)
        jobs['jobStatus'] = jobs.apply(utils.updateStatus, axis=1)
        jobs['build'] = jobs.apply(utils.getBuild, axis=1)

        cleanJobs = jobs[jobs['platform'] != ""]

        jbs = cleanJobs
        jbs['shortVersion'] = jbs['ocpVersion'].str.slice(0, 4)

        return ({"data":jobs,"total":response["total"]})
    
    except Exception as err:
        print(f"{type(err).__name__} was raised: {err}") 

def fillEncryptionType(row):
    if row["encrypted"] == "N/A":
        return "N/A"
    elif row["encrypted"] == "false":
        return "None"
    else:
        return row["encryptionType"]
