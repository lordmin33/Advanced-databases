import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, XSD, URIRef

# =========================================================
# NAMESPACE
# =========================================================
BASE = "http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#"
ns = Namespace(BASE)

g = Graph()
g.bind("", ns)

# =========================================================
# HELPER
# =========================================================
def uri(cls, id):
    return URIRef(BASE + f"{cls}/{id}")


# =========================================================
# 1. STUDENTS
# =========================================================
students = pd.read_csv("Students.csv")

for _, row in students.iterrows():
    s = uri("student", row["Student id"])
    p = uri("program", row["Programme"])

    g.add((s, RDF.type, ns.Student))
    g.add((s, ns.name, Literal(row["Student name"])))
    g.add((s, ns.personalID, Literal(row["Student id"])))
    g.add((s, ns.enrolledYear, Literal(int(row["Year"]))))

    g.add((s, ns.enrolledInProgram, p))


# =========================================================
# 2. TEACHERS (Senior + TA)
# =========================================================
def add_teacher(df, is_senior=False):
    for _, row in df.iterrows():
        t = uri("teacher", row["Teacher id"])
        dept = uri("department", row["Department name"])
        div = uri("division", row["Division name"])

        g.add((t, RDF.type, ns.Teacher))

        if is_senior:
            g.add((t, RDF.type, ns.SeniorTeacher))

        g.add((t, ns.name, Literal(row["Teacher name"])))
        g.add((t, ns.personalID, Literal(row["Teacher id"])))

        # Department & Division as resources
        g.add((dept, RDF.type, ns.Department))
        g.add((dept, ns.departmentName, Literal(row["Department name"])))

        g.add((div, RDF.type, ns.Division))
        g.add((div, ns.divisionName, Literal(row["Division name"])))

        g.add((t, ns.empolyedAt, div))


teachers = pd.read_csv("Senior_Teachers.csv")
tas = pd.read_csv("Teaching_Assistants.csv")

add_teacher(teachers, is_senior=True)
add_teacher(tas, is_senior=False)


# =========================================================
# 3. PROGRAMS
# =========================================================
programs = pd.read_csv("Programmes.csv")

for _, row in programs.iterrows():
    p = uri("program", row["Programme code"])
    d = uri("teacher", row["Director"])

    g.add((p, RDF.type, ns.Program))
    g.add((p, ns.programCode, Literal(row["Programme code"])))
    g.add((p, ns.programName, Literal(row["Programme name"])))
    g.add((p, ns.departmentName, Literal(row["Department name"])))

    # FIXED: directorOf domain = SeniorTeacher → Program
    g.add((d, RDF.type, ns.SeniorTeacher))
    g.add((d, ns.directorOf, p))

# =========================================================
# 4. COURSES
# =========================================================
courses = pd.read_csv("Courses.csv")

for _, row in courses.iterrows():
    c = uri("course", row["Course code"])
    div = uri("division", row["Division"])
    prog = uri("program", row["Owned By"])

    g.add((c, RDF.type, ns.Course))
    g.add((c, ns.courseCode, Literal(row["Course code"])))
    g.add((c, ns.courseName, Literal(row["Course name"])))
    g.add((c, ns.credits, Literal(float(row["Credits"]))))
    g.add((c, ns.level, Literal(row["Level"])))

    g.add((c, ns.ArrangedBy, div))
    g.add((c, ns.ownedBy, prog))

# =========================================================
# PROGRAMME COURSES (Bridge table)
# =========================================================
prog_courses = pd.read_csv("Programme_Courses.csv")

for _, row in prog_courses.iterrows():
    # Create a ProgramCourse instance (bridge between Program and Course)
    pc_id = f"{row['Programme code']}_{row['Course']}_{row['Academic Year']}"
    pc = uri("programCourse", pc_id)
    
    prog = uri("program", row["Programme code"])
    course = uri("course", row["Course"])
    
    g.add((pc, RDF.type, ns.ProgramCourse))
    g.add((pc, ns.studyYear, Literal(float(row["Study Year"]))))
    g.add((pc, ns.academicYear, Literal(row["Academic Year"])))
    g.add((pc, ns.courseType, Literal(row["Course Type"])))
    
    # Link Program to ProgramCourse
    g.add((prog, ns.ProgramInProgramCourse, pc))
    
    # Link Course to ProgramCourse
    g.add((course, ns.CourseInProgramCourse, pc))

# =========================================================
# 5. COURSE INSTANCES
# =========================================================
instances = pd.read_csv("Course_Instances.csv")

for _, row in instances.iterrows():
    i = uri("instance", row["Instance_id"])
    c = uri("course", row["Course code"])
    examiner = uri("teacher", row["Examiner"])

    g.add((i, RDF.type, ns.CourseInstance))
    g.add((i, ns.instanceID, Literal(row["Instance_id"])))
    g.add((i, ns.studyPeriod, Literal(float(row["Study period"]))))
    g.add((i, ns.academicYear, Literal(row["Academic year"])))

    g.add((i, ns.InstanceOf, c))

    # FIX: examiner must be SeniorTeacher
    g.add((examiner, RDF.type, ns.SeniorTeacher))
    g.add((examiner, ns.examinerOf, i))


# =========================================================
# 6. ASSIGNED HOURS
# =========================================================
assigned = pd.read_csv("Assigned_Hours.csv")

for _, row in assigned.iterrows():
    t = uri("teacher", row["Teacher Id"])
    i = uri("instance", row["Course Instance"])

    th = uri("teachingHours", f"{row['Teacher Id']}_{row['Course Instance']}")

    g.add((th, RDF.type, ns.TeachingHours))
    g.add((th, ns.assignedHours, Literal(float(row["Hours"]))))

    g.add((t, ns.TeacherHours, th))
    g.add((th, ns.TeacherCourseHours, i))

# =========================================================
# 9. REPORTED HOURS (ADD THIS!)
# =========================================================
reported = pd.read_csv("Reported_Hours.csv")

for _, row in reported.iterrows():
    t = uri("teacher", row["Teacher Id"])
    i = uri("instance", row["Course code"])  # Note: Course code here is actually Instance_id
    
    # Create a unique URI for this reported hours entry
    th = uri("reportedHours", f"{row['Teacher Id']}_{row['Course code']}")
    
    g.add((th, RDF.type, ns.TeachingHours))
    g.add((th, ns.reportedHours, Literal(float(row["Hours"]))))
    
    # Link teacher to these teaching hours
    g.add((t, ns.TeacherHours, th))
    
    # Link teaching hours to course instance
    g.add((th, ns.TeacherCourseHours, i))

# =========================================================
# 7. COURSE PLANNING
# =========================================================
planning = pd.read_csv("Course_plannings.csv")

for _, row in planning.iterrows():
    i = uri("instance", row["Course"])

    g.add((i, ns.planningNumStudents, Literal(int(row["Planned number of Students"]))))
    g.add((i, ns.seniorHours, Literal(float(row["Senior Hours"]))))
    g.add((i, ns.assistantHours, Literal(float(row["Assistant Hours"]))))


# =========================================================
# 8. COURSE REGISTRATIONS
# =========================================================
regs = pd.read_csv("Registrations.csv")

for _, row in regs.iterrows():
    r = uri("registration", f"{row['Course Instance']}_{row['Student id']}")
    s = uri("student", row["Student id"])
    i = uri("instance", row["Course Instance"])

    g.add((r, RDF.type, ns.CourseRegistration))
    g.add((r, ns.status, Literal(row["Status"])))
    g.add((r, ns.grade, Literal(float(row["Grade"]), datatype=XSD.float)))

    g.add((s, ns.RegisteredStudent, r))
    g.add((r, ns.RegisteredForCourse, i))

# =========================================================
# SAVE RDF
# =========================================================
g.serialize("output.ttl", format="turtle")

print("RDF generation complete: output.ttl")