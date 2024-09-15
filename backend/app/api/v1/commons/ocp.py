from datetime import date
import pandas as pd
import app.api.v1.commons.utils as utils
from app.services.search import ElasticService


async def getData(start_datetime: date, end_datetime: date, configpath: str):
    try:
        query = {
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "timestamp": {
                                "format": "yyyy-MM-dd"
                            }
                        }
                    }
                }
            }
        }
        job = []
        es = ElasticService(configpath=configpath)
        response = await es.post(query=query, start_date=start_datetime, end_date=end_datetime, timestamp_field='timestamp')
        print("potassium")
        print(response)
        await es.close()
        print("test in response") if("test" in response) else print("no")
        tasks = [item['_source'] for item in response["test"]]
        print(tasks)
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
        
        return ({"test":jobs,"total":response["total"]})
    except Exception as err:
        raise("I'm here")
        print(f"{type(err).__name__} was raised: {err}") 

def fillEncryptionType(row):
    if row["encrypted"] == "N/A":
        return "N/A"
    elif row["encrypted"] == "false":
        return "None"
    else:
        return row["encryptionType"]
