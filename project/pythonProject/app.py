from flask import Flask, render_template, request
from models import Resource
from dbpedia_utils import get_universities_from_dbpedia
from SPARQLWrapper import SPARQLWrapper, JSON
import json

app = Flask(__name__)

# ---------- RESURSE MANUALE ----------
from rdflib import Graph, Namespace, RDF, URIRef, Literal

EX = Namespace("http://example.org/schema#")

def load_resources_from_rdf(file_path="resources.rdf"):
    g = Graph()
    g.parse(file_path, format="xml")
    resources = []

    for s in g.subjects(RDF.type, EX.Resource):
        title = str(g.value(s, EX.title))
        author = str(g.value(s, EX.author))
        level = str(g.value(s, EX.level))
        rtype = str(g.value(s, EX.type))
        url = str(g.value(s, EX.url))
        framework = str(g.value(s, EX.framework))
        target = str(g.value(s, EX.target))

        resources.append(Resource(title, author, level, rtype, url, {"framework": framework, "target": target}))

    return resources

resources = load_resources_from_rdf("resources.rdf")



# ---------- RUTA PRINCIPALĂ ----------
@app.route("/dashboard")
def index():
    level = request.args.get("level", "")
    rtype = request.args.get("rtype", "")
    filtered = resources
    if level:
        filtered = [r for r in filtered if r.level.lower() == level.lower()]
    if rtype:
        filtered = [r for r in filtered if r.rtype.lower() == rtype.lower()]

    filtered_dicts_js = [{
        "title": r.title,
        "level": r.level,
        "rtype": r.rtype,
        "url": r.url
    } for r in filtered]

    filtered_dicts_jsonld = [r.to_jsonld() for r in filtered]

    universities = get_universities_from_dbpedia(limit=10)

    return render_template(
        "index.html",
        resources=filtered,
        resources_json_str=json.dumps(filtered_dicts_js),
        export_jsonld_str=json.dumps(filtered_dicts_jsonld),
        universities=universities
    )



# ---------- DETALII PENTRU O RESURSĂ ----------
@app.route("/resource/<int:idx>")
def resource_detail(idx):
    if idx < 0 or idx >= len(resources):
        return "Resource not found", 404
    res = resources[idx]
    jsonld = json.dumps(res.to_jsonld(), indent=4)
    return render_template("resource.html", resource=res, jsonld=jsonld)


# ---------- RESURSE DIN DBPEDIA ----------
@app.route("/dbpedia")
def dbpedia_resources():
    universities = get_universities_from_dbpedia(limit=15)

    # convertim în format Resource pentru a le putea transforma în JSON-LD
    dbpedia_resources = [
        Resource(
            u["name"],
            "DBpedia",
            "College",
            "University",
            u["url"] if u["url"] else "N/A",
            {"framework": "Higher Education", "target": u["city"]}
        )
        for u in universities
    ]

    return render_template("dbpedia.html", universities=dbpedia_resources)


# ---------- EXPORT JSON-LD DIN DBPEDIA ----------
@app.route("/dbpedia/jsonld")
def dbpedia_jsonld():
    universities = get_universities_from_dbpedia(limit=15)
    dbpedia_resources = [
        Resource(
            u["name"],
            "DBpedia",
            "College",
            "University",
            u["url"] if u["url"] else "N/A",
            {"framework": "Higher Education", "target": u["city"]}
        )
        for u in universities
    ]
    jsonld = [r.to_jsonld() for r in dbpedia_resources]
    return app.response_class(
        response=json.dumps(jsonld, indent=4),
        mimetype="application/json"
    )
@app.route("/universities")
def universities():
    city = request.args.get("city", "").strip()
    name = request.args.get("name", "").strip()

    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = """
    SELECT DISTINCT ?univ ?univLabel ?abstract ?cityLabel WHERE {
        ?univ a dbo:University ;
              rdfs:label ?univLabel ;
              dbo:country dbr:Romania .
        OPTIONAL { ?univ dbo:abstract ?abstract . FILTER (lang(?abstract) = 'en') }
        OPTIONAL { ?univ dbo:city ?city . ?city rdfs:label ?cityLabel . FILTER (lang(?cityLabel) = 'en') }
        FILTER (lang(?univLabel) = 'en')
    """
    if city:
        query += f'FILTER(CONTAINS(LCASE(?cityLabel), LCASE("{city}"))) '
    if name:
        query += f'FILTER(CONTAINS(LCASE(?univLabel), LCASE("{name}"))) '
    query += "} LIMIT 50"

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    universities = []
    for r in results["results"]["bindings"]:
        universities.append({
            "name": r["univLabel"]["value"],
            "uri": r["univ"]["value"],
            "abstract": r.get("abstract", {}).get("value", "No description available"),
            "city": r.get("cityLabel", {}).get("value", "Unknown")
        })

    # JSON-LD export
    jsonld = [{
        "@context": "https://schema.org",
        "@type": "CollegeOrUniversity",
        "name": u["name"],
        "url": u["uri"],
        "description": u["abstract"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": u["city"]
        }
    } for u in universities]

    return render_template(
        "universities.html",
        universities=universities,
        jsonld_str=json.dumps(jsonld)
    )
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/manual")
def manual_resources():
    level = request.args.get("level", "")
    rtype = request.args.get("rtype", "")
    filtered = resources
    if level:
        filtered = [r for r in filtered if r.level.lower() == level.lower()]
    if rtype:
        filtered = [r for r in filtered if r.rtype.lower() == rtype.lower()]

    filtered_dicts_js = [{
        "title": r.title, "level": r.level, "rtype": r.rtype, "url": r.url
    } for r in filtered]

    filtered_dicts_jsonld = [r.to_jsonld() for r in filtered]

    return render_template(
        "manual.html",
        resources=filtered,
        resources_json_str=json.dumps(filtered_dicts_js),
        export_jsonld_str=json.dumps(filtered_dicts_jsonld)
    )

if __name__ == "__main__":
    app.run(debug=True)
