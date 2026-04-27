import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Senior_Teachers.csv")
df.columns = df.columns.str.strip()

# Namespace (your ontology)
EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    teacher_id = str(row["Teacher id"])

    # Create URI for Teacher
    teacher_uri = URIRef(EX["teacher/" + quote(teacher_id)])

    # Type
    g.add((teacher_uri, RDF.type, EX.Teacher))

    # Data properties
    g.add((teacher_uri, EX.name, Literal(row["Teacher name"])))
    g.add((teacher_uri, EX.personalID, Literal(teacher_id)))

    g.add((teacher_uri, EX.departmentName, Literal(row["Department name"])))
    g.add((teacher_uri, EX.divisionName, Literal(row["Division name"])))

# Save RDF
g.serialize("senior_teachers.ttl", format="turtle", encoding="utf-8")

print("RDF file created: senior_teachers.ttl")