from flask import Flask, send_file

app = Flask(__name__,static_folder='images', static_url_path='/images/')

@app.route('/')
def main():
    return send_file('table.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False)
