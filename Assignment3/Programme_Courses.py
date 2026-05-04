import pandas as pd
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from urllib.parse import quote

# Load CSV
df = pd.read_csv("Programme_Courses.csv")
df.columns = df.columns.str.strip()

EX = Namespace("http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#")

g = Graph()
g.bind("", EX)

for _, row in df.iterrows():

    program_code = str(row["Programme code"])
    course_code = str(row["Course"])
    year = str(row["Academic Year"])

    # -----------------------
    # ProgramCourse instance
    # -----------------------
    pc_id = f"{program_code}_{course_code}_{year}"
    pc_uri = URIRef(EX["programCourse/" + quote(pc_id)])

    g.add((pc_uri, RDF.type, EX.ProgramCourse))

    # -----------------------
    # Data properties
    # -----------------------
    g.add((pc_uri, EX.studyYear, Literal(int(row["Study Year"]), datatype=XSD.int)))

    # Extract start year from "2013-2014"
    start_year = int(year.split("-")[0])
    g.add((pc_uri, EX.academicYear, Literal(start_year, datatype=XSD.int)))

    g.add((pc_uri, EX.courseType, Literal(row["Course Type"])))

    # -----------------------
    # Program
    # -----------------------
    program_uri = URIRef(EX["program/" + quote(program_code)])
    g.add((program_uri, RDF.type, EX.Program))
    g.add((program_uri, EX.programCode, Literal(program_code)))

    g.add((program_uri, EX.ProgramInProgramCourse, pc_uri))

    # -----------------------
    # Course
    # -----------------------
    course_uri = URIRef(EX["course/" + quote(course_code)])
    g.add((course_uri, RDF.type, EX.Course))
    g.add((course_uri, EX.courseCode, Literal(course_code)))

    g.add((course_uri, EX.CourseInProgramCourse, pc_uri))

# Save RDF
g.serialize("Programme_Courses.ttl", format="turtle", encoding="utf-8")

print("RDF created: Programme_Courses.ttl")