import csv
import os
from collections import defaultdict

# Prefixes
PREFIXES = """@prefix : <http://www.semanticweb.org/kemp/ontologies/2019/3/untitled-ontology-1#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix res: <http://www.semanticweb.org/kemp/resource/> .

"""

RES = "http://www.semanticweb.org/kemp/resource/"

def uri(cls, id_val):
    """Create a resource URI."""
    return f"res:{cls}/{id_val}"

def esc(s):
    """Escape a string for Turtle."""
    if s is None:
        return ""
    return s.replace('\\', '\\\\').replace('"', '\\"')

def parse_academic_year(ay_str):
    """Convert '2013-2014' to start year int. Handle both formats."""
    if not ay_str or not ay_str.strip():
        return None
    ay_str = ay_str.strip()
    if '-' in ay_str:
        return ay_str.split('-')[0].strip()
    try:
        return str(int(float(ay_str)))
    except:
        return ay_str

def safe_int(val):
    """Convert to int if possible, else None."""
    if not val or not val.strip():
        return None
    try:
        return int(float(val.strip()))
    except (ValueError, TypeError):
        return None

def safe_float(val):
    """Convert to float if possible, else None."""
    if not val or not val.strip():
        return None
    try:
        return float(val.strip())
    except (ValueError, TypeError):
        return None

def safe_bool(val):
    """Convert to boolean string if possible, else None."""
    if not val or not val.strip():
        return None
    v = val.strip().lower()
    if v in ('true', '1', 'yes'):
        return 'true'
    elif v in ('false', '0', 'no'):
        return 'false'
    return None

# Store all generated triples keyed by subject
triples = defaultdict(list)
# Track teachers, senior teachers, TAs, directors, examiners
teachers = set()
senior_teachers = set()
ta_teachers = set()
directors = {}       # teacher_id -> [programme_codes]
examiners = {}       # teacher_id -> [instance_ids]
teaching_hours_map = {}  # (teacher_id, instance_id) -> (assigned, reported)

# --- Process CSVs ---

def process_students(filepath):
    """Students.csv -> :Student + :Enrollment"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row['Student id'].strip()
            name = row['Student name'].strip()
            prog = row['Programme'].strip()
            year = row['Year'].strip()
            graduated = row['Graduated'].strip()

            # Student
            subj = uri('Student', sid)
            triples[subj].append(f'a :Student ;')
            triples[subj].append(f':name "{esc(name)}" ;')
            triples[subj].append(f':personalID "{sid}" .')

            # Enrollment
            enr_subj = uri('Enrollment', f'{sid}_{prog}')
            triples[enr_subj].append(f'a :Enrollment ;')
            
            yr = safe_int(year)
            if yr is not None:
                triples[enr_subj].append(f':enrolledYear {yr} ;')
            
            grad = safe_bool(graduated)
            if grad is not None:
                triples[enr_subj].append(f':graduated {grad} ;')
            
            triples[enr_subj].append(f':enrolledStudent {uri("Student", sid)} ;')
            triples[enr_subj].append(f':enrolledInProgram {uri("Programme", prog)} .')

def process_teaching_assistants(filepath):
    """Teaching_Assistants.csv -> :Teacher (TAs are students who assist)"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row['Teacher id'].strip()
                name = row['Teacher name'].strip()
                div = row['Division name'].strip()

                ta_teachers.add(tid)
                teachers.add(tid)

                subj = uri('Teacher', tid)
                triples[subj].append(f'a :Teacher ;')
                triples[subj].append(f':name "{esc(name)}" ;')
                triples[subj].append(f':personalID "{tid}" ;')
                triples[subj].append(f':empolyedAt {uri("Division", div)} .')
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, skipping.")

def process_senior_teachers(filepath):
    """Senior_Teachers.csv -> :SeniorTeacher"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = row['Teacher id'].strip()
                name = row['Teacher name'].strip()
                div = row['Division name'].strip()

                senior_teachers.add(tid)
                teachers.add(tid)

                subj = uri('Teacher', tid)
                triples[subj].append(f'a :SeniorTeacher, :Teacher ;')
                triples[subj].append(f':name "{esc(name)}" ;')
                triples[subj].append(f':personalID "{tid}" ;')
                triples[subj].append(f':empolyedAt {uri("Division", div)} .')
    except FileNotFoundError:
        print(f"Warning: {filepath} not found, skipping.")

def process_programmes(filepath):
    """Programmes.csv -> :Program + :directorOf on teacher"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pcode = row['Programme code'].strip()
            pname = row['Programme name'].strip()
            dept = row['Department name'].strip()
            director = row['Director'].strip()

            subj = uri('Programme', pcode)
            triples[subj].append(f'a :Program ;')
            triples[subj].append(f':programName "{esc(pname)}" ;')
            triples[subj].append(f':programCode "{pcode}" ;')
            triples[subj].append(f':givenBy {uri("Department", dept)} .')

            # Store director link
            if director:
                if director not in directors:
                    directors[director] = []
                directors[director].append(pcode)
                teachers.add(director)

def process_programme_courses(filepath):
    """Programme_Courses.csv -> :ProgramCourse"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pcode = row['Programme code'].strip()
            syear = row['Study Year'].strip()
            ayear = row['Academic Year'].strip()
            course = row['Course'].strip()
            ctype = row['Course Type'].strip()

            year_int = parse_academic_year(ayear)

            subj = uri('ProgramCourse', f'{pcode}_{course}')
            triples[subj].append(f'a :ProgramCourse ;')
            
            sy = safe_int(syear)
            if sy is not None:
                triples[subj].append(f':studyYear {sy} ;')
            
            if year_int:
                triples[subj].append(f':academicYear {year_int} ;')
            
            triples[subj].append(f':courseType "{esc(ctype)}" ;')
            triples[subj].append(f':ProgramInProgramCourse {uri("Programme", pcode)} ;')
            triples[subj].append(f':CourseInProgramCourse {uri("Course", course)} .')

def process_courses(filepath):
    """Courses.csv -> :Course"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ccode = row['Course code'].strip()
            cname = row['Course name'].strip()
            credits = row['Credits'].strip()
            level = row['Level'].strip()
            div = row['Division'].strip()
            owned = row['Owned By'].strip()

            subj = uri('Course', ccode)
            triples[subj].append(f'a :Course ;')
            triples[subj].append(f':courseName "{esc(cname)}" ;')
            triples[subj].append(f':courseCode "{ccode}" ;')
            
            cr = safe_float(credits)
            if cr is not None:
                triples[subj].append(f':credits {cr} ;')
            
            triples[subj].append(f':level "{esc(level)}" ;')
            triples[subj].append(f':ArrangedBy {uri("Division", div)} ;')
            triples[subj].append(f':ownedBy {uri("Programme", owned)} .')

def process_course_instances(filepath):
    """Course_Instances.csv -> :CourseInstance + :examinerOf"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ccode = row['Course code'].strip()
            speriod = row['Study period'].strip()
            ayear = row['Academic year'].strip()
            iid = row['Instance_id'].strip()
            examiner = row['Examiner'].strip()

            year_int = parse_academic_year(ayear)

            subj = uri('CourseInstance', iid)
            triples[subj].append(f'a :CourseInstance ;')
            triples[subj].append(f':instanceID "{iid}" ;')
            
            sp = safe_int(speriod)
            if sp is not None:
                triples[subj].append(f':studyPeriod {sp} ;')
            
            if year_int:
                triples[subj].append(f':academicYear {year_int} ;')
            
            triples[subj].append(f':InstanceOf {uri("Course", ccode)} .')

            # Store examiner link
            if examiner:
                if examiner not in examiners:
                    examiners[examiner] = []
                examiners[examiner].append(iid)
                teachers.add(examiner)

def process_course_plannings(filepath):
    """Course_plannings.csv -> augments :CourseInstance"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            iid = row['Course'].strip()  # This IS the instance ID
            planned = row['Planned number of Students'].strip()
            senior = row['Senior Hours'].strip()
            assistant = row['Assistant Hours'].strip()

            subj = uri('CourseInstance', iid)
            
            pl = safe_int(planned)
            if pl is not None:
                triples[subj].append(f':planningNumStudents {pl} ;')
            
            sh = safe_float(senior)
            if sh is not None:
                triples[subj].append(f':seniorHours {sh} ;')
            
            ah = safe_float(assistant)
            if ah is not None:
                triples[subj].append(f':assistantHours {ah} .')

def process_assigned_hours(filepath):
    """Assigned_Hours.csv -> :TeachingHours"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row['Teacher Id'].strip()
            iid = row['Course Instance'].strip()
            hours = row['Hours'].strip()

            key = (tid, iid)
            assigned = safe_float(hours)
            teaching_hours_map[key] = [assigned if assigned is not None else 0.0, 0.0]
            if tid:
                teachers.add(tid)

def process_reported_hours(filepath):
    """Reported_Hours.csv -> updates :TeachingHours"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = row['Teacher Id'].strip()
            hours = safe_float(row['Hours'].strip())
            if hours is None:
                hours = 0.0
            
            # Find existing entries for this teacher and update reported hours
            found = False
            for key in teaching_hours_map:
                if key[0] == tid:
                    teaching_hours_map[key][1] = hours
                    found = True
            if not found:
                # Create entry with zero assigned, full reported
                ccode = row['Course code'].strip()
                key = (tid, f"REPORTED_{ccode}")
                teaching_hours_map[key] = [0.0, hours]
                if tid:
                    teachers.add(tid)

def process_registrations(filepath):
    """Registrations.csv -> :CourseRegistration"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            iid = row['Course Instance'].strip()
            sid = row['Student id'].strip()
            status = row['Status'].strip()
            grade = row['Grade'].strip()

            subj = uri('CourseRegistration', f'{sid}_{iid}')
            triples[subj].append(f'a :CourseRegistration ;')
            
            if status:
                triples[subj].append(f':status "{esc(status)}" ;')
            
            gr = safe_float(grade)
            if gr is not None:
                triples[subj].append(f':grade {gr} ;')
            
            triples[subj].append(f':RegisteredStudent {uri("Student", sid)} ;')
            triples[subj].append(f':RegisteredForCourse {uri("CourseInstance", iid)} .')


# --- Write grouped triples properly ---

def write_triples(output_dir='output'):
    os.makedirs(output_dir, exist_ok=True)

    # Combine all triples per subject into complete blocks
    combined = defaultdict(list)
    for subj, props in triples.items():
        combined[subj].extend(props)

    # Write main data
    with open(os.path.join(output_dir, 'data.ttl'), 'w', encoding='utf-8') as f:
        f.write(PREFIXES)
        f.write('\n')
        for subj in sorted(combined.keys()):
            props = combined[subj]
            f.write(f'{subj}')
            for prop in props:
                if prop.endswith(' .'):
                    f.write(f'\n    {prop[:-2]} .\n')
                elif prop.endswith('.'):
                    f.write(f'\n    {prop[:-1]} .\n')
                else:
                    f.write(f'\n    {prop}')
            f.write('\n')

    # Write director links
    if directors:
        with open(os.path.join(output_dir, 'directors.ttl'), 'w', encoding='utf-8') as f:
            f.write(PREFIXES)
            f.write('\n')
            for tid, progs in directors.items():
                subj = uri('Teacher', tid)
                for prog in progs:
                    f.write(f'{subj} :directorOf {uri("Programme", prog)} .\n')

    # Write examiner links
    if examiners:
        with open(os.path.join(output_dir, 'examiners.ttl'), 'w', encoding='utf-8') as f:
            f.write(PREFIXES)
            f.write('\n')
            for tid, instances in examiners.items():
                subj = uri('Teacher', tid)
                for iid in instances:
                    f.write(f'{subj} :examinerOf {uri("CourseInstance", iid)} .\n')

    # Write teaching hours
    if teaching_hours_map:
        with open(os.path.join(output_dir, 'teaching_hours.ttl'), 'w', encoding='utf-8') as f:
            f.write(PREFIXES)
            f.write('\n')
            for (tid, iid), (assigned, reported) in teaching_hours_map.items():
                subj = uri('TeachingHours', f'{tid}_{iid}')
                f.write(f'{subj} a :TeachingHours ;\n')
                f.write(f'    :assignedHours {assigned} ;\n')
                f.write(f'    :reportedHours {reported} ;\n')
                f.write(f'    :TeacherHours {uri("Teacher", tid)} ;\n')
                f.write(f'    :TeacherCourseHours {uri("CourseInstance", iid)} .\n\n')

    # Write TA links
    if ta_teachers:
        with open(os.path.join(output_dir, 'ta_links.ttl'), 'w', encoding='utf-8') as f:
            f.write(PREFIXES)
            f.write('\n')
            for tid in ta_teachers:
                subj = uri('Teacher', tid)
                for (t, iid) in teaching_hours_map:
                    if t == tid:
                        f.write(f'{subj} :teachingAssistant {uri("CourseInstance", iid)} .\n')


# --- Run all ---
if __name__ == '__main__':
    base_dir = '.'  # Change to your CSV directory

    process_students(os.path.join(base_dir, 'Students.csv'))
    process_teaching_assistants(os.path.join(base_dir, 'Teaching_Assistants.csv'))
    process_senior_teachers(os.path.join(base_dir, 'Senior_Teachers.csv'))
    process_programmes(os.path.join(base_dir, 'Programmes.csv'))
    process_programme_courses(os.path.join(base_dir, 'Programme_Courses.csv'))
    process_courses(os.path.join(base_dir, 'Courses.csv'))
    process_course_instances(os.path.join(base_dir, 'Course_Instances.csv'))
    process_course_plannings(os.path.join(base_dir, 'Course_plannings.csv'))
    process_assigned_hours(os.path.join(base_dir, 'Assigned_Hours.csv'))
    process_reported_hours(os.path.join(base_dir, 'Reported_Hours.csv'))
    process_registrations(os.path.join(base_dir, 'Registrations.csv'))

    write_triples()
    print("RDF generation complete. Check the 'output' directory.")