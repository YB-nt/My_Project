from flask import Flask,blueprint

def create_app(config=None):
    app = Flask(__name__)
    
    if config is not None:
            app.config.update(config)

    from application.views.main_search import main_bp
    from application.views.sub_search import sub_bp
    from application.views.result import result_bp

    # app.register_blueprint(main_bp)
    # app.register_blueprint(sub_bp, url_prefix='/api')
    # app.regisrer_blueprint(result_bp, url_perfix='/<movie_name>')

    return app


if __name__ =="__main__":
    app = create_app()
    app.run(debug=True)