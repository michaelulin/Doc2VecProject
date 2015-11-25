import mwclient
from collections import defaultdict
import sys

class getData(object):

    def __init__(self,site,pages):
        self.site = mwclient.Site(site)
        self.pages = self.site.Categories[pages]
        self.data = defaultdict(dict)
        #self.count = 0

    #def create_shelve(self):
    #    self.d = shelve.open('wikivoyage.db')


    def _fetch_data(self,site):
        if type(site) == mwclient.page.Page:
            self.data[site.name] = defaultdict(str)
            self.data[site.name]['text'] = site.text()
            self.data[site.name]['loc'] = site.extlinks().next()


        else:
            #print self.count
            map(self._fetch_data,site.members())

    def fetch_data(self):
        self._fetch_data(self.pages)

    def iterativeChildren(self,nodes):
        #from http://blog.nextgenetics.net/?e=64
        while 1:
            newNodes = []
            if len(nodes) == 0:
                break
            for node in nodes:
                if type(node) != mwclient.page.Page:
                    newNodes += list(node.members())
                    self.data[node.name+"CAT"] = defaultdict(str)
                    self.data[node.name+"CAT"]['text'] = node.text()
                    self.data[node.name+"CAT"]['type'] = "category"
                    try:
                        self.data[node.name+"PAGE"]['loc'] = node.extlinks().next()
                    except:
                        continue
                else:
                    self.data[node.name+"PAGE"] = defaultdict(str)
                    self.data[node.name+"PAGE"]['text'] = node.text()
                    self.data[node.name+"PAGE"]['type'] = "page"
                    try:
                        self.data[node.name+"PAGE"]['loc'] = node.extlinks().next()
                    except:
                        continue

            nodes = newNodes


if __name__ == '__main__':
    #reload(sys)  # Reload does the trick!
    #sys.setdefaultencoding('UTF8')
    gd = getData('en.wikivoyage.org/','United States of America')
    gd.iterativeChildren(list(gd.pages.members()))
