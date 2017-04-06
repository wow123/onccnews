# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import time, os
from datetime import datetime, timedelta
import shutil

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

# Funnction to return weekday in Chinese
def WeekdayInChinese(Engday):
    weekday = Engday.upper()
    if weekday == 'MON':
        Chiday = '一'
    elif weekday == 'TUE':
        Chiday = '二'
    elif weekday == 'WED':
        Chiday = '三'
    elif weekday == 'THU':
        Chiday = '四'
    elif weekday == 'FRI':
        Chiday = '五'
    elif weekday == 'SAT':
        Chiday = '六'
    else:
        Chiday = '日'
    return '星期' + Chiday

# Function to print message with system time
def Log(mesg):
    print(datetime.now().strftime('%H:%M:%S') + ' ' + mesg)
    return

# Define project home path
#project_path = '.'  # for Windows or RPi interactive
project_path = '/home/pi/Projects/onccnews'  # for RPi cron job

Log('scrape_index starts...')
domain = 'http://orientaldaily.on.cc'
# Scape web page by lxml
r = Render(domain)
# Parsing data by Beautiful Soup
soup = BeautifulSoup(r.frame.toHtml(), 'html.parser')
#print (soup.encode('utf-8'))

# Get cover image
head_img = soup.find('img', class_='headline')
head_img_url = domain + head_img['src']

# Get all items from the Drop Down List
drop_down_list = soup.find('select', id='articleListSELECT')
# Tag structure of drop_down_list:
# <select id="articleListSELECT" ...> <optgroup label=...> <option value=...> </option> </optgroup> </select>
article_type=[]
article_title=[]
article_href=[]
article_oncc_href=[]
for optgroup in drop_down_list.findAll('optgroup'):
#    print('inside optgroup')
#    print(optgroup)
    # Add group label to the lists
    article_type.append('G')  # group label
    article_title.append(optgroup['label'])
    article_href.append('')
    article_oncc_href.append('')
    for option in optgroup.findAll('option'):
        # Add oncc link for each article for later use of scrape_article
        oncc_href = option['value']
        article_oncc_href.append(oncc_href)
        # Add article to the list variables
        article_type.append('A')  # article
        article_title.append(option.text)
        i = option['value'].rfind('/')  # Search last '/' char to get the aricle Id
        article_href.append(option['value'][i+1:])

# Create output folder <yymmdd>
folder = project_path + '/' + time.strftime('%Y%m%d')
if not os.path.exists(folder):
    os.makedirs(folder)
    Log('Folder ' + folder + ' created.')

# Using jinja to create html page from extracted data
templateLoader = FileSystemLoader( searchpath=project_path)
env = Environment( loader=templateLoader )
env.globals.update(zip=zip)  #to use zip which can iterate 2 lists
TEMPLATE_FILE = 'tmpl_index.html'
template = env.get_template( TEMPLATE_FILE )
newsdate = time.strftime('%d-%m-%Y') + ' ~ ' + WeekdayInChinese(time.strftime('%a'))
output = template.render(newsdate=newsdate, types=article_type, titles=article_title, hrefs=article_href, head_img_url=head_img_url)
#print(output)
filename = os.path.join(folder, 'index.html')
with open(filename, 'w', encoding='utf-8') as f:
    f.write(output)
    Log(filename + ' saved.')

# Delete yesterday folder <yymmdd - 1>
yday = datetime.today() - timedelta(days=1)
yfolder = project_path + '/' + yday.strftime('%Y%m%d')
if os.path.exists(yfolder):
    shutil.rmtree(yfolder, ignore_errors=True)
    Log('Folder ' + yfolder + ' deleted.')
else:
    Log('Folder ' + yfolder + ' not exists.')

# Amend on 6.4.2017
# Loop to scrape each article
for t, h in zip(article_type, article_oncc_href):
    if t == 'A':
        print(h)
        # Call scrape_article.py
#        cmd = 'python scrape_article.py ' + oncc_href  # for windows
        cmd = 'python3 ' + project_path + '/scrape_article.py ' + oncc_href  # for RPi
#        os.system(cmd)
