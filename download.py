# -*- coding: utf-8 -*-
import logging
import os
import requests
import urllib
import re

def main():
    with open('pansci_article_urls.txt', 'r') as urls:
        # 利用diffbot的article API抓取文章內容
        articleAPI = 'https://api.diffbot.com/v3/article'
        # 取出文章id
        filenamePat = re.compile('(?<=\?p\=)([0-9]+)')
        params = {
            'fields':'text',
            'token':'84af59f2abf93b237700517d8e4dc4e5',
            'paging':'false'
        }
        for url in urls:
            params['url'] = url
            fileId = filenamePat.search(url).group(0)

            if(os.path.isfile('corpora/' + fileId + ".txt")):
                print("file is already downloaded")
                continue
            try:
                r = requests.get(articleAPI, params=params)
                if(r.status_code != 200):
                    print("something wrong:", url)
                else:
                    data = r.json()
                    with open('corpora/' + fileId + ".txt", 'w+') as f:
                        f.write(data['objects'][0]['text'])
                    # id對應標題另外存
                    with open('corpora/title.txt', 'a+') as f:
                        f.write(fileId + ":" + data['objects'][0]['title'] +"\n")
            except:
                print("nothing, keep going", url)

if __name__ == "__main__":
    main()
