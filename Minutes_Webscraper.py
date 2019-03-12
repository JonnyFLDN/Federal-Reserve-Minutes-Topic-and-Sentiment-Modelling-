#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: JonnyFLDN
"""
import requests
from bs4 import BeautifulSoup
import os
import re
from concurrent.futures import ProcessPoolExecutor


def minarchive(year):
    url_main = 'https://www.federalreserve.gov'
    year = int(year)
    
    if year > 2012: #Post 2012 has a different URL
        url = url_main+'/monetarypolicy/fomccalendars.htm'
    else:
        url = url_main + '/monetarypolicy/fomchistorical'+str(year)+'.htm'
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    min_link = soup.findAll('a',href=re.compile('(?=.*minutes)(?=.*'+str(year)+')'), 
                                text=lambda text: text and 'PDF' not in text)
    
    #Methods
    m0={'name':'div','attrs':{'id':'article'}}
    m1={'name':'div','attrs':{'id':'leftText'}}
    m2={'name':'p'}
    
    for m in min_link:
        url = str(m['href']) if 'federalreserve.gov' in str(m['href']) else url_main + str(m['href'])
        filename = re.search("(\d{4})(\d{2})(\d{2})",url)[0]
        soup = BeautifulSoup(requests.get(url).content,'lxml')
        
        i=0
        
        main_text=[]
        while not main_text and i<3:
            main_text = soup.findAll(**eval('m'+str(i)))
            i += 1        
        saveFile(filename,year,main_text)


def saveFile(fname,year,text):
    main_directory = '/Users/jonny/Python_work/FedMin/Minutes/'
    os.chdir(main_directory)
    directory = os.join(main_directory, str(year))
    
    if not os.path.exists(directory):
        os.makedirs(directory)
        #check if file name already exists
    if not os.path.isfile(fname):
        os.chdir(directory)
        with open(fname + '.txt', 'w', encoding='utf-8') as f:
            text_clean = '\n'.join(t.text for t in text)
            text_clean = re.sub(r'\r\n', ' ', text_clean)
            text_clean = re.sub(r'(?<!\n)\n(?!\n)', r'\n\n', text_clean)

            print(text_clean)
            f.write(text_clean)


if __name__ == '__main__':
    start_year, end_year = 2004, 2018
    with ProcessPoolExecutor(max_workers=4) as pool:
        for year in range(start_year, end_year + 1):
            pool.submit(minarchive, year)
