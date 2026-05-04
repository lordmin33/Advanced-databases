import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

df = pd.read_csv("Registrations.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    course_instance = str(row["Course Instance"])
    student_id = str(row["Student id"])
    status = str(row["Status"])
    grade = float(row["Grade"])

    # -----------------------
    # CourseRegistration instance
    # -----------------------
    reg_id = f"{course_instance}_{student_id}"
    reg_uri = URIRef(EX["registration/" + quote(reg_id)])

    g.add((reg_uri, RDF.type, EX.CourseRegistration))

    # Datatype properties
    g.add((reg_uri, EX.status, Literal(status)))
    g.add((reg_uri, EX.grade, Literal(grade, datatype=XSD.float)))

    # -----------------------
    # Student
    # -----------------------
    student_uri = URIRef(EX["student/" + quote(student_id)])

    g.add((student_uri, RDF.type, EX.Student))

    g.add((student_uri, EX.RegisteredStudent, reg_uri))

    # -----------------------
    # CourseInstance
    # -----------------------
    ci_uri = URIRef(EX["courseInstance/" + quote(course_instance)])

    g.add((ci_uri, RDF.type, EX.CourseInstance))

    g.add((reg_uri, EX.RegisteredForCourse, ci_uri))

# Save RDF
g.serialize("Registrations.ttl", format="turtle", encoding="utf-8")

print("RDF created: Registrations.ttl")