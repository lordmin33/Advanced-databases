import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF
from urllib.parse import quote

df = pd.read_csv("Programmes.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    program_code = str(row["Programme code"])
    program_name = str(row["Programme name"])
    dept_name = str(row["Department name"])
    director_id = str(row["Director"])

    # -----------------------
    # Program
    # -----------------------
    program_uri = URIRef(EX["program/" + quote(program_code)])

    g.add((program_uri, RDF.type, EX.Program))
    g.add((program_uri, EX.programCode, Literal(program_code)))
    g.add((program_uri, EX.programName, Literal(program_name)))

    # -----------------------
    # Department
    # -----------------------
    dept_uri = URIRef(EX["department/" + quote(dept_name)])

    g.add((dept_uri, RDF.type, EX.Department))
    g.add((dept_uri, EX.departmentName, Literal(dept_name)))

    g.add((program_uri, EX.givenBy, dept_uri))

    # -----------------------
    # Director (SeniorTeacher)
    # -----------------------
    teacher_uri = URIRef(EX["teacher/" + quote(director_id)])

    g.add((teacher_uri, RDF.type, EX.SeniorTeacher))
    g.add((teacher_uri, EX.personalID, Literal(director_id)))

    g.add((teacher_uri, EX.directorOf, program_uri))

# Save RDF
g.serialize("Programmes.ttl", format="turtle", encoding="utf-8")

print("RDF created: Programmes.ttl")