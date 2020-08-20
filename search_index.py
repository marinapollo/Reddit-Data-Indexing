from elasticsearch import Elasticsearch


def results(es, es_index, query_str,year,month,first_day,last_day,subreddits):
    """Return results for query_str in es_index"""
    return es.search(index=es_index, body={
            "query": {
                "bool" : {
                    
                    "must": [{
                      "match_phrase": {
                        "body": query_str
                      }
                    },
                    {
                      "range": {
                        "day": {
                          "gte": first_day,
                          "lte": last_day
                        }
                      }
                    }
                  ],
                    "filter":[
                       { "term":  { "month": month }}, 
                       { "term":  { "year": year }},
                       { "terms":  { "subreddit": subreddits}}
                       
                   ]
                
                }
            }
        })

def results2(es, es_index, query_str,year,month,day):
    """Return results for query_str in es_index"""
    # TODO
    #print(query_str,month,year,day)
    return es.search(index=es_index, body={
            "query": {
                "bool" : {
                   'must' : {
                       'match_phrase' : {
                           'body': query_str
                       }
                   },
                   "filter":[
                       { "term":  { "month": month }}, 
                       { "term":  { "year": year }},
                       { "term":  { "day": day }},
                       { "terms":  { "subreddit": ["entertainment","movies"] }}
                       
                   ]
                }
            }
        })


def hit_subreddit(hit):
    """Return title of hit"""
    return hit["_source"]["subreddit"]


def hit_body(hit):
    """Return text of hit"""
    return hit["_source"]["body"]


def get_posts(input_str,index_name):
    es = Elasticsearch()
    data = input_str.split(" ")
    query_str, dayF, dayS, month, year = data[:-4], data[-4],data[-3],data[-2], data[-1]
    query_str = " ".join(query_str)    
    subreddits = ["entertainment","movies"]
    
    res = results(es, index_name, query_str, year,month, dayF,dayS,subreddits)
    bodies = []
    for hit in res['hits']['hits']:
        body = hit_body(hit)
        bodies.append(body)
    return bodies

def main(index_name):

    es = Elasticsearch()

    while True:
        input_str = input("Query firstDay secondDay Month Year: ").strip()
        
        data = input_str.split(" ")
        query_str, dayF, dayS, month, year = data[:-4], data[-4],data[-3],data[-2], data[-1]
        query_str = " ".join(query_str)

        if not query_str:
            break

        subreddits = ["entertainment","movies"]
        res = results(es, index_name, query_str, year,month, dayF,dayS,subreddits)
        bodies = []
        for hit in res['hits']['hits']:
            subreddit = hit_subreddit(hit)
            body = hit_body(hit)
            bodies.append(body)
        print(" ".join(bodies))

if __name__ == "__main__":
    index_name = sys.argv[1]
    main(index_name)

 