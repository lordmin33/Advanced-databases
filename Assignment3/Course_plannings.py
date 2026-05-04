import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Course_plannings.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    instance_id = str(row["Course"])

    # -----------------------
    # CourseInstance
    # -----------------------
    course_uri = URIRef(EX["courseInstance/" + quote(instance_id)])

    g.add((course_uri, RDF.type, EX.CourseInstance))
    g.add((course_uri, EX.instanceID, Literal(instance_id)))

    # Planned number of students
    g.add((course_uri, EX.planningNumStudents,
           Literal(int(row["Planned number of Students"]), datatype=XSD.int)))

    # Senior hours
    g.add((course_uri, EX.seniorHours,
           Literal(float(row["Senior Hours"]), datatype=XSD.float)))

    # Assistant hours
    g.add((course_uri, EX.assistantHours,
           Literal(float(row["Assistant Hours"]), datatype=XSD.float)))

# Save RDF
g.serialize("Course_Plannings.ttl", format="turtle", encoding="utf-8")

print("RDF created: Course_Plannings.ttl")