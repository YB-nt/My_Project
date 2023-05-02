from flask import Blueprint, render_template
from application.make_cloud.make_cloud import word_clouding


main_bp = Blueprint('main','__name__')

@main_bp.route('/')
def index():
    """
    index 함수에서 '/' 앤드 포인트로 접속했을때 페이지 랜더링 

    """

    return render_template('search.html'), 200

@main_bp.route('/<movie_name>',methods=['GET','POST'])
def print_result(movie_name):
    POS_FILE,NAG_FILE  = word_clouding(movie_name)
    return render_template("result.html",pos_image=POS_FILE,nag_image=NAG_FILE),200


