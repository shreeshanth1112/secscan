import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

CHECKS = {
    "Strict-Transport-Security": "Forces HTTPS",
    "Content-Security-Policy": "Blocks XSS / injected scripts",
    "X-Frame-Options": "Stops clickjacking",
    "X-Content-Type-Options": "Stops MIME sniffing",
    "Referrer-Policy": "Limits referrer leaks",
    "Permissions-Policy": "Restricts browser features",
}

PAGE = """
<h1>🛡️ SecScan v3</h1>
<form><input name="url" placeholder="example.com" size="40"><button>Scan</button></form>
{% if res %}
  <h2>{{ res.url }}: {{ res.score }}/{{ res.total }}</h2>
  <ul>{% for h, ok in res.results %}
    <li>{{ '✅' if ok else '❌' }} {{ h }}: {{ CHECKS[h] }}</li>
  {% endfor %}</ul>
{% endif %}
{% if err %}<p>⚠️ {{ err }}</p>{% endif %}
"""

def is_safe(url):
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        return False
    try:
        port = p.port
    except ValueError:
        return False
    if port not in (None, 80, 443):
        return False
    try:
        infos = socket.getaddrinfo(p.hostname, None)
    except socket.gaierror:
        return False
    return all(ipaddress.ip_address(i[4][0].split("%")[0]).is_global
               for i in infos)

def fetch(url):
    for _ in range(4):
        if not is_safe(url):
            raise ValueError("Blocked: only public http(s) sites on ports 80/443 are allowed")
        with requests.get(url, timeout=5, allow_redirects=False, stream=True) as r:
            if r.is_redirect and r.headers.get("Location"):
                url = urljoin(url, r.headers["Location"])
                continue
            return r.headers
    raise ValueError("Too many redirects")

def scan(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    headers = fetch(url)
    results = [(h, h in headers) for h in CHECKS]
    return {"url": url, "score": sum(ok for _, ok in results),
            "total": len(CHECKS), "results": results}

@app.route("/")
def home():
    url, res, err = request.args.get("url"), None, None
    if url:
        try:
            res = scan(url)
        except ValueError as e:
            err = str(e)
        except requests.RequestException:
            err = "Could not reach that site"
    return render_template_string(PAGE, res=res, err=err, CHECKS=CHECKS)

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
