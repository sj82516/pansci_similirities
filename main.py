# -*- coding: utf-8 -*-
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
from gensim import corpora, models, similarities
import os
import json
import jieba
import re

# 文件篩選機制，文件的名稱格式為 123.txt
textPat = re.compile('([0-9]*)\.txt')

def main():
    preprocess()
    genDictionary()
    doc2bow()
    genTfIdf()
    genArticleTopSimilarities()


def preprocess():
    """
    預處理資料，輪詢所有文章，並產生個別文章斷詞，另存於 corpora_seg/中
    """
    # jieba custom setting.
    jieba.set_dictionary('jieba_dict/dict.txt.big')
    # load stopwords set
    stopwordset = set()
    with open('jieba_dict/stopwords.txt','r',encoding='utf-8') as sw:
        for line in sw:
            stopwordset.add(line.strip('\n'))

    article_num = 0
    # 輪詢每篇文章
    for root, dirs, filenames in os.walk("corpora/"):
        for f in filenames:
            if textPat.match(f):
                fullpath = os.path.join("corpora/",f)

                #針對每篇文章處理斷詞，並另外存到 corpora_seg
                output = open('corpora_seg/'+ f,'w+')
                with open(fullpath, 'r') as content:
                    for line in content:
                        line = line.strip('\n')
                        words = jieba.cut(line, cut_all=False)
                        for word in words:
                            if word not in stopwordset:
                                output.write(word +' ')
                output.close()

def genDictionary():
    """
    讀取所有文章產生字典，存於 pansci.dict
    """
    dictionary = corpora.Dictionary()
    for root, dirs, filenames in os.walk("corpora_seg/"):
        for f in filenames:
            if textPat.match(f):
                fullpath = os.path.join("corpora_seg/", f)

                with open(fullpath, 'r') as content:
                    for line in content:
                        dictionary.add_documents([line.split()])
    dictionary.save('pansci.dict')
    # print(dictionary)
    # print(dictionary.token2id)

def doc2bow():
    """
    利用字典，將corpora_seg運用doc2bow轉換成，存於 pansci.mm
    """
    dictionary = corpora.Dictionary.load('pansci.dict')
    corpus_memory_friendly = MyCorpus(dictionary)
    corpora.MmCorpus.serialize('pansci.mm', corpus_memory_friendly)

def genTfIdf():
    """
    讀取字典與corpora_seg建立 ITIDF模型
    """
    if (os.path.exists("pansci.dict")):
        dictionary = corpora.Dictionary.load('pansci.dict')
        corpus = corpora.MmCorpus('pansci.mm')
        print("Used files generated from first tutorial")
    else:
        print("Please run first tutorial to generate data set")

    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    # for doc in corpus_tfidf:
    #     print(doc)

    # 300維用來後續計算相似度
    lsi_300 = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    lsi_300.save('pansci_300.lsi')

    # 2維用來顯示文章在2維空間中的相似度，並寫入 article_2d.json
    lsi_2 = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2)
    lsi_300.save('pansci_2.lsi')


def genArticleTopSimilarities():
    """
    輪詢文章，找出前十大相似的文章，並輸出到 article_similarities.json
    """
    corpus = corpora.MmCorpus('pansci.mm')
    dictionary = corpora.Dictionary.load('pansci.dict')
    lsi = models.LsiModel.load('pansci_300.lsi')
    index = similarities.MatrixSimilarity(lsi[corpus])
    # 讀取title.txt，找出 id => title
    titles = {}
    titlePat = re.compile('([0-9]*):(.*)')
    with open('corpora/title.txt') as output:
        for line in output:
            result = titlePat.search(line)
            titles[result.group(1)] = result.group(0)
    # 處理文章順序參照 os.listdir()，需要將id轉換回 index => title
    indexes = []
    for f in os.listdir("corpora/"):
        if textPat.match(f):
            result = textPat.search(f)
            if result != None:
                result = result.groups()
                if result[0] in titles:
                    indexes.append(titles[result[0]])
                else:
                    indexes.append("NotFound")
    for c in corpus:
        sims = index[lsi[c]]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        print([(indexes[sim[0]], sim[1]) for sim in sims[0:5]])


class MyCorpus(object):
    """
    參考gensim官方教學，用每次讀一行 memory-friendly方式處理
    """
    def __init__(self, dictionary, clip_docs=None):
        """
        Parse the first `clip_docs` Wikipedia documents from file `dump_file`.
        Yield each document in turn, as a list of tokens (unicode strings).

        """
        self.dictionary = dictionary

    def __iter__(self):
        self.titles = []
        for root, dirs, filenames in os.walk("corpora_seg/"):
            for f in filenames:
                if textPat.match(f):
                    fullpath = os.path.join("corpora_seg/", f)
                    with open(fullpath, 'r') as content:
                        for line in content:
                            yield self.dictionary.doc2bow(line.split())


if __name__ == "__main__":
    main()
