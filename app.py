from flask import Flask, request, render_template_string
import requests

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
<h1>🛡️ SecScan v2</h1>
<form><input name="url" placeholder="example.com" size="40"><button>Scan</button></form>
{% if res %}
  <h2>{{ res.url }}: {{ res.score }}/{{ res.total }}</h2>
  <ul>{% for h, ok in res.results %}
    <li>{{ '✅' if ok else '❌' }} {{ h }}: {{ CHECKS[h] }}</li>
  {% endfor %}</ul>
{% endif %}
{% if err %}<p>⚠️ {{ err }}</p>{% endif %}
"""

def scan(url):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    r = requests.get(url, timeout=5)
    results = [(h, h in r.headers) for h in CHECKS]
    return {"url": url, "score": sum(ok for _, ok in results),
            "total": len(CHECKS), "results": results}

@app.route("/")
def home():
    url, res, err = request.args.get("url"), None, None
    if url:
        try:
            res = scan(url)
        except requests.RequestException:
            err = "Could not reach that site"
    return render_template_string(PAGE, res=res, err=err, CHECKS=CHECKS)

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

