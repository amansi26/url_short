import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for
import uuid
import os.path

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

# Use secret key to have a secure session 
app.config['SECRET_KEY'] = uuid.uuid4().hex

# Use hash to encode the secret key
hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

@app.route('/', methods=('GET', 'POST'))
def index():
    conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))
        
        # short_url.txt contains the url and short url
        # Check if short_url.txt exist or not
        # If it exists check for the url present, if present return short_url
        # else create a new short url and update table and short_url.txt
        if os.path.isfile('short_url.txt'):
            with open('short_url.txt') as f:
                datafile = f.readlines()

            for line in datafile:
               if url in line:
                   short_url = line.split(' ')[1]
            
                   return render_template('index.html', short_url=short_url)

        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)',
                                        (url,))
        conn.commit()
        conn.close()

        # Encode the id using hashids and create short url
        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        with open('short_url.txt', 'w') as w:
            w.write(url + ' ' + short_url)

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<id>')
def url_redirect(id):
    conn = get_db_connection()
    # Decodes the hashed id and get the original id
    original_id = hashids.decode(id)
    # this is to read the table and redirect the short_url to original url
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls'
                                            ' WHERE id = (?)', (original_id,)
                                                                        ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                             (clicks+1, original_id))

        conn.commit()
        conn.close()
        return redirect('https://%s' % original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))
