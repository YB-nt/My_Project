from Check_Chromedriver import Check_Chromedriver
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from time import sleep
from typing import Text
from bs4 import BeautifulSoup
import pickle
from collections import Counter
from konlpy.tag import Twitter,Okt
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from wordcloud import WordCloud





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

def load_reviews(movie_name):
    reviews=[]


    link = data_load(movie_name)
    URL =f"https://pedia.watcha.com/ko-KR/contents/{link}/comments"
    
    Check_Chromedriver.driver_mother_path = "./driver"
    Check_Chromedriver.main()

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
    options.add_argument("lang=ko_KR")
    # options.add_argument("headless")
    options.add_argument('--start-maximized')


    driver = webdriver.Chrome('./driver/chromedriver',chrome_options=options)
scroll
    driver.get(URL)
    scroll=10
    for i in range(1,100):
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
if __name__=='__main__':
   review = load_reviews('인셉션')

   print(review)