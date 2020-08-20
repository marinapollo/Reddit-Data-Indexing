import argparse, sys, os
from elasticsearch import Elasticsearch
from reddit_indexing import RedditData


def files_in_dir(base_directory):
    """Return list of files in directory"""
    filelist = []
    for path,dirs,files in os.walk(base_directory):
        for filename in files:
            filelist.append(os.path.join(path,filename))
    return filelist


def add_to_index(es, es_index, doc,id):
    """Add doc to es_index"""
    es.index(index=es_index, doc_type='article', id=int(id), body=doc)#doc['id']


def doc_from_article(article,month=None,year=None,day=None):
    """Return elasticsearch document for article"""
    doc = {}
    if day:
        doc = {
            'id': article.id,
            'subreddit': article.subreddit,
            'body': article.body,
            'month': article.m,#month,
            'year': article.y,#year,
            'day': article.d,#day

        }
    else:
        doc = {
            'id': article.id,
            'subreddit': article.subreddit,
            'body': article.body,
            'month': article.m,#month,
            'year': article.y,#year
            'day': article.d,#day
        }
    return doc



def main(path, index_name):
    '''
    before running the script, type: 
    cd elasticsearch-7.9.0/bin
    ./elasticsearch
    '''
    ES_HOST = {"host" : "localhost", "port" : 9200} # ES localhost;
    es = Elasticsearch()

    # Delete index if it already exists
    if es.indices.exists(index=index_name):
        print("deleting index")
        es.indices.delete(index=index_name)
    
    target_subreddits = ['movies', 'entertainment']
    files = files_in_dir(path)
    for i in range(len(files)):
        
        print("\rFile %d out of %d" % (i+1,len(files)), end = "")
        f = files[i]        
        movieMatch = False
        i = i+1
        for j,article in enumerate(RedditData.iterator_from_file(f)):
            id = str(i)+str(j)
            if article:
                doc = doc_from_article(article)
                if article.subreddit in target_subreddits:
                    movieMatch = True
                    add_to_index(es, index_name, doc, id)
    es.indices.refresh(index=index_name)

    
if __name__ == "__main__":
    index_name = sys.argv[1]
    path = "/mounts/data/proj/sedinkina/reddit/zipped_reddit"#change to 2007
    main(path,index_name)
