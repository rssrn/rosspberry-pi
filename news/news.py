from newsapi import NewsApiClient
from beeprint import pp
from prometheus_client import CollectorRegistry, Gauge, Counter, push_to_gateway
from datetime import datetime, date, timedelta
import collections
import time
import os
import timeit

start_time = datetime.now()

key = os.environ['NEWS_API_KEY']
newsapi = NewsApiClient(key)

def countNews(search_term):
    global newsapi
    
    today_date = date.today()
    today = today_date.strftime('%Y-%m-%d')

    yesterday_date = today_date - timedelta(days=1)
    yesterday = yesterday_date.strftime('%Y-%m-%d')

    tomorrow_date = today_date + timedelta(days=1)
    tomorrow = tomorrow_date.strftime('%Y-%m-%d')

    news = newsapi.get_everything(
        q='"' + search_term + '"',
        language='en',
        sort_by='relevancy',
        page_size=100,
        from_param=today,
        to=tomorrow
    )


    boring_words = [
        'to',
        '-',
        '&',
        'as',
        'in',
        'the',
        'a',
        'is',
        'be',
        'by',
        'what',
        'say',
        'and',
        'of',
        'for',
        'from',
        'on',
        'or',
        'at',
        'her',
        'his',
        'says',
        'have',
    ]
    boring_words.append(search_term.lower())
    boring_words.extend([x.lower() for x in search_term.split()])
    
    words = []
    for article in news['articles']:
        if article['title'] is None:
            continue
        words.extend(article['title'].split())
        # get pairs of words as well
        prev_word = ''
        for w in article['title'].split():
            if (prev_word == ''):
                prev_word = w
                continue
            if (prev_word.lower() in boring_words or w.lower() in boring_words):
                prev_word = w
                continue
            pair = prev_word + ' ' + w
            prev_word = w
            words.append(pair)
                
    cleaned_words = []
    for w in words:
        if w.lower() not in boring_words:
            cleaned_words.append(w)

    counter = collections.Counter(cleaned_words)

    print(search_term)
    print(counter.most_common()[:10])
    print(news['totalResults'])
    return news['totalResults'],counter.most_common()[:10]

def writeTermsDetail(term,words):
    pass

def gaugeName(term):
    return 'news_' + term.replace(' ','_') + "_hits"

search_terms = [
    'new zealand',
    'brexit',
    'london',
    'impeachment',
    'openbet',
    'sg digital',
    'scientific games'
]

i_search_terms_checked = 0
r = CollectorRegistry()
for term in search_terms:
    count, words = countNews(term)
    g = Gauge(gaugeName(term), \
              'Hits on search for news about ' + term, \
              registry = r)
    g.set(count)

    writeTermsDetail(term, words)
    
    i_search_terms_checked += 1
    time.sleep(1)

#--------------------- Start Instrumentation ------------------------------
i_term_count = Gauge('news_script_searchterms_checked_count', \
                     'Number of search terms checked by script in one run', \
                     registry = r)
i_term_count.set(i_search_terms_checked)

i_exec_time = Gauge('news_script_exec_duration_milliseconds', \
                   'Total time for one run of news collection script', \
                   registry = r)
dt = datetime.now() - start_time
ms_delta = (dt.days *24*60*60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
print('execution time ' + str(ms_delta))
i_exec_time.set(ms_delta)

i_last_exec = Gauge('news_script_exec_timestamp_seconds', \
                    'last time news script executed', \
                    registry = r)
i_last_exec.set_to_current_time()
#--------------------- End Instrumentation --------------------------------

push_to_gateway('localhost:9091', job='news', registry=r)
