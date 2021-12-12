from typing import Text
from flask import Blueprint,render_template
from bs4 import BeautifulSoup
import requests
import pickle
from collections import Counter
from konlpy.tag import Twitter
from wordcloud import WordCloud



def data_load(movie_name):
    """
    input : 영화제목  type: string
    output : 영화리뷰 type: list

    영화 제목을 입력하면 왓챠피디아에서 해당 리뷰를 크롤링해온다. 
    학습데이터를 모을떄도 사용했던 함수와 거의 유사하다.
    """
    BASE_URL=f"https://pedia.watcha.com/ko-KR/searches/movies?query={movie_name}"
    reviews=[]
    resp = requests.get(BASE_URL)
    if(resp.status_code==200):
        soup = BeautifulSoup(resp.content,'html.parser')
        a_tag = soup.find('a',class_='css-1aaqvgs-InnerPartOfListWithImage')
        if(a_tag!=None):
            link_text = a_tag.get('href').split('/')
        link = link_text[-1]
    else:
        print(resp.status_code)
    BASE_URL2 = f"https://pedia.watcha.com/ko-KR/contents/{link}/comments"
    resp2 = requests.get(BASE_URL2)
    if(resp2==200):
        soup = BeautifulSoup(resp2.content,"html.parser")
        # 시간 부족으로 영화 제목이 동일한 경우는 첫번째 영화로처리 
        review_ = soup.findAll('div',class_='css-1g78l7j')
        for review in review_:
            reviews.append(review)   
        return reviews
    else:
        print(resp2.status_code)

def use_model(movie_name):
    """
    output: 긍정 단어, 부정 단어 type: list

    영화 리뷰를 모델에 넣어서 결과를 통해서 
    긍정으로 분류되면 형태소를 pos에,
    부정으로 분류되면 형태소를 nag에 넣어준다. 
    """
    
    pos_ = []
    nag_ = []
    reviews,movie_name = data_load(movie_name)

    model = None
    with open('model/model.pkl','rb') as pickle_file:
        model = pickle.load(pickle_file)

    for review in reviews:
        X_test = review
        y_pred = model.predict(X_test)
        # 지금은 리뷰로 나누어 져있는데 단어,형태소 단위로 나누어 주어야된다.
        for value in zip(X_test,y_pred):
            if(value[1]==0):
                nag_.append(value[0])
            elif(value[1]==1):
                pos_.append(value[0])            
            else:
                pass
        # 긍정리뷰 부정리뷰 나누어서 저장후 글자 count
    word_nag =[]
    word_pos =[]
    twitter = Twitter()

    sen_tag_nag = []
    sen_tag_pos = []
    sen_tag_nag = twitter.pos(nag_)
    sen_tag_pos = twitter.pos(pos_)

    for word,tag in sen_tag_nag:
        if(tag in ['Noun','Adjective']):
            word_nag.append(word)
    for word,tag in sen_tag_pos:
        if(tag in ['Noun','Adjective']):
            word_pos.append(word)


    word_nag = Counter(nag_)
    word_pos = Counter(pos_)
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
    
    pos,nag = use_model(movie_name)

    wc= WordCloud(font_path='/Font/GodoM.otf',
                  background_color ="black",
                  max_font_size = 60)

    cloud_pos = wc.generate_from_frequencies(dict(pos))
    cloud_nag = wc.generate_from_frequencies(dict(nag))
    cloud_pos.to_file(POS_FILE)
    cloud_nag.to_file(NAG_FILE)

    return POS_FILE,NAG_FILE 

result_bp = Blueprint('main',__name__)


@result_bp.route('/<movie_name>',methods=['GET'])
def print_result(movie_name):
    POS_FILE,NAG_FILE  = word_clouding(movie_name)
    return render_template("result.html",pos_image=POS_FILE,nag_image=NAG_FILE),200