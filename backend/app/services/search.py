from elasticsearch import AsyncElasticsearch
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
from app import config
import bisect
import re

    
class ElasticService:
    # todo add bulkhead pattern
    # todo add error message for unauthorized user
    def __init__(self,configpath="",index=""):
        """Init method."""
        cfg = config.get_config()
        self.new_es, self.new_index, self.new_index_prefix = self.initialize_es(cfg, configpath, index)
        self.prev_es = None
        if cfg.get(configpath + '.internal'):
            self.prev_es, self.prev_index, self.prev_index_prefix = self.initialize_es(cfg, configpath + '.internal', index)

    def initialize_es(self, config, path, index):
        """Initializes es client using the configuration"""
        url = config.get(path+'.url')
        esUser = None
        index_prefix = ""
        if index == "":
            indice = config.get(path+'.indice')
        else:
            indice = index
        if config.is_set(path+'.prefix'):
            index_prefix = config.get(path+'.prefix')
        if config.is_set(path+'.username') and \
                config.is_set(path+'.password'):
            esUser = config.get(path+'.username')
            esPass = config.get(path+'.password')
        if esUser :
            es = AsyncElasticsearch(
                    url,
                    use_ssl=False,
                    verify_certs=False,
                    http_auth=(esUser,esPass)
            )
        else:
            es = AsyncElasticsearch(url, verify_certs=False)
        return es, indice, index_prefix

    async def post(self, query, indice=None, size=2, start_date=None, end_date=None, timestamp_field=None):
        """Runs a query and returns the results"""
        try:
            print("hydrogen")
            if size == 0:
                print("helium")
                """Handles aggregation queries logic"""
                if self.prev_es:
                    print("if helium")
                    self.prev_index = self.prev_index_prefix + (self.prev_index if indice is None else indice)
                    a = await self.prev_es.search(
                        index=self.prev_index+"*",
                        body=jsonable_encoder(query),
                        size=size)
                    print(a)
                    return a
                else:
                    print("lithium")
                    self.new_index = self.new_index_prefix + (self.new_index if indice is None else indice)
                    return await self.new_es.search(
                        index=self.new_index+"*",
                        body=jsonable_encoder(query),
                        size=size)
            else:
                """Handles queries that require data from ES docs"""
                print("Beryllium")
                if timestamp_field:
                    print("carbon")
                    """Handles queries that have a timestamp field. Queries from both new and archive instances"""
                    if self.prev_es:
                        print("nitrogen")
                        self.prev_index = self.prev_index_prefix + (self.prev_index if indice is None else indice)
                        today = datetime.today().date()
                        seven_days_ago = today - timedelta(days=7)
                        if start_date and start_date > seven_days_ago:
                            previous_results = {}
                        else:
                            print("oxygen")
                            new_end_date = min(end_date, seven_days_ago) if end_date else seven_days_ago
                            query['query']['bool']['filter']['range'][timestamp_field]['lte'] = str(new_end_date)
                            if start_date:
                                query['query']['bool']['filter']['range'][timestamp_field]['gte'] = str(start_date)
                            if start_date is None:
                                response = await self.prev_es.search(
                                    index=self.prev_index+"*",
                                    body=jsonable_encoder(query),
                                    size=size)
                                previous_results = {"test":response['hits']['hits'], "total":response['hits']["total"]["value"]}
                            else:
                                previous_results = await self.scan_indices(self.prev_es, self.prev_index, query, timestamp_field, start_date, new_end_date, size)
                    if self.prev_es and self.new_es:
                        print("neon1")
                        self.new_index = self.new_index_prefix + (self.new_index if indice is None else indice)
                        today = datetime.today().date()
                        seven_days_ago = today - timedelta(days=7)
                        if end_date and end_date < seven_days_ago:
                            new_results = {}
                        else:
                            print("carbon")
                            new_start_date = max(start_date, seven_days_ago) if start_date else seven_days_ago
                            query['query']['bool']['filter']['range'][timestamp_field]['gte'] = str(new_start_date)
                            if end_date:
                                query['query']['bool']['filter']['range'][timestamp_field]['lte'] = str(end_date)
                            if end_date is None:
                                response = await self.new_es.search(
                                    index=self.new_index+"*",
                                    body=jsonable_encoder(query),
                                    size=size)
                                new_results = {"test":response['hits']['hits'],"total":response['hits']['total']['value']}
                            else:
                                print("above nenon")
                                new_results = await self.scan_indices(self.new_es, self.new_index, query, timestamp_field, new_start_date, end_date, size)
                        print("nenon")
                        print(previous_results)
                        
                        print("yes") if("test" in previous_results) else print("no")
                        print("nenon2")
                        print(new_results)
                        a=await self.remove_duplicates(previous_results["test"] if("test" in previous_results) else [] + new_results["test"]  if("test" in new_results) else[])
                        print(previous_results["test"] if("test" in previous_results) else [] + new_results["test"] if("test" in new_results) else[])
                        
                        print("q")
                        print(a)
                        print({"test":a, "total": new_results["total"]})
                        print("zumb")
                        return ({"test":a, "total": new_results["total"]})
                    else:
                        if start_date and end_date:
                            query['query']['bool']['filter']['range'][timestamp_field]['gte'] = str(start_date)
                            query['query']['bool']['filter']['range'][timestamp_field]['lte'] = str(end_date)
                            return await self.scan_indices(self.new_es, self.new_index, query, timestamp_field, start_date, end_date, size)
                        else:
                            response = await self.new_es.search(
                                index=self.new_index+"*",
                                body=jsonable_encoder(query),
                                size=size)
                            return {"test":response['hits']['hits'],"total":response['hits']["total"]["value"]}
                else:
                    """Handles queries that do not have a timestamp field"""
                    previous_results = {}
                    if self.prev_es:
                        self.prev_index = self.prev_index_prefix + (self.prev_index if indice is None else indice)
                        response = await self.prev_es.search(
                            index=self.prev_index+"*",
                            body=jsonable_encoder(query),
                            size=size)
                        previous_results = {"test":response['hits']['hits'], "total":response['hits']["total"]["value"]}
                    self.new_index = self.new_index_prefix + (self.new_index if indice is None else indice)
                    response = await self.new_es.search(
                        index=self.new_index+"*",
                        body=jsonable_encoder(query),
                        size=size)
                    new_results = {"test":response['hits']['hits'],"total":response['hits']["total"]["value"]}
                    a=await self.remove_duplicates(previous_results["test"] if("test" in previous_results) else [] + new_results["test"] if("test" in new_results) else [])
                    return ({"test":a, "total": new_results["total"]})
        except Exception as err:
            print(f"{type(err).__name__} was raised: {err}")   
            

    async def scan_indices(self, es_client, indice, query, timestamp_field, start_date, end_date, size):
        """Scans results only from es indexes relevant to a query"""
        print("I'm inside scan indices")
        try:
            indices = await self.get_indices_from_alias(es_client, indice)
            if not indices:
                indices = [indice]
            sorted_index_list = SortedIndexList()
            for index in indices:
                sorted_index_list.insert(IndexTimestamp(index, await self.get_timestamps(es_client, index, timestamp_field)))
            filtered_indices = sorted_index_list.get_indices_in_given_range(start_date, end_date)
            results = []
            for each_index in filtered_indices:
                query['query']['bool']['filter']['range'][timestamp_field]['lte'] = str(min(end_date, each_index.timestamps[1]))
                query['query']['bool']['filter']['range'][timestamp_field]['gte'] = str(max(start_date, each_index.timestamps[0]))
                response = await es_client.search(
                    index=each_index.index,
                    body=jsonable_encoder(query),
                    size=size)
                results.extend(response['hits']['hits'])
            print("above loadd")
            print("loadd")
            # await print(response['hits'])
            # return await self.remove_duplicates(results)
            #print({{"test":  await self.remove_duplicates(results), "total":10}})
            return({"test":await self.remove_duplicates(results) , "total":response['hits']['total']['value']}) 
        except Exception as err:
            print(f"{type(err).__name__} was raised: {err}")
            raise("Exception in scan indices")     
        
        
    async def remove_duplicates(self, all_results):
        print("hydro")
        
        print(all_results)
        seen = set()
        filtered_results = []
        try:
            print("I'm inside duplicated")
            for each_result in all_results:
                flat_doc = flatten_dict(each_result)
                if tuple(sorted(flat_doc.items())) in seen:
                    continue
                else:
                    filtered_results.append(each_result)
                    seen.add(tuple(sorted(flat_doc.items())))
        except Exception as err:
            print(f"{type(err).__name__} was raised: {err}")
        print("hyfro resuks")
        print(filtered_results)
        return filtered_results

    async def get_timestamps(self, es_client, index, timestamp_field):
        """Returns start and end timestamps of a index"""
        query = {
            "size": 2,
            "from": 1,
            "aggs": {
                "min_timestamp": {
                    "min": {
                        "field": timestamp_field
                    }
                },
                "max_timestamp": {
                    "max": {
                        "field": timestamp_field
                    }
                }
            }
        }
        response = await es_client.search(
            index=index,
            body=query
        )
        print("rhodium")
        min_timestamp = response["aggregations"]["min_timestamp"]["value_as_string"]
        max_timestamp = response["aggregations"]["max_timestamp"]["value_as_string"]
        return [datetime.strptime(datetime.strptime(min_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d"), "%Y-%m-%d").date(), 
                datetime.strptime(datetime.strptime(max_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d"), "%Y-%m-%d").date()]

    async def get_indices_from_alias(self, es_client, alias):
        """Get indexes that match an alias"""
        print("I'm alya")
        try:
            indexes = []
            response = await es_client.indices.get_alias(alias)
            index_prefixes = [re.sub(r'-\d+$', '', index) for index in list(response.keys())]
            for each_prefix in index_prefixes:
                response = await es_client.indices.get(each_prefix + '*', format='json')
                indexes.extend(list(response.keys()))
            
            result_set = [alias] if len(indexes) == 0 else indexes
            print("result_set")
            print(result_set)
            return list(set(result_set))
        except Exception as e:
            print(f"Error retrieving indices for alias '{alias}': {e}")
            return []

    async def close(self):
        """Closes es client connections"""
        await self.new_es.close()
        if self.prev_es is not None:
            await self.prev_es.close()

class IndexTimestamp:
    """Custom class to store and index with its start and end timestamps"""
    def __init__(self, index, timestamps):
        self.index = index
        self.timestamps = timestamps

    def __lt__(self, other):
        return self.timestamps[0] < other.timestamps[0]

class SortedIndexList:
    """Custom class to sort indexes based on their start timestamps"""
    def __init__(self):
        self.indices = []

    def insert(self, index_timestamps):
        bisect.insort(self.indices, index_timestamps)

    def get_indices_in_given_range(self, start_date, end_date):
        return [index_timestamp for index_timestamp in self.indices if ((
            start_date and end_date and start_date <= index_timestamp.timestamps[0] and index_timestamp.timestamps[1] <= end_date) 
            or (start_date and index_timestamp.timestamps[0] < start_date and start_date <= index_timestamp.timestamps[1]) 
            or (end_date and index_timestamp.timestamps[1] > end_date and index_timestamp.timestamps[0] <= end_date))]

def flatten_dict(d, parent_key='', sep='.'):
    """Method to flatten a ES doc for comparing duplicates"""
    try:
        print("inside flatten")
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, val in enumerate(v):
                    items.extend(flatten_dict({str(i): val}, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        print("new")
        print(dict(items))
        return dict(items)
    except Exception as err:
        print(f"{type(err).__name__} was raised: {err}")
