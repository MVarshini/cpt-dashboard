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
                    "filter": [{
                        "range": {
                            "timestamp": {
                                "format": "yyyy-MM-dd"
                            }
                        }
                    }]
                }
            }
        }
       
        if(sort):
            query.update({"sort": json.loads(sort)})
        if(filter):
            query = buildFilterQuery(filter, query) 
            
        es = ElasticService(configpath=configpath)
       
        response = await es.post(query=query, size=size, offset=offset, start_date=start_datetime, end_date=end_datetime, timestamp_field='timestamp')
        await es.close()
        tasks = [item['_source'] for item in response['data']]
        jobs = pd.json_normalize(tasks)
        if len(jobs) == 0:
            return jobs

        jobs[['masterNodesCount', 'workerNodesCount',
            'infraNodesCount', 'totalNodesCount']] = jobs[['masterNodesCount', 'workerNodesCount', 'infraNodesCount', 'totalNodesCount']].fillna(0)
        jobs.fillna('', inplace=True)
        jobs['benchmark'] = jobs.apply(utils.updateBenchmark, axis=1)
        jobs['platform'] = jobs.apply(utils.clasifyAWSJobs, axis=1)
        jobs['jobStatus'] = jobs.apply(utils.updateStatus, axis=1)
        jobs['build'] = jobs.apply(utils.getBuild, axis=1)
        jobs['shortVersion'] = jobs['ocpVersion'].str.slice(0, 4)

        return jobs[jobs['platform'] != ""]
    
    except Exception as err:
        print(f"{type(err).__name__} was raised in quay.py: {err}") 
        
def buildFilterQuery(filter: dict, query: dict):
    minimum_match = 0
    filter_dict = json.loads(filter)
    if bool(filter_dict):
        for key,val in filter_dict.items():
            if key == "workerNodesCount":
                query["query"]["bool"]["filter"].append({"terms":{"workerNodesCount":val}})
            elif key == "build":    
                for item in filter_dict["build"]:                
                    buildObj = getMatchPhrase("ocpVersion", item) 
                    query["query"]["bool"]["should"].append(buildObj)
                minimum_match+=1
            elif key == "jobType":
                for item in filter_dict["jobType"]:
                    obj = getMatchPhrase("upstreamJob", item)                      
                    query["query"]["bool"]["should"].append(obj)
                minimum_match+=1
            elif key == "isRehearse":
                rehearseObj = {"match_phrase": {"upstreamJob":"rehearse"}}
                if True in filter_dict["isRehearse"]:
                    query["query"]["bool"]["should"].append(rehearseObj)
                    minimum_match+=1
                if False in filter_dict["isRehearse"]:
                    query["query"]["bool"]["must_not"].append(rehearseObj)
            else:
                
                for item in filter_dict[key]:
                    queryObj = getMatchPhrase(key, item) 
                    query["query"]["bool"]["should"].append(queryObj)
                minimum_match+=1
    if len(query["query"]["bool"]["should"]) >= 1:
        query["query"]["bool"].update({"minimum_should_match": minimum_match})
    
    return query    

def getMatchPhrase(key:str, item:str):
    buildObj = {"match_phrase": {key: item}}  
    return buildObj