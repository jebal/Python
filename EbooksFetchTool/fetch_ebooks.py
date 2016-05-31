# -*- coding: utf-8 -*-

import os
import urllib
import re
from HTMLParser import HTMLParser
import send_mail


def getEbooksHtml(url):
        page = urllib.urlopen(url)
        html = page.read()
        return html

def getEbooks(html):
        return html

class EbookHTMLParser(HTMLParser):

        def __init__(self):
                HTMLParser.__init__(self)
                self.links = []
        
        def handle_starttag(self, tag, attrs):
                if "a" == tag:
                        if len(attrs) == 0:
                                pass
                        else:
                                for (var, value) in attrs:
                                        if var == "class" and value == "book thumbnail":
                                                self.links.append(attrs[1][1])
                                                        
                
        def handle_endtag(self, tag):
                pass
                #print('</%s>' % tag)

        def handle_startendtag(self, tag, attrs):
                pass
                #print('<%s/>' % tag)

        def handle_data(self, data):
                pass
                #print('data')

        def handle_comment(self, data):
                pass
                #print('<!-- -->')

        def handle_entityref(self, name):
                pass
                #print('&%s;' % name)

        def handle_charref(self, name):
                pass
                #print('&#%s;' % name)


class EbookDownLoadHTMLParser(HTMLParser):

        def __init__(self):
                HTMLParser.__init__(self)
                self.str_link = ""
                self.str_ebook_name = ""
        
        def handle_starttag(self, tag, attrs):
                '''
                这里解析能电子书的下载地址并存于links中
                '''
                pass
                
        def handle_endtag(self, tag):
                pass
                #print('</%s>' % tag)

        def handle_startendtag(self, tag, attrs):
                pass
                #print('<%s/>' % tag)

        def handle_data(self, data):
                pass
                #print('data')

        def handle_comment(self, data):
                pass
                #print('<!-- -->')

        def handle_entityref(self, name):
                pass
                #print('&%s;' % name)

        def handle_charref(self, name):
                pass
                #print('&#%s;' % name)



if __name__ == '__main__':

        # download ebooks
        html = getEbooksHtml(u"http://readcolor.com/books")
        html_parser = EbookHTMLParser()
        html_parser.feed(html)

        html_file = open("Ebooks.html", "w")
        html_file.write(html)
        html_file.close()
        
        for ebooks_link in html_parser.links:
                print "parsering ebook link " + ebooks_link + "..."
                ebook_html = getEbooksHtml(ebooks_link)
                html_parser = EbookDownLoadHTMLParser()
                html_parser.feed(html)
                urllib.urlretrieve(html_parser.str_link, str_ebook_name)

        # send ebooks mail to kindle
        

     
       
