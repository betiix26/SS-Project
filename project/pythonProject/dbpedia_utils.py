from SPARQLWrapper import SPARQLWrapper, JSON

def get_universities_from_dbpedia(limit=10):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    query = f"""
    SELECT ?university ?name ?abstract WHERE {{
        ?university rdf:type dbo:University .
        ?university dbo:country dbr:Romania .
        # ?university dbo:city dbr:Craiova .
        ?university rdfs:label ?name .
        OPTIONAL {{ ?university dbo:abstract ?abstract . }}
        FILTER (lang(?name) = 'en')
        FILTER (lang(?abstract) = 'en')
    }} LIMIT {limit}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    universities = []
    for result in results["results"]["bindings"]:
        universities.append({
            "uri": result["university"]["value"],
            "name": result["name"]["value"],
            "abstract": result.get("abstract", {}).get("value", "")
        })

    return universities
