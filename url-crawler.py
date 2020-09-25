import sys
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
from multiprocessing import Pool

url1 = "http://caucusconnect.com"
url2 = "https://scrapethissite.com"
url3 = "https://cnn.com"
############## DATA STRUCTURES ##############
toBeCrawled = deque([url2]) # deque to store urls left to crawl (original url and ones that come from it)

def spider(url):
    finished_urls = set() # set to store urls that are already crawled and processed
    local_urls = set() # set to store local domains of a visited website
    foreign_urls = set() # set to store foreign domains reached from a visited website
    broken_urls = set() # set to store broken urls of a visited website


    # process urls from queue
    # for i in range(len(toBeCrawled)):
    while len(toBeCrawled):
    # while (False):
        url = toBeCrawled.popleft() # move url from the queue to processed url set, popleft() returns url that is popped
        finished_urls.add(url)
        # print the current url
        print("Processing %s" % (url,))

        # add broken urls to broken_urls set
        try:
            response = requests.get(url)
        except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
            broken_urls.add(url) # if no response, then add to set in except statement
            continue

        # get base url to differentiate local/foriegn urls
        parts = urlsplit(url)
        base = "{0.netloc}".format(parts)
        strip_base = base.replace("www.", "")
        base_url = "{0.scheme}://{0.netloc}".format(parts) 
        path = url
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]
        else:
            path = url

        soup = BeautifulSoup(response.text, "lxml")
        # scrape links
        links = soup.findAll('a')
        for link in links:
            # get link url from the anchor
            anchor = ''
            if "href" in link.attrs:
                anchor = link.attrs["href"]

            # add to corresponding set
            if anchor.startswith('/'):
                local_link = base_url + anchor
                local_urls.add(local_link)
            elif strip_base in anchor:
                local_urls.add(anchor)
            elif not anchor.startswith('http'):
                local_link = path + anchor
                local_urls.add(local_link)
            else:
                foreign_urls.add(anchor)

            # if not link in toBeCrawled and not link in finished_urls:
            #     toBeCrawled.append(link)
        # get only local urls
        for i in local_urls:
            if not i in toBeCrawled and not i in finished_urls:
                toBeCrawled.append(i)

# spider(toBeCrawled, finished_urls, local_urls, foreign_urls, broken_urls)

p = Pool(50)
p.map(spider, toBeCrawled)
p.terminate()
p.join()

# print("First name: " + sys.argv[1])
# print("Last name: " + sys.argv[2])