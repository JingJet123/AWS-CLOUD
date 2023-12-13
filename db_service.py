from db_connection import create_connection

sequenceTable = "SEQ_MATRIX"
studentTable = 'Student'
companyTable = 'Company'
universitySupervisorTable = 'UniversitySupervisor'
adminTable = 'Admin'
taskTable = 'Task'
companyRequestTable = 'CompanyRequest'
studentPersonalTable = 'StudentPersonal'
submissionTable = 'Submission'
internshipTable = 'Internship'
internshipApplicationTable = 'InternshipApplication'
internshipJobTable = 'InternshipJob'
companyPersonnelTable = 'CompanyPersonnel'
attachmentTable = 'Attachment'

def retrieveAllStud():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + studentTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllStudDetail():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + studentPersonalTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllComp():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + companyTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllUniSup():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + universitySupervisorTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllAdmin():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + adminTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllJob():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + internshipJobTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllTask():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + taskTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllCompReq():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + companyRequestTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllInternshipApplication():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + internshipApplicationTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllInternship():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + internshipTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveAllSubmissions():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + submissionTable)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveApplicationByAppId(appId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + internshipApplicationTable + " WHERE ApplicationId = %s", (appId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveStudApplication(studEmail):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + internshipApplicationTable + " WHERE StudentEmail = %s", (studEmail,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveTaskById(taskId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + taskTable + " WHERE TaskId = %s", (taskId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveStudentBySupervisorId(supervisorId):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + studentTable + " WHERE UniversitySupervisorId = %s", (supervisorId,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveCompById(compId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + companyTable + " WHERE companyId = %s", (compId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveCompJobById(compId):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + internshipJobTable + " WHERE companyId = %s", (compId,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveJobById(jobId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + internshipJobTable + " WHERE jobId = %s", (jobId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveStudByEmail(studEmail):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + studentTable + " WHERE StudentEmail = %s", (studEmail,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveStudDetailByEmail(studEmail):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + studentPersonalTable + " WHERE StudentEmail = %s", (studEmail,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveSeqNoByTblName(tblName):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT SEQ_NO FROM " + sequenceTable + " WHERE TBL_NAME = '" + tblName + "'")
    seqNo = cur.fetchone()[0]
    cur.close()
    conn.close()
    return seqNo

def retrieveUniSupervisorByEmail(email):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + universitySupervisorTable + " WHERE Email = %s", (email,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveUniSupervisorById(id):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + universitySupervisorTable + " WHERE StaffId = %s", (id,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrievePICById(picId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + companyPersonnelTable + " WHERE PersonInChargeId = %s", (picId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveInternshipByEmail(email):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + internshipTable + " WHERE StudentEmail = %s", (email,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row

def retrieveStudentSubmissionByEmail(email):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM " + submissionTable + " WHERE StudentEmail = %s", (email,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def retrieveStudentSubmissionById(submissionId):
    row = None
    try:
        conn = create_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + submissionTable + " WHERE SubmissionId = %s", (submissionId,))
        row = cur.fetchone()
    except Exception as e:
        print(e)
    finally:
        cur.close()
        conn.close()
    return row