import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Courses.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    # -----------------------
    # Course
    # -----------------------
    course_code = str(row["Course code"])
    course_uri = URIRef(EX["course/" + quote(course_code)])

    g.add((course_uri, RDF.type, EX.Course))

    g.add((course_uri, EX.courseCode, Literal(course_code)))
    g.add((course_uri, EX.courseName, Literal(row["Course name"])))
    g.add((course_uri, EX.credits, Literal(row["Credits"], datatype=XSD.float)))
    g.add((course_uri, EX.level, Literal(row["Level"])))

    # -----------------------
    # Program (Owned By)
    # -----------------------
    program_code = str(row["Owned By"])
    program_uri = URIRef(EX["program/" + quote(program_code)])

    g.add((program_uri, RDF.type, EX.Program))
    g.add((program_uri, EX.programCode, Literal(program_code)))

    g.add((course_uri, EX.ownedBy, program_uri))

    # -----------------------
    # Division
    # -----------------------
    division_name = str(row["Division"])
    division_uri = URIRef(EX["division/" + quote(division_name)])

    g.add((division_uri, RDF.type, EX.Division))
    g.add((division_uri, EX.divisionName, Literal(division_name)))

    g.add((course_uri, EX.ArrangedBy, division_uri))

    # -----------------------
    # Department (optional but correct modeling)
    # -----------------------
    dept_name = str(row["Department"])
    dept_uri = URIRef(EX["department/" + quote(dept_name)])

    g.add((dept_uri, RDF.type, EX.Department))
    g.add((dept_uri, EX.departmentName, Literal(dept_name)))

# Save RDF
g.serialize("Courses.ttl", format="turtle", encoding="utf-8")

print("RDF created: Courses.ttl")