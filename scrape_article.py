# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import time, os
from datetime import datetime

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    self.app.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    self.app.quit()

# Function to print message with system time
def Log(mesg):
    print(datetime.now().strftime('%H:%M:%S') + ' ' + mesg)
    return

Log('scrape_article starts...')

# Main program begins
if len(sys.argv)<2:
    print('Pls. pass the article url as parameter.')
    print('Usage: python scrape_article.py <url>')
    quit()  # Exit program

# Define project home path
#project_path = '.'  # for Windows or RPi interactive
project_path = '/home/pi/Projects/onccnews'  # for RPi cron job
tmp_path = project_path+'/tmp'  # for RPi cron job

domain = 'http://orientaldaily.on.cc'
oncc_url = str(domain + sys.argv[1])
Log('Scraping ' + oncc_url)
#oncc_url = 'http://orientaldaily.on.cc/cnt/news/20160920/00186_001.html'
i = articleId = oncc_url.rfind('/')  # Search last '/' char to get the aricle Id
articleId = oncc_url[i+1:]
articleTmpFile = tmp_path+'/'+articleId+'.txt'

# declare variable for jinja
output_list=[]

#Commented on 29.11.2017
#Fail to use lxml in crontab mode to render webpage.
#lxml works fine in interactive mode.
#Instead, use PhantomJS in crontab mode.
# Scape web page by lxml
#r = Render(oncc_url)
cmd = 'phantomjs '+project_path+'/saveWebPage.js '+oncc_url+' > '+articleTmpFile
os.system(cmd)
Log('Sleep 10 secs...')
time.sleep(10)
# Parsing data by Beautiful Soup
#soup = BeautifulSoup(r.frame.toHtml(), 'html.parser') #for lxml method
soup = BeautifulSoup(open(articleTmpFile, encoding='utf-8'), 'html.parser') #for PhantomJS
#print (soup.encode('utf-8'))
title = soup.find('h1')  # Get aritcle title
#print(title)
heading = title.text
output_list.append('<i><h1>' + heading + '</h1></i>')
heading=title.text

# Get text
for paragh in title.find_all_next('p'):
    # Check if previous tag is a header, get it if it is
    prev = paragh.find_previous()
    if prev.name == 'h3':
        #print(prev)
        output_list.append('<i><h3>' + prev.text + '</h3></i>')
    #print(paragh)
    output_list.append('<p>' + paragh.text + '</p><br>')

# Get Author for commentary article (if any)
author = soup.find('div', class_='authorInfo')
if author is not None:
    #print('author=' + author.text)
    output_list.append('<p>' + author.text + '</p><br>')

# Get photo
aTags = title.find_all_next('a')
for aTag in aTags:
    if aTag.has_attr('title') and aTag.has_attr('class'):
        if aTag['class'][0] == 'thickbox':
#            print(aTag['title'])
#            print(aTag['href'])
            output_list.append('<p class="normal"><img src="' + domain + aTag['href'] + '"><br><i>' + aTag['title'] + '</i></p>' )

# Create output folder <yymmdd>
folder = project_path + '/' + time.strftime('%Y%m%d')
if not os.path.exists(folder):
    os.makedirs(folder)
    Log('Folder ' + folder + ' created.')

'''
# Save source code of the entire page for debugging
sourceFile = os.path.join(folder, articleId + '_source.html')
with open(sourceFile, "w", encoding="utf8") as f:
    f.write(r.frame.toHtml())
    print(sourceFile + ' saved.')
'''

# Using jinja to create html page from extracted data
templateLoader = FileSystemLoader( searchpath=project_path )
env = Environment( loader=templateLoader )
env.globals.update(zip=zip)  #to use zip which can iterate 2 lists
TEMPLATE_FILE = "tmpl_article.html"
template = env.get_template( TEMPLATE_FILE )
output = template.render(heading=heading, output=output_list, oncc_url=oncc_url)
#print(output)
#filename = 'oncc_' + time.strftime("%Y%m%d") + '.html'
filename = os.path.join(folder, articleId)
with open(filename, "w", encoding="utf-8") as f:
    f.write(output)
    Log(filename + ' saved.')
f.close()
Log('Sleep 2 secs...')
time.sleep(2)
Log('End of scrape_article.')
