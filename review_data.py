import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sqlite3



#############################################################################################
#############################################################################################
#############################################################################################

def make_movie_name():
#네이버 리뷰에서 영화 제목 가져오기
#리뷰가 대체적으로 짧은 편이여서 해당 리뷰는 선택하지 않고 제목만 추출하였다.
    movie_name_list =[]
    for i in range(1,100):
        NAVER_REVIEW_URL = f'https://movie.naver.com/movie/board/review/list.naver?&page={i}'
        resp = requests.get(NAVER_REVIEW_URL)
        if(resp.status_code==200):
            soup = BeautifulSoup(resp.content,'html.parser')
            div = soup.find("div",{"id":"old_content"})
            # print(div)
            table = div.find("table",class_='list_table_1 list_h48')
            # print(table)
            td = table.find("td",class_="movie")
            for item in td:
                # print(td.find('a').text)
                movie_name_list.append(td.find('a').text)
        else:
            print(resp.status_code)
    movie_name_list = list(set(movie_name_list))
    return movie_name_list
    

def make_movie_info(movie_name_list):
#왓챠피디아 에서 영화 정보가져오기
#영화 제목,영화정보(개봉연도,국가) 불러오기
    search_info =[]
    for movie_name in movie_name_list:
        movie_name = movie_name.replace(' ','%20')
        PEDIA_BASE_URL =f'https://pedia.watcha.com/ko-KR/searches/movies?query={movie_name}'
        resp = requests.get(PEDIA_BASE_URL)
        if(resp.status_code==200):
            soup = BeautifulSoup(resp.content,"html.parser")
            ul = soup.find("ul",class_="css-17i7zjx-VisualUl-StyledResultsUl e1493pgd3")
            if(ul!=None):
                for col_num in (1,len(ul.find("div",class_="css-x62r3q").text)+1):
                    div_name = ul.findAll("div",class_="css-x62r3q")
                    div_info = ul.findAll("div",class_="css-h25two")
                    link_code= ul.findAll("a",class_="css-1aaqvgs-InnerPartOfListWithImage")
                    if(div_name!=None and div_info!=None and link_code!=None):
                        for name,info,link in zip(div_name,div_info,link_code):
                            temp_value = [name.text]
                            linkcode=link.get('href').split('/')
                            info_ = info.text.split(' ・ ') 
                            # breakpoint()
                            year = info_[0]
                            temp_value.append(year)

                            try:
                                country =info_[1]
                            except:
                                print("---Country Error---")
                                print(name.text,info.text)
                                temp_value.append('-')
                            else:
                                temp_value.append(country)
                            # breakpoint()
                            temp_value.append(link_code[-1])
                            search_info.append(temp_value)    
        else:
            print("RESPONSE_CODE:",resp.status_code)
    return search_info

def make_review_info(search_info):
#영화리뷰,영화 평점(별점) 불러오기
    reviews =[]
    for link in search_info:
        link_code = link[-1]
        comment_URL =f'https://pedia.watcha.com/ko-KR/contents/{link_code}/comments'
        resp = requests.get(comment_URL)
        if(resp.status_code==200):
            soup = BeautifulSoup(resp.content,'html.parser')
            review_tab = soup.findAll('div',class_="css-bawlbm")
            for table in review_tab:
                if(table is not None):
                    star_table = table.find('div',class_='css-yqs4xl')
                    if(star_table is not None):
                        star = star_table.find('span')
                    review_table = table.find('div',class_='css-1g78l7j')
                    if(review_table is not None):
                        review = review_table.find('span')
                    if(review!=None and star!=None):
                        reviews.append([review.text,star.text])
        else:
            print(comment_URL)
            print(resp.status_code)

    return reviews


#############################################################################################
#############################################################################################
#############################################################################################



movie_name = make_movie_name()
movie_info = make_movie_info(movie_name)
movie_review = make_review_info(movie_info)


conn = sqlite3.connect("review.db")
cur = conn.cursor()
try:
    cur.execute("DROP TABEL IF EXISTS movie_info;")
    cur.execute("DROP TABLE IF EXISTS movie_review;")
except:
    pass

cur.execute("""
    CREATE TABLE movie_info(
        movie_name VARCHAR(50),
        year INTEGER,
        country TEXT
    );
""")

cur.execute("""
    CREATE TABLE movie_review(
        movie_name VARCHAR(50),
        review TEXT,
        star FLAOT,
        FOREIGN KEY (movie_name) REFERENCES movie_info(movie_name)
    );
""")

#데이터 적재
for info_item,reivew_item in zip(movie_info,movie_review):
    name = info_item[0]
    year = info_item[1]
    country = info_item[2]
    review = review[0]
    star = review[1]
    info_table = [name,year,country]
    review_table = [name,review,star]
    # db 에 넣어주기
    cur.executemany("INSERT INTO movie_info VALUES(?,?);",info_table)
    cur.executemany("INSERT INTO movie_review VALUES(?,?,?);",review_table)

conn.commit()
cur.close()
conn.close()




    

