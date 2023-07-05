import requests
from flask import Flask, jsonify, render_template, request, send_from_directory
from ctext import *
from openlibrary import *

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
    # Search for books in English
    # french_books = openlibrary_api.get(subject='fiction', language='fre')
    # Loop through the results and print book titles
    # print(french_books)
    # chinses books
    #titles = gettexttitles()['books'][:3]
    #print(titles)
    return render_template('index.html')

# chinese reader page
@app.route('/readchinese')
def readchinese():
    
    urn = request.args.get('urn')
    print(urn)
    
    if urn:
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
                return render_template('chapterschinese.html', title=title, chapters=chapters)
            # no subsections -> render fulltext
            if 'fulltext' in data:
                fulltext = data['fulltext']
                #format for HTML
                body = "@".join(fulltext)
                return render_template('read.html', title=title, body=body)
        else:
            return 'Error: Failed to retrieve text from the API'
    else:
        titles = gettexttitles()['books'][:3]
        return render_template('chinese.html', title='Select a Book', books=titles)
    
# latin languages reader page
@app.route('/read')
def read():
    
    lang = request.args.get('lang')
    print(lang)
    
    if lang == 'french':
        url = 'https://openlibrary.org/search.json?q=q=language%3Afre&has_fulltext=true&limit=10'
        response = requests.get(url)
        
        if response.status_code == 200:
            #Parse the JSON response
            data = response.json()            
            # Book is restricted    
            if 'error' in data:
                return render_template('error.html', title="Restricted Book", message='This book is restricted and cannot be read for free.')
            #check if there is a subsection
            if 'docs' in data:
                # Extract and print the titles of the books
                books = {}
                for doc in data['docs']:
                    title = doc['title']
                    key = doc['key']
                    books[key] = title
                return render_template('chapters.html', title='Select a Book', chapters=books)
            # no subsections -> render fulltext
            #if 'fulltext' in data:
            #    fulltext = data['fulltext']
            #    #format for HTML
            #    body = "@".join(fulltext)
            #    return render_template('read.html', title=title, body=body)
        else:
            return 'Error: Failed to retrieve text from the API'
    
    return render_template('read.html', title='work in progress...')

@app.route('/readtext')
def readtext():
    key = request.args.get('key')
    url = 'https://openlibrary.org' + key + '.json'
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()    
        description = data['description']
        title = data['title']
        
        # Check if description has children
        if 'value' in description:
            body = description['value']
        else:
            body = description
            
        apiKey = '4670812e-ea92-88b1-8b82-0812f3f4009b:fx'
        apiUrl = 'https://api-free.deepl.com/v2/translate?auth_key=' + apiKey + '&text=' + body + '&source_lang=en&target_lang=fr'

        response_temp = requests.get(apiUrl)
        data_temp = response_temp.json()

        if 'translations' in data_temp:
            translations = data_temp['translations']
            if translations:
                translated_text = translations[0]['text']
                body = translated_text
            else:
                print("No translations available.")
        else:
            print("Error occurred while translating the text.")
        
        return render_template('readlatin.html', title=title, body=body)
        
    
    
# entry point
if __name__ == '__main__':
    app.run(debug=True)
