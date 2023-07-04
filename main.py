import requests
from flask import Flask, jsonify, render_template, request, send_from_directory
from ctext import *

app = Flask(__name__)
setapikey("your-api-key-goes-here")

# serve manifest.json
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(app.root_path, 'manifest.json')

# serve manifest.json
@app.route('/service-worker.js')
def serve_worker():
    return send_from_directory(app.root_path, 'service-worker.js')

# book selection page
@app.route('/')
def books():
    titles = gettexttitles()['books'][:3]
    print(titles)
    return render_template('index.html', books=titles)

# book reader page
@app.route('/read')
def read():
    
    urn = request.args.get('urn')
    print(urn)
    
    url = "https://api.ctext.org/gettext?urn=" + urn
    print(url)
    
    response = requests.get(url)
    
    if response.status_code == 200:
        #Parse the JSON response
        data = response.json()
        # Book is restricted    
        if 'error' in data:
            return render_template('error.html', title="Restricted Book", message='This book is restricted and cannot be read for free.')
        title = data['title']
        #check if there is a subsection
        if 'subsections' in data:
            chapters = data['subsections']
            return render_template('chapters.html', title=title, chapters=chapters)
        # no subsections -> render fulltext
        if 'fulltext' in data:
            fulltext = data['fulltext']
            #format for HTML
            body = "@".join(fulltext)
            return render_template('read.html', title=title, body=body)
    else:
        return 'Error: Failed to retrieve text from the API'
    
# entry point
if __name__ == '__main__':
    app.run(debug=True)
