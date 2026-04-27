import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

df = pd.read_csv("Students.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://example.org/")

g = Graph()
g.bind("ex", EX)

# Classes
g.add((EX.Person, RDF.type, EX.Class))
g.add((EX.Student, RDF.type, EX.Class))
g.add((EX.TeachingAssistant, RDF.type, EX.Class))

for _, row in df.iterrows():

    person_uri = URIRef(EX["person/" + quote(str(row["Student id"]))])

    name = str(row["Student name"])
    programme = str(row["Programme"])
    year = Literal(int(row["Year"]), datatype=XSD.integer)
    graduated = Literal(str(row["Graduated"]).lower() == "true", datatype=XSD.boolean)

    # Determine type (Student vs TA)
    if str(row["Student name"]).startswith("TA"):
        g.add((person_uri, RDF.type, EX.TeachingAssistant))
    else:
        g.add((person_uri, RDF.type, EX.Student))

    g.add((person_uri, RDF.type, EX.Person))

    g.add((person_uri, EX.hasName, Literal(name)))
    g.add((person_uri, EX.hasProgramme, Literal(programme)))
    g.add((person_uri, EX.hasYear, year))
    g.add((person_uri, EX.graduated, graduated))

g.serialize("students.ttl", format="turtle", encoding="utf-8")