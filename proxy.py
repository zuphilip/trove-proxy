from flask import Flask, abort
from urllib2 import urlopen, Request, HTTPError, URLError
import time

app = Flask(__name__)


def get_url(url):
        response = None
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        except URLError as e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        return response


def ping_pdf(ping_url):
    ready = False
    print ping_url
    req = Request(ping_url)
    try:
        urlopen(req)
    except HTTPError as e:
        if e.code == 423:
            ready = False
            print 'LOCKED'
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
                time.sleep(0.5)
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


if __name__ == "__main__":
    app.run(debug=True)
