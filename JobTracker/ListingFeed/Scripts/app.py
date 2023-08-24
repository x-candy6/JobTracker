import time
import feedparser
from .models import Indeedlistings, Providers, Urls


file = open("./urls.txt", "r")
sample = "http://rss.indeed.com/rss?q=IT+Support&l=Cypress%2C+CA&radius=35"
urls = file.readlines()

responses = []
fr = (33.837, -118.042)
def distance(f: tuple, t: tuple):
    f = fr
    

    return f, t

def parser():
    for url in urls:
        #a = client.get(url)
        b = feedparser.parse(url)
    
        for i in b.entries:
            print(i.id, "\n", i.title, "\n" , i.links[0].href, "\n", i.published, "\n", i.summary, "\n",i.where.type, " - ", i.where.coordinates  ,"\n\n")
            responses.append(i)
        b = None
        time.sleep(15)



    print(responses[0].entries[0])
    for x in responses:
        for i in x.entries:
            entry = IndeedListings(
                id = i.id,
                title = i.title,
                category_id = "",#TODO
                location = i.where.coordinates,
                distance = distance(fr, i.where.coordinates),
                summary = i.summary,
                link = i.links[0].href,
                flag = False,
                remove = False,
                finish = False,
                in_progress = False
            )

            #print(i.id, "\n", i.title, "\n" , i.links[0].href, "\n", i.published, "\n", i.summary, "\n",i.where.type, " - ", i.where.coordinates  ,"\n\n")
    print(b.entries[0])
    
    
    print(len(responses))

def testparser():

    b = feedparser.parse(sample)
    sample_entry = b.entries[0]

    entry = IndeedListings(
        id = sample_entry.id,
        title = sample_entry.title,
        category_id = "",#TODO
        location = sample_entry.where.coordinates,
        distance = distance(fr, sample_entry.where.coordinates),
        summary = sample_entry.summary,
        link = sample_entry.links[0].href,
        flag = False,
        remove = False,
        finish = False,
        in_progress = False
    )
    entry.save()
    return "testparser() end"
    

testparser()
#b = feedparser.parse(sample)
#print(distance(fr, (1,2)))


