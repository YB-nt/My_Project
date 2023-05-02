from flask import Blueprint, render_template

sub_bp = Blueprint('main',__name__)

@sub_bp.route('/sub',methods=['GET'])
def select_movie():

    return render_template('sub.html'), 200