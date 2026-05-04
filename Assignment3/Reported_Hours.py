import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

df = pd.read_csv("Reported_Hours.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    course_instance = str(row["Course code"])
    teacher_id = str(row["Teacher Id"])
    hours = float(row["Hours"])

    # -----------------------
    # TeachingHours instance
    # -----------------------
    th_id = f"{teacher_id}_{course_instance}"
    th_uri = URIRef(EX["teachingHours/" + quote(th_id)])

    g.add((th_uri, RDF.type, EX.TeachingHours))
    g.add((th_uri, EX.reportedHours, Literal(hours, datatype=XSD.float)))

    # -----------------------
    # Teacher
    # -----------------------
    teacher_uri = URIRef(EX["teacher/" + quote(teacher_id)])

    g.add((teacher_uri, RDF.type, EX.Teacher))
    g.add((teacher_uri, EX.TeacherHours, th_uri))

    # -----------------------
    # CourseInstance
    # -----------------------
    ci_uri = URIRef(EX["courseInstance/" + quote(course_instance)])

    g.add((ci_uri, RDF.type, EX.CourseInstance))
    g.add((th_uri, EX.TeacherCourseHours, ci_uri))

# Save RDF
g.serialize("Reported_Hours.ttl", format="turtle", encoding="utf-8")

print("RDF created: Reported_Hours.ttl")