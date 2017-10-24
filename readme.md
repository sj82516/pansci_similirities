### 找出Pansci相似文章
擷取pansci 約2700篇文章，透過gensim計算文章相似度。

### 檔案目錄架構
/corpora : 用diffbot抓取pansci文章內文，分id儲存，詳見 download.py  
/corpora : 將/corpora中的所有文章，利用jieba斷詞後儲存  
/jieba_dict : jeiba相關文件  

### 運行方式  
採用 Python 3.6，外部函式庫需安裝 jieba、gensim，如果文章沒有下載先執行 download.py，目前專案上有，所以不用另外載。   
接著執行 main.py，以下補充main.py與相關產生的文件說明  
1. 將/corpora_seg中的文件，建立字典並存於 pansci.dict     
2. 將/corpora_seg中的文件，先將文章用Bag-of-Word轉換，並將字對應字典轉換為向量，生成 pansci.mm   
3. 將pansci.mm透過td-idf轉換，接著建立LSI模型，存於 pansci_300.lsi等相關檔案，pansci_2.lsi是為了2維圖式向量表達  
4. 最後利用 pansci_300.lsi建立相似度模型比對，打印輸出為 輪詢每一篇文章並找出前五相似的文章，可以看到每次輸出的第一篇相似度逼近1，因為那篇就是自己(itself)  

### TODO  
1. 輸出2維圖示，建立靜態網站顯示  
2. 相似度比對似乎不太準，需要加強  
3. 文章一開始下載有儲存 id => 標題，存於 /corpora/title.txt，最後將相似度的文章順序id對比標題，可是不確定是否正確，需要有個回推原文的機制，方便判讀。
