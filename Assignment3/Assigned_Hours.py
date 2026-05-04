import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Assigned_Hours.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for i, row in df.iterrows():

    teacher_id = str(row["Teacher Id"])
    instance_id = str(row["Course Instance"])

    # -----------------------
    # Teacher
    # -----------------------
    teacher_uri = URIRef(EX["teacher/" + quote(teacher_id)])
    g.add((teacher_uri, RDF.type, EX.Teacher))

    # -----------------------
    # CourseInstance
    # -----------------------
    course_uri = URIRef(EX["courseInstance/" + quote(instance_id)])
    g.add((course_uri, RDF.type, EX.CourseInstance))

    g.add((course_uri, EX.instanceID, Literal(instance_id)))
    g.add((course_uri, EX.studyPeriod, Literal(int(row["Study Period"]), datatype=XSD.int)))
    g.add((course_uri, EX.academicYear, Literal(row["Academic Year"])))

    # -----------------------
    # TeachingHours (unique per row)
    # -----------------------
    th_uri = URIRef(EX["teachingHours/" + str(i)])

    g.add((th_uri, RDF.type, EX.TeachingHours))
    g.add((th_uri, EX.assignedHours, Literal(float(row["Hours"]), datatype=XSD.float)))

    # -----------------------
    # Links (VERY IMPORTANT)
    # -----------------------

    # Teacher → TeachingHours
    g.add((teacher_uri, EX.TeacherHours, th_uri))

    # TeachingHours → CourseInstance
    g.add((th_uri, EX.TeacherCourseHours, course_uri))


# Save RDF
g.serialize("Assigned_Hours.ttl", format="turtle", encoding="utf-8")

print("RDF created: Assigned_Hours.ttl")