from app import app
from waitress import serve

if __name__ == '__main__':
    if app.config['MODE'] == 'production':
        serve(app, host='0.0.0.0', port=app.config['PORT'])
    elif app.config['MODE'] == 'development':
        app.run(host='0.0.0.0', port=app.config['PORT'])