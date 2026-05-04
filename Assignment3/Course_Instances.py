import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Course_Instances.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    teacher_id = str(row["Examiner"])
    instance_id = str(row["Instance_id"])

    # -----------------------
    # Teacher (Examiner)
    # -----------------------
    teacher_uri = URIRef(EX["teacher/" + quote(teacher_id)])

    # Use SeniorTeacher (important!)
    g.add((teacher_uri, RDF.type, EX.SeniorTeacher))

    # -----------------------
    # CourseInstance
    # -----------------------
    course_uri = URIRef(EX["courseInstance/" + quote(instance_id)])

    g.add((course_uri, RDF.type, EX.CourseInstance))
    g.add((course_uri, EX.instanceID, Literal(instance_id)))

    g.add((course_uri, EX.studyPeriod,
           Literal(int(float(row["Study period"])), datatype=XSD.int)))

    g.add((course_uri, EX.academicYear,
           Literal(row["Academic year"])))

    # -----------------------
    # Link: examinerOf
    # -----------------------
    g.add((teacher_uri, EX.examinerOf, course_uri))


# Save RDF
g.serialize("Course_Instances.ttl", format="turtle", encoding="utf-8")

print("RDF created: Course_Instances.ttl")