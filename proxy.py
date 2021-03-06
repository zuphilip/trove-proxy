from flask import Flask, abort, request, Response, render_template
from urllib2 import urlopen, Request, HTTPError, URLError
import time
import urlparse

app = Flask(__name__)


def get_url(url):
        response = None
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            abort(e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        return response


def ping_pdf(ping_url):
    ready = False
    req = Request(ping_url)
    try:
        urlopen(req)
    except HTTPError as e:
        if e.code == 423:
            ready = False
            print('LOCKED')
        else:
            raise
    else:
        ready = True
    return ready


def get_pdf_url(article_id, zoom=3):
    pdf_url = None
    prep_url = 'http://trove.nla.gov.au/newspaper/rendition/nla.news-article{}/level/{}/prep'.format(article_id, zoom)
    response = get_url(prep_url)
    prep_id = response.read()
    if prep_id:
        ping_url = 'http://trove.nla.gov.au/newspaper/rendition/nla.news-article{}.{}.ping?followup={}'.format(article_id, zoom, prep_id)
        tries = 0
        ready = False
        time.sleep(2)  # Give some time to generate pdf
        while ready is False and tries < 2:
            ready = ping_pdf(ping_url)
            if not ready:
                tries += 1
                time.sleep(5)
        if ready:
            pdf_url = 'http://trove.nla.gov.au/newspaper/rendition/nla.news-article{}.{}.pdf?followup={}'.format(article_id, zoom, prep_id)
        else:
            abort(504)
    else:
        abort(404)
    return pdf_url


@app.route("/pdf/<id>")
def pdf(id):
    pdf_url = get_pdf_url(id)
    return pdf_url, 200


@app.route('/api/list/<id>')
def list_proxy(id):
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/list/{}?{}'.format(id, query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/newspaper/<id>')
def newspaper_proxy(id):
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/newspaper/{}?{}'.format(id, query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/work/<id>')
def work_proxy(id):
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/work/{}?{}'.format(id, query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/newspaper/title/<id>')
def title_proxy(id):
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/newspaper/title/{}?{}'.format(id, query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/newspaper/titles')
def titles_proxy():
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/newspaper/titles?{}'.format(query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/contributor/<id>')
def contributor_proxy(id):
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/contributor/{}?{}'.format(id, query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/contributor')
def contributors_proxy():
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/contributor?{}'.format(query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route('/api/result')
def search_proxy():
    parsed_url = urlparse.urlsplit(request.url)
    query = parsed_url.query
    api_url = 'http://api.trove.nla.gov.au/result?{}'.format(query)
    response = get_url(api_url)
    return Response(response.read(), mimetype='application/json')


@app.route("/")
@app.route("/pdf/")
@app.route("/api/")
def default():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
