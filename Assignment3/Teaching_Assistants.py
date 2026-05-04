import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Teaching_Assistants.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    teacher_id = str(row["Teacher id"])

    # -----------------------
    # TA as Teacher
    # -----------------------
    teacher_uri = URIRef(EX["teacher/" + quote(teacher_id)])

    g.add((teacher_uri, RDF.type, EX.Teacher))

    # Data properties
    g.add((teacher_uri, EX.name, Literal(row["Teacher name"])))
    g.add((teacher_uri, EX.personalID, Literal(teacher_id)))

    g.add((teacher_uri, EX.departmentName, Literal(row["Department name"])))
    g.add((teacher_uri, EX.divisionName, Literal(row["Division name"])))

# Save RDF
g.serialize("Teaching_Assistants.ttl", format="turtle", encoding="utf-8")

print("RDF created: Teaching_Assistants.ttl")