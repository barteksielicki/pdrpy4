from api import app

if __name__ == '__main__':
    app.run(host='localhost', port=1337, workers=2, debug=True)
