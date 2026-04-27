import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

df = pd.read_csv("Students.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    student_id = str(row["Student id"])

    # -----------------------
    # 1. Student individual
    # -----------------------
    student_uri = URIRef(EX["student/" + quote(student_id)])

    g.add((student_uri, RDF.type, EX.Student))
    g.add((student_uri, EX.name, Literal(row["Student name"])))
    g.add((student_uri, EX.personalID, Literal(student_id)))

    # -----------------------
    # 2. Enrollment individual
    # -----------------------
    enrollment_uri = URIRef(EX["enrollment/" + quote(student_id)])

    g.add((enrollment_uri, RDF.type, EX.Enrollment))

    # Link Student → Enrollment
    g.add((student_uri, EX.enrolledStudent, enrollment_uri))

    # Program
    program_uri = URIRef(EX["program/" + str(row["Programme"])])

    g.add((enrollment_uri, EX.enrolledInProgram, program_uri))

    # Year
    g.add((enrollment_uri, EX.enrolledYear, Literal(int(row["Year"]), datatype=XSD.int)))

    # Graduated
    g.add((enrollment_uri, EX.graduated, Literal(bool(row["Graduated"]))))

g.serialize("students.owl.ttl", format="turtle", encoding="utf-8")