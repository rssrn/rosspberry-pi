from newsapi import NewsApiClient
from beeprint import pp
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import datetime
import collections
import time

newsapi = NewsApiClient(api_key='89487e14389244b88f51115a0624c3f4')

def countNews(search_term):
    global newsapi
    
    today_date = datetime.date.today()
    today = today_date.strftime('%Y-%m-%d')

    news = newsapi.get_everything(
        q='"' + search_term + '"',
        language='en',
        sort_by='relevancy',
        page_size=100,
        from_param=today,
        to=today
    )


    boring_words = [
        'to',
        '-',
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

r = CollectorRegistry()
for term in search_terms:
    count, words = countNews(term)
    g = Gauge(gaugeName(term), \
              'Hits on search for news about ' + term, \
              registry = r)
    g.set(count)
    push_to_gateway('localhost:9091', job='news', registry=r)
    time.sleep(1)
