from typing import Text
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import requests
import pickle
import pandas
from collections import Counter
from application import MODEL_FILEPATH
from konlpy.tag import Twitter,Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from wordcloud import WordCloud

MODEL_FILEPATH = os.path.join(os.getcwd(), 'application', 'model', 'model.pkl')
POS_FILEPATH = os.path.join(os.getcwd(), 'application','wordcloud','movie_pos.png')
NAG_FILEPATH = os.path.join(os.getcwd(), 'application','wordcloud','movie_nag.png')
DRIVER_FILEPATH = os.path.join(os.getcwd(),'application','driver','chromedriver')
TRAIN_FILEPATH = os.path.join(os.getcwd(),'application','model','X_train.pkl')
model = None
with open(MODEL_FILEPATH,'rb') as pickle_file:
    model = pickle.load(pickle_file)

with open(TRAIN_FILEPATH,'rb') as train_file:
    X_train = pickle.load(train_file)

twitter=Okt()


def data_load(movie_name):
    """
    input : 영화제목  type: string
    output : 영화리뷰 type: list

    영화 제목을 입력하면 왓챠피디아에서 해당 리뷰를 크롤링해온다. 
    학습데이터를 모을떄도 사용했던 함수와 거의 유사하다.
    """
    BASE_URL=f"https://pedia.watcha.com/ko-KR/searches/movies?query={movie_name}"
    resp = requests.get(BASE_URL)
    if(resp.status_code==200):
        soup = BeautifulSoup(resp.content,'html.parser')
        a_tag = soup.find('a',class_='css-1aaqvgs-InnerPartOfListWithImage')
        if(a_tag!=None):
            link_text = a_tag.get('href').split('/')
        link = link_text[-1]
        return link
    else:
        print(resp.status_code)
# def review_load(movie_name):
#     reviews=[]
#     link = data_load(movie_name)
#     BASE_URL2 = f"https://pedia.watcha.com/ko-KR/contents/{link}/comments"
#     resp2 = requests.get(BASE_URL2)
#     # print("2222",resp2.status_code)
#     # print('11'*50)
#     if(resp2.status_code==200):
#         soup = BeautifulSoup(resp2.content,'html.parser')
#         review_tab = soup.findAll('div',class_='css-bawlbm')
#         # 시간 부족으로 영화 제목이 동일한 경우는 첫번째 영화로처리 
#         for table in review_tab:
#             if(table is not None):
#                 review_ = table.find('div',class_='css-1g78l7j')
#                 if(review_ is not None):
#                     # print(review_)
#                     review_span = review_.find('span')
#                     if(review_span is not None):
#                         # print(review_span)
#                          reviews.append(review_span.text)                   
#         return reviews
#     else:
#         print(resp2.status_code)
#     # print('12'*50)
def load_reviews(movie_name):
    reviews=[]


    link = data_load(movie_name)
    URL =f"https://pedia.watcha.com/ko-KR/contents/{link}/comments"
    
    # Check_Chromedriver.driver_mother_path = "./driver"
    # Check_Chromedriver.main()

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
    options.add_argument("lang=ko_KR")
    options.add_argument("headless")
    options.add_argument('--start-maximized')


    driver = webdriver.Chrome(DRIVER_FILEPATH,chrome_options=options)

    driver.get(URL)
    scroll=10
    for i in range(1,50):
        scroll += 1*100
        MAX_DOWN ='document.body.scrollHeight'
        driver.execute_script(f"window.scrollTo(0,{scroll});")
        sleep(1)

    soup = BeautifulSoup(driver.page_source,'html.parser')
    review_tab = soup.findAll('div',class_='css-bawlbm')
    # 시간 부족으로 영화 제목이 동일한 경우는 첫번째 영화로처리 
    for table in review_tab:
        if(table is not None):
            review_ = table.find('div',class_='css-1g78l7j')
            if(review_ is not None):
                # print(review_)
                review_span = review_.find('span')
                if(review_span is not None):
                    # print(review_span)
                        reviews.append(review_span.text)

    return reviews  
def use_model(movie_name):
    """
    output: 긍정 단어, 부정 단어 type: list

    영화 리뷰를 모델에 넣어서 결과를 통해서 
    긍정으로 분류되면 형태소를 pos에,
    부정으로 분류되면 형태소를 nag에 넣어준다. 
    """
    
    pos_ = []
    nag_ = []
    
    # reviews = review_load(movie_name)
    reviews=load_reviews(movie_name)
    rev = load_reviews(movie_name) 
    
    tfv = TfidfVectorizer(tokenizer=twitter.morphs, ngram_range=(1,2), min_df=3, max_df = 0.9)
    tfv.fit_transform(X_train)
    X_test=tfv.transform(reviews)



    # X_test = tfv.transform(reviews)
    y_pred = model.predict(X_test)
    # 지금은 리뷰로 나누어 져있는데 단어,형태소 단위로 나누어 주어야된다.
    for value in zip(rev,y_pred):
        if(value[1]==0):
            nag_.append(value[0])
        elif(value[1]==1):
            pos_.append(value[0])            
        else:
            pass

        
    print(pos_)
    print(nag_)
    # 긍정리뷰 부정리뷰 나누어서 저장후 글자 count
    word_nag =[]
    word_pos =[]
    
    sen_tag_nag = []
    sen_tag_pos = []
    for word in nag_:
        sen_tag_nag.append(twitter.pos(word))
    for word in pos_:
        sen_tag_pos.append(twitter.pos(word))
    
    for line in sen_tag_nag:
        for word,tag in line:
            if(tag in ['Noun','Adjective']):
                word_nag.append(word)
    for line in sen_tag_pos:                
        for word,tag in line:
            if(tag in ['Noun','Adjective']):
                word_pos.append(word)

    
    word_nag = Counter(word_nag)
    word_pos = Counter(word_pos)
    
    # word cloud 에  띄울 단어 수 (df.head(20))
    nag = word_nag.most_common(20)
    pos = word_pos.most_common(20)
    
    return pos,nag

def word_clouding(movie_name):
    """
    output: filepath

    pos,nag를 이용해서 word cloud 를 만들어준다. 
    그리고 wordcloud를 저장해주고 파일 path를 return 해준다.
    """
    POS_FILE=f"wordcloud/{movie_name}_pos.png"
    NAG_FILE=f"wordcloud/{movie_name}_nag.png"
    # print(POS_FILEPATH)
    # print(NAG_FILEPATH)    
    pos,nag = use_model(movie_name)

    # wc = WordCloud(font_path='/Font/GodoM.otf',
    #               background_color ="black",
    #               max_font_size = 60)
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=0, font_path='/Library/Fonts/AppleGothic.ttf')
    print(dict(pos))
    print(dict(nag))
    cloud_pos = wc.generate_from_frequencies(dict(pos))
    cloud_nag = wc.generate_from_frequencies(dict(nag))
    
    cloud_pos.to_file(POS_FILEPATH)
    cloud_nag.to_file(NAG_FILEPATH)
    
    return POS_FILE,NAG_FILE 


