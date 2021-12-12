from flask import Flask
import os

MODEL_FILEPATH = os.path.join(os.getcwd(), __name__, 'model','model.pkl')
def create_app(config=None):
    app = Flask(__name__)
    
    if config is not None:
            app.config.update(config)

    from application.views.main_search import main_bp
    
    app.register_blueprint(main_bp)
    

    return app


if __name__ =="__main__":
    app = create_app()
    app.run(debug=True)