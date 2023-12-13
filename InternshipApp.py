from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from flask_session import Session
from datetime import datetime, time
from s3_service import uploadToS3, get_object_url
from Models import *
from db_connection import create_connection
from utils import *
from db_service import *

app = Flask(__name__, template_folder='template/dist',
            static_folder="template/dist/assets")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Session(app)

output = {}
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


@app.route("/")
def home():
    return render_template('login.html')


@app.route("/<page_name>")
def render_page(page_name):
    return render_template('%s.html' % page_name)


@app.route("/<folder>/<page_name>")
def render_subFolder_page(folder, page_name):
    return render_template("%s/%s.html" % (folder, page_name))


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --------------------- Student ---------------------------


@app.route("/studentRegister")
def studentRegister():

    connection = create_connection()
    cursor = connection.cursor()
    try:

        uniSupervisorResults = retrieveAllUniSup()
        uniSupervisorList = []
        for supervisor in uniSupervisorResults:
            uniSupervisorList.append(UniversitySupervisor(
                supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4]))

    except Exception as e:
        connection.rollback()  # Rollback the transaction if an exception occurs
    finally:
        cursor.close()
        connection.close()

    error = get_flashed_messages(category_filter=['student-error'])
    if error:
        error = error[0]
    return render_template('studentRegister.html', uniSupervisorList=uniSupervisorList, error=error)


@app.route("/AddStud", methods=['POST'])
def AddStud():
    # Student Table
    studEmail = request.form['studentEmail']
    curEduLevel = request.form['level']
    cohort = request.form['cohort']
    programme = request.form['programme']
    tutGrp = request.form['tutorialGroup']
    latestCgpa = request.form['cgpa']
    studId = request.form['studentId']
    supervisorEmail = request.form['supervisorEmail']
    # StudentPersonal Table
    studName = request.form['studentName']
    nric = request.form['nric']
    gender = request.form['gender']
    ownTransport = request.form['transport']
    healthRemark = request.form['healthRemark']
    personalEmail = request.form['personalEmail']
    termAddr = request.form['termAddress']
    permAddr = request.form['permAddress']
    contactNo = request.form['mobile']
    profilePic = request.files['profile']
    # FK StudentEmail <-- Student Table

    insertStud_sql = "INSERT INTO " + studentTable + \
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    insertStudPersonal_sql = "INSERT INTO " + studentPersonalTable + \
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    connection = create_connection()
    cursor = connection.cursor()

    try:

        if (retrieveStudByEmail(studEmail) is not None):
            print("Student already exists")
            flash("Student already exists", 'student-error')
            # Redirect to the studentRegister route
            return redirect("/studentRegister")

        # Execute the query
        uniSupervisor = retrieveUniSupervisorByEmail(supervisorEmail)
        supervisorId = uniSupervisor[0]

        # Upload image file in S3
        uploadToS3(profilePic, "students/" + studEmail + "/profile.png")
        profilePath = "students/" + studEmail + "/profile.png"

        insertStud_sql = "INSERT INTO " + studentTable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        insertStudPersonal_sql = "INSERT INTO " + studentPersonalTable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        cursor.execute(insertStud_sql, (studEmail, curEduLevel, cohort,
                       programme, tutGrp, latestCgpa, studId, supervisorId))
        cursor.execute(insertStudPersonal_sql, (studName, nric, gender, ownTransport,
                       healthRemark, personalEmail, termAddr, permAddr, contactNo, profilePath, studEmail))

        connection.commit()
    except Exception as e:
        connection.rollback()  # Rollback the transaction if an exception occurs
    finally:
        cursor.close()
        connection.close()

    return render_template("studentLogin.html", success="You may login now")


@app.route("/StudLogin", methods=['POST'])
def StudLogin():
    studEmail = request.form['studentEmail']
    nric = request.form['nric']

    allStudentDetails = retrieveAllStudDetail()

    for stud in allStudentDetails:
        if stud[-1] == studEmail and stud[1] == nric:
            session["studEmail"] = studEmail
            return redirect("/studentHome")

    return render_template('studentLogin.html', error="Invalid Email or NRIC")


@app.route("/studentHome")
def studentDashboard():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    internship = retrieveInternshipByEmail(studEmail)
    if internship != None:
        internship = Internship(internship[0], internship[1], internship[2], internship[3],
                                internship[4], internship[5], internship[6], internship[7], internship[8])

    pendingTaskCount = 0
    approvedTaskCount = 0
    rejectTaskCount = 0
    for submission in retrieveStudentSubmissionByEmail(studEmail):
        if submission[2] == None:
            pendingTaskCount += 1
        if submission[1] == "Approved":
            approvedTaskCount += 1
        elif submission[1] == "Rejected":
            rejectTaskCount += 1

    return render_template("studentHome.html", student=student, internship=internship, pendingTaskCount=pendingTaskCount, approvedTaskCount=approvedTaskCount, rejectedTaskCount=rejectTaskCount)


@app.route("/studentTask")
def studentTask():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    studentTasks = retrieveStudentSubmissionByEmail(studEmail)

    pendingTask = []
    completedTask = []
    for studentTask in studentTasks:
        studentTask = Submission(studentTask[0], studentTask[1], studentTask[2],
                                 studentTask[3], studentTask[4], studentTask[5], studentTask[6])
        print(studentTask)
        task = retrieveTaskById(studentTask.taskId)
        print(task)
        task = Task(task[0], task[1], task[2],
                    task[3], task[4], task[5], task[6])
        studentTask.taskName = task.taskName
        studentTask.taskDesc = task.taskDesc
        studentTask.dueDate = task.dueDate.strftime("%d, %b %H:%M %p")
        studentTask.attachmentName = task.attachmentName
        studentTask.attachmentURL = get_object_url(task.attachmentURL)
        if studentTask.dateSubmitted == None:
            studentTask.submissionStatus = "Pending"
            pendingTask.append(studentTask)
        else:
            studentTask.submissionStatus = "Submitted"
            completedTask.append(studentTask)

    return render_template("studentTask.html", student=student, pdngTask=pendingTask, cptdTask=completedTask)


@app.route("/viewTask")
def viewTask():
    studEmail = session["studEmail"]
    submissionId = request.args.get('submissionId')
    submissionStatus = request.args.get('submissionStatus')
    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    print(submissionId)
    submission = retrieveStudentSubmissionById(submissionId)
    print(submission)
    submission = Submission(submission[0], submission[1], submission[2],
                            submission[3], submission[4], submission[5], submission[6])
    task = retrieveTaskById(submission.taskId)
    task = Task(task[0], task[1], task[2], task[3], task[4], task[5], task[6])
    task.attachmentURL = get_object_url(task.attachmentURL)
    if submissionStatus == "pending":
        if (datetime.now() > task.dueDate):
            submitStatus = "Missing"
        else:
            submitStatus = "Pending"
    elif submissionStatus == "submitted":
        if (submission.dateSubmitted > task.dueDate):
            submitStatus = "Turned in Late"
        else:
            submitStatus = "Submitted"
    task.dueDate = task.dueDate.strftime("%d, %b %H:%M %p")
    if submission.dateSubmitted != None:
        submission.dateSubmitted = submission.dateSubmitted.strftime(
            "%d, %b %H:%M %p")

    success = get_flashed_messages(category_filter=['submit-success'])
    if success:
        success = success[0]

    return render_template("/viewTask.html", student=student, submission=submission, taskViewing=task, submitStatus=submitStatus, success=success)


@app.route("/SubmitTask", methods=['GET', 'POST'])
def SubmitTask():
    submissionId = request.form['submissionId']
    report = request.files['report']
    taskName = request.form['taskName']
    dateSubmitted = datetime.now()

    try:
        connection = create_connection()
        cursor = connection.cursor()
        updateSubmission_sql = "UPDATE " + submissionTable + \
            " SET Report = %s, DateSubmitted = %s WHERE SubmissionId = %s"
        path = "students/" + session["studEmail"] + \
            "/" + taskName + "/" + report.filename
        uploadToS3(report, path)
        cursor.execute(updateSubmission_sql,
                       (path, dateSubmitted, submissionId))
        connection.commit()

        flash("Your report has been submitted successfully", 'submit-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/viewTask?submissionId=" + submissionId + "&submissionStatus=submitted")


@app.route("/jobFinding")
def jobFinding():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    internshipJobs = []

    # Retrieve all jobs and companies in one query
    jobs = retrieveAllJob()
    companies = {comp[0]: Company(*comp) for comp in retrieveAllComp()}

    internshipJobs = []

    for job in jobs:
        job = InternshipJob(*job)
        company = companies.get(job.companyId)
        if company:
            job.companyName = company.companyName
            if company.logo:
                job.companyLogo = get_object_url(company.logo)
            else:
                job.companyLogo = ""
        internshipJobs.append(job)

    success = get_flashed_messages(category_filter=['apply-job-success'])
    if success:
        success = success[0]

    jobApplied = get_flashed_messages(category_filter=['applied-job'])
    if jobApplied:
        jobApplied = jobApplied[0]

    internshipSecured = False
    studentInternship = retrieveInternshipByEmail(studEmail)
    if studentInternship != None:
        internshipSecured = True

    return render_template("jobFinding.html", student=student, internshipJobs=internshipJobs, success=success, jobApplied=jobApplied, internshipSecured=internshipSecured)


@app.route("/ApplyJob")
def ApplyJob():
    studEmail = session["studEmail"]
    jobId = request.args.get("jobId")

    seqNo = retrieveSeqNoByTblName(internshipApplicationTable)
    applicationId = "APP" + fillLeftZero(4, seqNo)
    applicationStatus = "Pending"

    # Check if student has already applied for this job
    for application in retrieveAllInternshipApplication():
        if application[6] == studEmail and application[5] == jobId:
            flash("You have already applied for this job before.", 'applied-job')
            return redirect("/jobFinding")
    try:
        connection = create_connection()
        cursor = connection.cursor()

        updateInternshipAppSeqNo_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + internshipApplicationTable + "'"
        cursor.execute(updateInternshipAppSeqNo_sql)
        insertInternshipApp_sql = "INSERT INTO " + internshipApplicationTable + \
            " (ApplicationId, ApplicationStatus, ApplyDate, JobId, StudentEmail) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insertInternshipApp_sql, (applicationId,
                       applicationStatus, datetime.now(), jobId, studEmail))

        connection.commit()

        flash("Your job application has been submitted successfully.",
              'apply-job-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/jobFinding")


@app.route("/studentJob")
def studentJob():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    jobsApplied = []

    for application in retrieveStudApplication(studEmail):
        application = InternshipApplication(*application)
        job = retrieveJobById(application.jobId)
        job = InternshipJob(*job)
        company = retrieveCompById(job.companyId)
        company = Company(*company)
        application.jobTitle = job.jobTitle
        application.allowance = job.allowance
        application.companyName = company.companyName
        application.applyDate = application.applyDate.strftime(
            "%d, %b %H:%M %p")
        if application.reviewDate != None:
            application.reviewDate = application.reviewDate.strftime(
                "%d, %b %H:%M %p")
        jobsApplied.append(application)

    return render_template("studentJob.html", student=student, jobsApplied=jobsApplied)


@app.route("/updateInternship")
def updateInternship():
    studEmail = session["studEmail"]
    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}
    # If student has already submitted internship details, redirect the student to updateInternshipView html
    studentInternship = retrieveInternshipByEmail(studEmail)
    if studentInternship != None:
        success = get_flashed_messages(
            category_filter=['intern-submit-success'])
        if success:
            success = success[0]
        studentInternship = Internship(studentInternship[0], studentInternship[1], studentInternship[2], studentInternship[3],
                                       studentInternship[4], studentInternship[5], studentInternship[6], studentInternship[7], studentInternship[8])
        studentInternship.companyAcceptanceForm = get_object_url(
            studentInternship.companyAcceptanceForm)
        studentInternship.parentAckForm = get_object_url(
            studentInternship.parentAckForm)
        studentInternship.indemnityLetter = get_object_url(
            studentInternship.indemnityLetter)
        return render_template("updateInternshipView.html", student=student, studentInternship=studentInternship, success=success)

    # If student has not submitted
    # Retrieve all approved companies and approved company requests
    companies = [{"compName": comp[1], "compAddr": comp[5]}
                 for comp in retrieveAllComp() if comp[10] == "Approved"]
    approvedReqCompanies = [{"compName": comp[1], "compAddr": comp[2]}
                            for comp in retrieveAllCompReq() if comp[3] == "Approved"]
    # Append approved company requests to approved companies
    companies.extend(approvedReqCompanies)

    requestCompMessage = get_flashed_messages(
        category_filter=['request-comp-success'])
    if requestCompMessage:
        requestCompMessage = requestCompMessage[0]

    return render_template("updateInternship.html", student=student, companies=companies, requestCompMessage=requestCompMessage)


@app.route("/AddInternship", methods=['POST'])
def AddInternship():
    studEmail = session["studEmail"]
    companyName = request.form['compName']
    companyAddress = request.form['companyAddr']
    allowance = request.form['allowance']
    compSupervisorName = request.form['compSupName']
    compSupervisorEmail = request.form['email']
    compAcceptance = request.files['comAcceptance']
    parentAck = request.files['parentForm']
    indemnityLetter = request.files['letter']

    try:
        connection = create_connection()
        cursor = connection.cursor()

        insertInternship_sql = "INSERT INTO " + internshipTable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        internshipDocPath = "students/" + studEmail + "/internship/"
        compAcceptancePath = internshipDocPath + "CompanyAcceptance.pdf"
        parentAckPath = internshipDocPath + "ParentAcknowledgement.pdf"
        indemnityLetterPath = internshipDocPath + "IndemnityLetter.pdf"
        uploadToS3(compAcceptance, compAcceptancePath)
        uploadToS3(parentAck, parentAckPath)
        uploadToS3(indemnityLetter, indemnityLetterPath)

        cursor.execute(insertInternship_sql, (studEmail, companyName, companyAddress, allowance,
                       compSupervisorName, compSupervisorEmail, compAcceptancePath, parentAckPath, indemnityLetterPath))

        connection.commit()

        flash("Your internship details have been submitted successfully",
              'intern-submit-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/updateInternship")


@app.route("/requestCompany")
def requestCompany():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    student = {"name": studentPersonal[0], "studId": student[6],
               "profilePic": get_object_url(studentPersonal[9])}

    return render_template("requestCompany.html", student=student)


@app.route("/RequestInternCompany", methods=['POST'])
def RequestInternCompany():
    companyName = request.form['comName']
    companyAddr = request.form['comAddr']
    studEmail = session["studEmail"]
    requestStatus = "Pending"

    seqNo = retrieveSeqNoByTblName(companyRequestTable)
    reqeustId = "CREQ" + fillLeftZero(4, seqNo)

    try:
        connection = create_connection()
        cursor = connection.cursor()

        insertCompanyRequest_sql = "INSERT INTO " + companyRequestTable + \
            " (RequestId, CompanyName, CompanyAddress, RequestStatus, StudentEmail) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insertCompanyRequest_sql, (reqeustId,
                       companyName, companyAddr, requestStatus, studEmail))

        updateReqSeqNo_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + companyRequestTable + "'"
        cursor.execute(updateReqSeqNo_sql)
        connection.commit()
        flash("Your request has been submitted successfully. Please wait for admin approval. . You will be notified via email once your company request is updated.", 'request-comp-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/updateInternship")


@app.route("/studentProfile")
def studentProfile():
    studEmail = session["studEmail"]

    student = retrieveStudByEmail(studEmail)
    studentPersonal = retrieveStudDetailByEmail(studEmail)
    studentObj = Student(student[0], student[1], student[2], student[3], student[4], student[5], student[6], student[7],
                         studentPersonal[0], studentPersonal[1], studentPersonal[2], studentPersonal[3], studentPersonal[4], studentPersonal[5], studentPersonal[6], studentPersonal[7], studentPersonal[8], studentPersonal[9])

    studentObj.profilePic = get_object_url(studentObj.profilePic)
    supervisor = retrieveUniSupervisorById(studentObj.supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])
    student_dict = vars(studentObj)
    for key, value in student_dict.items():
        print(f"{key}: {value}")

    success = get_flashed_messages(category_filter=['update-success'])
    if success:
        success = success[0]

    return render_template("studentProfile.html", student=studentObj, supervisor=supervisor, success=success)


@app.route("/UpdateStudProfile", methods=['POST'])
def updateStudProfile():
    studEmail = session["studEmail"]
    # profile, cgpa, own transport, health remarks, personal email, mobile, term address

    cgpa = request.form['cgpa']
    ownTransport = request.form['transport']
    healthRemark = request.form.get('healthRemark', '')
    personalEmail = request.form['personalEmail']
    mobile = request.form['mobile']
    termAddr = request.form.get('termAddr', '')

    connection = create_connection()
    cursor = connection.cursor()

    try:
        updateStud_sql = "UPDATE " + studentTable + \
            " SET LatestCgpa = %s WHERE StudentEmail = %s"
        updateStudProfile_sql = "UPDATE " + studentPersonalTable + \
            " SET ProfilePic = %s WHERE StudentEmail = %s"
        updateStudPersonal_sql = "UPDATE " + studentPersonalTable + \
            " SET OwnTransport = %s, HealthRemark = %s, PersonalEmail = %s, ContactNo = %s, TermAddress = %s WHERE StudentEmail = %s"
        if 'profile' in request.files:
            profilePic = request.files['profile']
            if profilePic.filename != '':
                # Upload image file in S3

                profilePath = "students/" + studEmail + "/profile_" + datetime.now() + ".png"
                uploadToS3(profilePic, profilePath)
                # Update profile pic path in Student Table
                cursor.execute(updateStudProfile_sql, (profilePath, studEmail))

        cursor.execute(updateStud_sql, (cgpa, studEmail))
        cursor.execute(updateStudPersonal_sql, (ownTransport,
                       healthRemark, personalEmail, mobile, termAddr, studEmail))
        connection.commit()
        flash("Your profile has been updated!", 'update-success')
        print("success")
    except Exception as e:
        print(e)
        connection.rollback()  # Rollback the transaction if an exception occurs
        print("got problem")
    finally:
        cursor.close()
        connection.close()

    return redirect("/studentProfile")

# --------------------- Student ---------------------------


# --------------------- Company ---------------------------
@app.route("/AddCompany", methods=['POST'])
def AddComp():

    # Company Table
    compName = request.form['companyName']
    username = request.form['cUsername']
    password = request.form['cPassword']
    otClaim = request.form['otClaim']
    compAddr = request.form['address']
    ssmCert = request.files['ssmCert']
    industry = request.form.getlist('industries')
    totalStaff = request.form['totalStaff']
    companyStatus = "Pending"
    website = request.form.get('website', '')
    # FK PersonInChargeId <-- CompanyPersonnel Table
    # CompanyPersonnel Table
    name = request.form['personName']
    designation = request.form['designation']
    contactNo = request.form['contact']
    email = request.form['pEmail']

    insertComp_sql = "INSERT INTO " + companyTable + \
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insertPic_sql = "INSERT INTO " + \
        companyPersonnelTable + " VALUES (%s, %s, %s, %s, %s)"
    connection = create_connection()
    cursor = connection.cursor()
    delimiter = '|'
    try:
        print("hii")
        success = ""
        # Retrieve company id sequence number from table SEQ_MATRIX
        retrieveSeqNo_sql = "SELECT SEQ_NO FROM " + \
            sequenceTable + " WHERE TBL_NAME = '" + companyTable + "'"
        cursor.execute(retrieveSeqNo_sql)
        seqNo = cursor.fetchone()[0]
        compId = "CP" + fillLeftZero(6, seqNo)
        # Retrieve person in charge id sequence number from table SEQ_MATRIX
        retrieveSeqNo_sql = "SELECT SEQ_NO FROM " + sequenceTable + \
            " WHERE TBL_NAME = '" + companyPersonnelTable + "'"
        cursor.execute(retrieveSeqNo_sql)
        seqNo = cursor.fetchone()[0]
        picId = "PIC" + fillLeftZero(4, seqNo)

        # Update sequence number in SEQ_MATRIX
        updateCmpSeq_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + companyTable + "'"
        updatePicSeq_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + companyPersonnelTable + "'"
        cursor.execute(updateCmpSeq_sql)
        cursor.execute(updatePicSeq_sql)

        compLogoPath = ""
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename != '':
                print("logo not empty")
                # Upload image file in S3
                uploadToS3(logo, "companies/" + compId + "/logo.png")
                compLogoPath = "companies/" + compId + "/logo.png"
        # Upload ssm cert pdf file in S3
        uploadToS3(ssmCert, "companies/" + compId + "/ssmCert.pdf")
        ssmCertPath = "companies/" + compId + "/ssmCert.pdf"

        cursor.execute(insertPic_sql, (picId, name,
                       designation, contactNo, email))
        cursor.execute(insertComp_sql, (compId, compName, username, password, otClaim, compAddr,
                       ssmCertPath, delimiter.join(industry), compLogoPath, totalStaff, companyStatus, website, picId))

        connection.commit()
        success = "Company registration successful. Please wait for admin approval. You will be notified via email once your company status is updated."
    except Exception as e:
        print(e)
        connection.rollback()  # Rollback the transaction if an exception occurs
    finally:
        cursor.close()
        connection.close()

    return render_template("companyLogin.html", success=success)


@app.route("/CompLogin", methods=['POST'])
def CompLogin():
    username = request.form['username']
    password = request.form['password']

    allCompanies = retrieveAllComp()

    for company in allCompanies:
        if company[2] == username and company[3] == password:
            session["companyId"] = company[0]
            return redirect("/companyHome")

    return render_template('companyLogin.html', error="Invalid Username or Password")


@app.route("/companyHome")
def companyDashboard():
    compId = session["companyId"]
    companyResult = retrieveCompById(compId)

    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}

    jobList = retrieveCompJobById(compId)
    jobCount = len(jobList)

    # get the total application received
    totalApplication = len([appl for appl in retrieveAllInternshipApplication(
    ) if any(appl[5] == job[0] for job in jobList)])

    return render_template("companyHome.html", company=company, jobCount=jobCount, totalApplication=totalApplication)


@app.route("/companyViewApplicant")
def companyViewApplicant():
    compId = session["companyId"]
    companyResult = retrieveCompById(compId)

    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}

    allStudents = retrieveAllStud()
    allStudentsDetails = retrieveAllStudDetail()
    jobLists = retrieveCompJobById(compId)
    allApplicants = retrieveAllInternshipApplication()

    # Create dictionaries to map student and student detail data by ID
    students_dict = {student[0]: (student[1], student[5])
                     for student in allStudents}
    stud_details_dict = {studDetail[10]: studDetail[0]
                         for studDetail in allStudentsDetails}

    applicantLists = []

    for job in jobLists:
        for application in allApplicants:
            if job[0] == application[5]:
                studentEmail = application[6]
                if studentEmail in students_dict and studentEmail in stud_details_dict:
                    application = InternshipApplication(
                        application[0], application[1], application[2], application[3],
                        application[4], application[5], studentEmail
                    )
                    application.applyDate = application.applyDate.strftime(
                        '%Y-%m-%d')
                    application.studentName = stud_details_dict[studentEmail]
                    application.level = students_dict[studentEmail][0]
                    application.cgpa = students_dict[studentEmail][1]
                    application.jobTitle = job[1]
                    application.allowance = job[3]
                    applicantLists.append(application)

    return render_template("companyViewApplicant.html", company=company, applicantLists=applicantLists)


@app.route("/updateApplicant")
def updateApplicant():
    compId = session["companyId"]
    companyResult = retrieveCompById(compId)

    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}

    applicationId = request.args.get('appId')
    application = retrieveApplicationByAppId(applicationId)
    application = InternshipApplication(application[0], application[1], application[2], application[3],
                                        application[4], application[5], application[6])
    application.applyDate = application.applyDate.strftime('%Y-%m-%d')
    stud = retrieveStudByEmail(application.studentEmail)
    studDetail = retrieveStudDetailByEmail(application.studentEmail)
    stud = Student(stud[0], stud[1], stud[2], stud[3], stud[4], stud[5], stud[6], stud[7],
                   studDetail[0], studDetail[1], studDetail[2], studDetail[3], studDetail[4], studDetail[5], studDetail[6], studDetail[7], studDetail[8], studDetail[9])
    stud.profilePic = get_object_url(stud.profilePic)
    job = retrieveJobById(application.jobId)
    job = InternshipJob(job[0], job[1], job[2], job[3], job[4],
                        job[5], job[6], job[7], job[8], job[9], job[10])

    success = get_flashed_messages(
        category_filter=['update-applicant-success'])
    if success:
        success = success[0]

    return render_template("updateApplicant.html", company=company, application=application, student=stud, job=job, success=success)


@app.route("/UpdateApplicantStatus")
def UpdateApplicantStatus():
    applicationId = request.args.get('applicationId')
    applicationStatus = request.args.get('statusUpdate')
    reviewDate = datetime.now()
    remark = request.args.get('remark')

    try:
        updateApplication_sql = "UPDATE " + internshipApplicationTable + \
            " SET ApplicationStatus = %s, ReviewDate = %s, Remarks = %s WHERE ApplicationId = %s"
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(updateApplication_sql, (applicationStatus,
                       reviewDate, remark, applicationId))
        connection.commit()
        flash("Applicant status has been updated successfully.",
              'update-applicant-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/updateApplicant?appId=" + applicationId)


@app.route("/companyProfile")
def companyProfile():
    compId = session['companyId']
    companyResult = retrieveCompById(compId)
    picResult = retrievePICById(companyResult[12])

    company = Company(companyResult[0], companyResult[1], companyResult[2], companyResult[3], companyResult[4], companyResult[5],
                      companyResult[6], companyResult[7], companyResult[8], companyResult[9], companyResult[10], companyResult[11], companyResult[12])
    pic = CompanyPersonnel(picResult[0], picResult[1],
                           picResult[2], picResult[3], picResult[4])
    company.logo = get_object_url(company.logo)

    success = get_flashed_messages(category_filter=['update-success'])
    if success:
        success = success[0]

    return render_template("companyProfile.html", company=company, personInCharge=pic, success=success)


@app.route("/UpdateCompProfile", methods=['POST'])
def updateCompProfile():
    # Company Table
    compId = session['companyId']
    compName = request.form['companyName']
    otClaim = request.form['otClaim']
    compAddr = request.form['address']
    industry = request.form.getlist('industries')
    totalStaff = request.form['totalStaff']
    website = request.form.get('website', '')
    # FK PersonInChargeId <-- CompanyPersonnel Table
    # CompanyPersonnel Table
    picId = request.form['personInChargeId']
    name = request.form['personName']
    designation = request.form['designation']
    contactNo = request.form['contact']
    email = request.form['pEmail']

    updateCompany_sql = "UPDATE " + companyTable + \
        " SET CompanyName = %s, OTClaim = %s, Address = %s, Industry = %s, TotalStaff = %s, Website = %s WHERE CompanyId = %s"
    updateCompanyPersonnel_sql = "UPDATE " + companyPersonnelTable + \
        " SET Name = %s, Designation = %s, ContactNo = %s, Email = %s WHERE PersonInChargeId = %s"
    connection = create_connection()
    cursor = connection.cursor()
    delimiter = '|'
    try:
        print("hii")
        compLogoPath = ""
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo.filename != '':
                print("logo not empty")
                # Upload image file in S3
                compLogoPath = "companies/" + compId + "/logo_"+ datetime.now() + ".png"
                uploadToS3(logo, compLogoPath)
                updateCompLogo_sql = "UPDATE " + companyTable + \
                    " SET Logo = %s WHERE CompanyId = %s"
                cursor.execute(updateCompLogo_sql, (compLogoPath, compId))
        cursor.execute(updateCompany_sql, (compName, otClaim, compAddr,
                       delimiter.join(industry), totalStaff, website, compId))
        cursor.execute(updateCompanyPersonnel_sql,
                       (name, designation, contactNo, email, picId))

        flash("Your profile has been updated!", 'update-success')
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()  # Rollback the transaction if an exception occurs
    finally:
        cursor.close()
        connection.close()

    return redirect("/companyProfile")


@app.route("/jobPosting")
def jobPosting():
    compId = session["companyId"]

    companyResult = retrieveCompById(compId)
    jobsResult = retrieveCompJobById(compId)

    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}
    companyJobs = []
    for job in jobsResult:
        job = InternshipJob(job[0], job[1], job[2], job[3], job[4],
                            job[5], job[6], job[7], job[8], job[9], job[10])
        companyJobs.append(job)

    success = get_flashed_messages(category_filter=['job-added'])
    if success:
        success = success[0]

    deleted = get_flashed_messages(category_filter=['job-deleted'])
    if deleted:
        deleted = deleted[0]

    return render_template("jobPosting.html", company=company, companyJobs=companyJobs, success=success, deleted=deleted)


@app.route("/JobPostingDetailViewEdit")
def JobPostingDetails():
    jobId = request.args.get('jobId')
    compId = session["companyId"]

    companyResult = retrieveCompById(compId)
    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}
    jobResult = retrieveJobById(jobId)
    job = InternshipJob(jobResult[0], jobResult[1], jobResult[2], jobResult[3], jobResult[4],
                        jobResult[5], jobResult[6], jobResult[7], jobResult[8], jobResult[9], jobResult[10])

    success = get_flashed_messages(category_filter=['update-success'])
    if success:
        success = success[0]

    return render_template("JobPostingDetailViewEdit.html", company=company, job=job, success=success)


@app.route("/UpdateJobDetail", methods=['POST'])
def updateJobDetail():
    jobId = request.form['jobId']
    jobTitle = request.form['jobTitle']
    jobDesc = request.form['jobDesc']
    allowance = request.form['allowance']
    workingDay = request.form['workingDay']
    workingHour = request.form['workingHour']
    openFor = request.form['openFor']
    accessory = request.form['accessory']
    accommodation = request.form['accommodation']

    # by default, set these 2 to "N"
    diploma = "N"
    degree = "N"

    if openFor == "diploma":
        diploma = "Y"
    elif openFor == "degree":
        degree = "Y"
    elif openFor == "diplomaAndDegree":
        diploma = "Y"
        degree = "Y"

    updateJobDetail_sql = "UPDATE " + internshipJobTable + \
        " SET JobTitle = %s, JobDescription = %s, Allowance = %s, WorkingDay = %s, WorkingHour = %s, Diploma = %s, Degree = %s, AccessoryProvide = %s, Accommodation = %s WHERE JobId = %s"
    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(updateJobDetail_sql, (jobTitle, jobDesc, allowance, workingDay,
                       workingHour, diploma, degree, accessory, accommodation, jobId))
        connection.commit()
        flash("Job Post has been updated successfully", 'update-success')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/JobPostingDetailViewEdit?jobId=" + jobId)


@app.route("/jobAdding")
def jobPostingDetail():
    compId = session["companyId"]

    companyResult = retrieveCompById(compId)
    company = {"companyName": companyResult[1], "username": companyResult[2], "logo": get_object_url(
        companyResult[8]), "companyStatus": companyResult[10]}

    return render_template("jobAdding.html", company=company)


@app.route("/AddJob", methods=['POST'])
def AddJob():
    # InternshipJob Table
    # jobId = request.form['jobId']
    jobTitle = request.form['jobTitle']
    jobDesc = request.form['jobDesc']
    allowance = request.form['allowance']
    workingDay = request.form['workingDay']
    workingHour = request.form['workingHour']
    openFor = request.form['openFor']
    accessory = request.form['accessory']
    accommodation = request.form['accommodation']
    # by default, set these 2 to "N"
    diploma = "N"
    degree = "N"

    if openFor == "diploma":
        diploma = "Y"
    elif openFor == "degree":
        degree = "Y"
    elif openFor == "diplomaAndDegree":
        diploma = "Y"
        degree = "Y"
    # FK companyId <-- Company Table
    compId = session["companyId"]
    try:
        insertJob_sql = "INSERT INTO " + internshipJobTable + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

        seqNo = retrieveSeqNoByTblName(internshipJobTable)
        print(seqNo)
        jobId = "J" + fillLeftZero(5, seqNo)
        print(jobId)
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(insertJob_sql, (jobId, jobTitle, jobDesc, allowance, workingDay,
                       workingHour, diploma, degree, accessory, accommodation, compId))

        # Update sequence number in SEQ_MATRIX
        updateJobSeq_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + internshipJobTable + "'"
        cursor.execute(updateJobSeq_sql)
        connection.commit()
        flash("Job has been added successfully", 'job-added')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/jobPosting")


@app.route("/DeleteJobPost")
def DeleteJob():
    jobId = request.args.get('jobId')
    try:
        connection = create_connection()
        cursor = connection.cursor()
        deleteApp_sql = "DELETE FROM " + internshipApplicationTable + " WHERE JobId = %s"
        cursor.execute(deleteApp_sql, (jobId))
        deleteJob_sql = "DELETE FROM " + internshipJobTable + " WHERE JobId = %s"
        cursor.execute(deleteJob_sql, (jobId))

        connection.commit()
        flash(
            "Job Post has been deleted, relevant applications also removed.", 'job-deleted')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/jobPosting")


# --------------------- Company ---------------------------


# --------------------- Supervisor ---------------------------
@app.route("/SupervisorLogin", methods=['POST'])
def SupervisorLogin():
    email = request.form['email']
    password = request.form['password']

    allSupervisor = retrieveAllUniSup()
    for sup in allSupervisor:
        if sup[1] == email and sup[2] == password:
            session["supervisorId"] = sup[0]
            return redirect("/supervisorHome")

    return render_template('supervisorLogin.html', error="Invalid Email or Password")


@app.route("/supervisorHome")
def supervisorDashboard():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    allSupervisedStudents = retrieveStudentBySupervisorId(supervisorId)
    diplomaStudCount = 0
    degreeStudCount = 0

    for stud in allSupervisedStudents:
        if stud[2] == "Diploma":
            diplomaStudCount += 1
        else:
            degreeStudCount += 1

    return render_template("supervisorHome.html", supervisor=supervisor, diplomaStudCount=diplomaStudCount, degreeStudCount=degreeStudCount)


@app.route("/studentProgress")
def studentProgress():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    allSupervisedStudents = retrieveStudentBySupervisorId(supervisorId)
    allStudentsDet = {stud[10]: stud for stud in retrieveAllStudDetail()}
    allInternship = {internship[0]: internship[1]
                     for internship in retrieveAllInternship()}

    allSubmissions = retrieveAllSubmissions()
    supervisedStudents = []

    # Group submissions by student email
    submissions_by_student = {}
    for submission in allSubmissions:
        student_email = submission[5]
        if student_email not in submissions_by_student:
            submissions_by_student[student_email] = []
        submission = Submission(submission[0], submission[1], submission[2],
                                submission[3], submission[4], submission[5], submission[6])
        submissions_by_student[student_email].append(submission)

    for stud in allSupervisedStudents:
        studDet = allStudentsDet.get(stud[0])
        print(studDet)
        companyName = allInternship.get(stud[0], "Not Secured Yet")
        if studDet:
            student = Student(stud[0], stud[1], stud[2], stud[3], stud[4], stud[5], stud[6], stud[7], studDet[0],
                              studDet[1], studDet[2], studDet[3], studDet[4], studDet[5], studDet[6], studDet[7], studDet[8], studDet[9])
            student.companyName = companyName
            student.submissions = submissions_by_student.get(stud[0], [])
            print(student.companyName)
            print(student.submissions)
            supervisedStudents.append(student)

    return render_template("studentProgress.html", supervisor=supervisor, supervisedStudents=supervisedStudents)


@app.route("/supervisorStudentView")
def supervisorStudentView():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    student = retrieveStudByEmail(request.args.get('studentEmail'))
    studentDet = retrieveStudDetailByEmail(request.args.get('studentEmail'))
    student = Student(student[0], student[1], student[2], student[3], student[4], student[5], student[6], student[7], studentDet[0],
                      studentDet[1], studentDet[2], studentDet[3], studentDet[4], studentDet[5], studentDet[6], studentDet[7], studentDet[8], studentDet[9])
    student.profilePic = get_object_url(student.profilePic)
    internship = retrieveInternshipByEmail(request.args.get('studentEmail'))
    if internship != None:
        internship = Internship(internship[0], internship[1], internship[2], internship[3],
                                internship[4], internship[5], internship[6], internship[7], internship[8])

    return render_template("supervisorStudentView.html", supervisor=supervisor, student=student, internship=internship)


@app.route("/supervisorStudentReportView")
def supervisorStudentReportView():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    student = retrieveStudByEmail(request.args.get('studentEmail'))
    studentDet = retrieveStudDetailByEmail(request.args.get('studentEmail'))
    student = Student(student[0], student[1], student[2], student[3], student[4], student[5], student[6], student[7], studentDet[0],
                      studentDet[1], studentDet[2], studentDet[3], studentDet[4], studentDet[5], studentDet[6], studentDet[7], studentDet[8], studentDet[9])
    student.profilePic = get_object_url(student.profilePic)

    studSubmissions = []

    allTasks = retrieveAllTask()

    for submission in retrieveAllSubmissions():
        submission = Submission(submission[0], submission[1], submission[2],
                                submission[3], submission[4], submission[5], submission[6])
        if submission.studentEmail == student.studEmail:
            for task in allTasks:
                if submission.taskId == task[0]:
                    submission.taskTitle = task[1]
                    submission.dueDate = datetime.strftime(task[3], '%Y-%m-%d')
                    break
            print(submission.dateSubmitted)
            if submission.dateSubmitted != None:
                submission.dateSubmitted = datetime.strftime(
                    submission.dateSubmitted, '%Y-%m-%d %I:%M:%S %p')
            print(submission.dateSubmitted)
            submission.report = get_object_url(submission.report)
            studSubmissions.append(submission)

    print(studSubmissions)

    success = get_flashed_messages(category_filter=['update-report-success'])
    if success:
        success = success[0]

    return render_template("supervisorStudentReportView.html", supervisor=supervisor, student=student, studSubmissions=studSubmissions, success=success)


@app.route("/UpdateReportStatus", methods=['POST'])
def UpdateReportStatus():
    submissionId = request.form['submissionId']
    updateStatus = request.form['updateStatus']
    remarks = request.form['reportRemark']

    try:
        connection = create_connection()
        cursor = connection.cursor()

        updateSubmission_sql = "UPDATE " + submissionTable + \
            " SET ReportStatus = %s, Remarks = %s WHERE SubmissionId = %s"
        cursor.execute(updateSubmission_sql,
                       (updateStatus, remarks, submissionId))

        flash("Report status has been updated successfully.",
              'update-report-success')

        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()
    return redirect("/supervisorStudentReportView?studentEmail=" + request.form['studentEmail'])


@app.route("/studentAssessment")
def studentAssessment():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    allSupervisedStudents = retrieveStudentBySupervisorId(supervisorId)
    allStudentsDet = {stud[10]: stud for stud in retrieveAllStudDetail()}
    allInternship = {internship[0]: internship[1]
                     for internship in retrieveAllInternship()}

    supervisedStudents = []

    for stud in allSupervisedStudents:
        studDet = allStudentsDet.get(stud[0])
        print(studDet)
        companyName = allInternship.get(stud[0], "Not Secured Yet")
        if studDet:
            student = Student(stud[0], stud[1], stud[2], stud[3], stud[4], stud[5], stud[6], stud[7], studDet[0],
                              studDet[1], studDet[2], studDet[3], studDet[4], studDet[5], studDet[6], studDet[7], studDet[8], studDet[9])
            student.companyName = companyName
            print(student.companyName)
            supervisedStudents.append(student)

    return render_template("studentAssessment.html", supervisor=supervisor, supervisedStudents=supervisedStudents)


@app.route("/supervisorStudentAssessmentForm")
def supervisorStudentAssessmentForm():
    studEmail = request.args.get('studentEmail')
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)
    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])
    
    
    student = retrieveStudByEmail(studEmail)
    studentDet = retrieveStudDetailByEmail(studEmail)
    student = Student(student[0], student[1], student[2], student[3], student[4], student[5], student[6], student[7], studentDet[0],
                      studentDet[1], studentDet[2], studentDet[3], studentDet[4], studentDet[5], studentDet[6], studentDet[7], studentDet[8], studentDet[9])
    student.profilePic = get_object_url(student.profilePic)
    internship = retrieveInternshipByEmail(studEmail)
    if internship != None:
        internship = Internship(internship[0], internship[1], internship[2], internship[3],
                                internship[4], internship[5], internship[6], internship[7], internship[8])
    
    return render_template("supervisorStudentAssessmentForm.html", supervisor=supervisor,  stud=student, internship=internship)

@app.route("/supervisorProfile")
def supervisorProfile():
    supervisorId = session['supervisorId']
    supervisor = retrieveUniSupervisorById(supervisorId)

    supervisor = UniversitySupervisor(
        supervisor[0], supervisor[1], supervisor[2], supervisor[3], supervisor[4])

    success = get_flashed_messages(category_filter=['update-success'])
    if success:
        success = success[0]
    return render_template("supervisorProfile.html", supervisor=supervisor, success=success)


@app.route("/UpdateSupervisorProfile", methods=['POST'])
def UpdateSupervisorProfile():
    supervisorId = session['supervisorId']
    password = request.form['newPassword']
    name = request.form['name']
    contact = request.form['contact']

    if password == "":
        password = request.form['oldPassword']

    try:
        updateSupervisor_sql = "UPDATE " + universitySupervisorTable + \
            " SET Password = %s, Name = %s, ContactNo = %s WHERE StaffId = %s"
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(updateSupervisor_sql,
                       (password, name, contact, supervisorId))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    flash("Your profile has been updated!", 'update-success')

    return redirect("/supervisorProfile")

# --------------------- Supervisor ---------------------------


# --------------------- Admin ---------------------------
@app.route("/AdminLogin", methods=['POST'])
def AdminLogin():
    username = request.form['username']
    password = request.form['password']

    allAdmin = retrieveAllAdmin()

    for admin in allAdmin:
        if admin[1] == username and admin[2] == password:
            session["adminId"] = admin[0]
            return redirect("/adminHome")

    return render_template('adminLogin.html', error="Invalid Username or Password")


@app.route("/adminHome")
def adminDashboard():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    allCompany = retrieveAllComp()
    allCompanyReq = retrieveAllCompReq()
    allTasks = retrieveAllTask()

    pendingCompany = []
    pendingCompanyReq = []

    for company in allCompany:
        if company[10] == "Pending":
            pendingCompany.append(company)

    for companyReq in allCompanyReq:
        if companyReq[3] == "Pending":
            pendingCompanyReq.append(companyReq)

    allCompanyCount = len(allCompany)
    allCompanyReqCount = len(allCompanyReq)
    allPendingCompCount = len(pendingCompany)
    allPendingCompReqCount = len(pendingCompanyReq)
    allTasksCount = len(allTasks)

    return render_template("adminHome.html", admin=admin, allCompanyCount=allCompanyCount,
                           allCompanyReqCount=allCompanyReqCount, allPendingCompCount=allPendingCompCount,
                           allPendingCompReqCount=allPendingCompReqCount, allTasksCount=allTasksCount)


@app.route("/adminCompanyRequest")
def adminCompanyRequest():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break
    compReqList = []
    for compReq in retrieveAllCompReq():
        compReq = CompanyRequest(
            compReq[0], compReq[1], compReq[2], compReq[3], compReq[4], compReq[5])
        compReqList.append(compReq)

    success = get_flashed_messages(category_filter=['req-approved'])
    if success:
        success = success[0]
    reject = get_flashed_messages(category_filter=['req-rejected'])
    if reject:
        reject = reject[0]

    return render_template("adminCompanyRequest.html", admin=admin, compReqs=compReqList, success=success, reject=reject)


@app.route("/UpdateCompReq")
def UpdateCompReq():
    adminId = session['adminId']
    requestId = request.args.get('requestId')
    status = request.args.get('status')

    try:
        connection = create_connection()
        cursor = connection.cursor()

        updateCompReq_sql = "UPDATE " + companyRequestTable + \
            " SET RequestStatus = %s, AdminId = %s WHERE RequestId = %s"
        cursor.execute(updateCompReq_sql, (status, adminId, requestId))
        connection.commit()
        if status == "Approved":
            flash("Company request has been approved", 'req-approved')
        elif status == "Rejected":
            flash("Company request has been rejected", 'req-rejected')

    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/adminCompanyRequest")


@app.route("/adminTaskManage")
def adminTaskManage():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    taskList = []
    for task in retrieveAllTask():
        task = Task(task[0], task[1], task[2], datetime.strftime(
            task[3], '%Y-%m-%d'), task[4], task[5], task[6])

        if task.assignTo == "Diploma and Degree":
            task.diploma = "Y"
            task.degree = "Y"
        else:
            task.diploma = "Y" if "Diploma" in task.assignTo else "N"
            task.degree = "Y" if "Degree" in task.assignTo else "N"

        taskList.append(task)

    success = get_flashed_messages(category_filter=['task-added'])
    if success:
        success = success[0]

    successDelete = get_flashed_messages(category_filter=['task-deleted'])
    if successDelete:
        successDelete = successDelete[0]

    return render_template("adminTaskManage.html", admin=admin, tasks=taskList, successAdd=success, successDelete=successDelete)


@app.route("/adminAddTask")
def adminAddTask():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    return render_template("adminAddTask.html", admin=admin)


@app.route("/adminTaskViewEdit")
def adminTaskViewEdit():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    taskId = request.args.get('taskId')

    task = retrieveTaskById(taskId)
    task = Task(task[0], task[1], task[2], datetime.strftime(
        task[3], '%Y-%m-%d'), task[4], task[5], task[6])
    task.attachmentURL = get_object_url(task.attachmentURL)

    success = get_flashed_messages(category_filter=['task-updated'])
    if success:
        success = success[0]

    return render_template("adminTaskViewEdit.html", admin=admin, task=task, success=success)


@app.route("/UpdateTask", methods=['POST'])
def UpdateTask():

    taskName = request.form['taskTitle']
    taskDueDate = request.form['taskDueDate']
    taskDesc = request.form['taskDesc']
    taskId = request.form['taskId']

    dueDate = datetime.strptime(taskDueDate, '%Y-%m-%d')
    desired_time = time(23, 59, 59)
    taskDueDate = datetime.combine(dueDate.date(), desired_time)

    try:
        updateTaskAttachment_sql = "UPDATE " + taskTable + \
            " SET AttachmentName = %s, AttachmentURL = %s WHERE TaskId = %s"
        updateTask_sql = "UPDATE " + taskTable + \
            " SET TaskName = %s, TaskDescription = %s, DueDate = %s WHERE TaskId = %s"
        connection = create_connection()
        cursor = connection.cursor()

        attachment = request.files['attachment']
        if attachment.filename != '':
            attachmentName = attachment.filename
            attachmentURL = "Attachment/" + taskId + "/" + attachmentName
            uploadToS3(attachment, attachmentURL)
            cursor.execute(updateTaskAttachment_sql, (attachmentName,
                           attachmentURL, taskId))
        cursor.execute(updateTask_sql, (taskName, taskDesc,
                       taskDueDate, taskId))

        connection.commit()
        flash("Task has been updated successfully", 'task-updated')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/adminTaskViewEdit?taskId=" + taskId)


@app.route("/DeleteTask")
def DeleteTask():
    taskId = request.args.get('taskId')
    try:
        connection = create_connection()
        cursor = connection.cursor()
        deleteSubmission_sql = "DELETE FROM " + submissionTable + " WHERE TaskId = %s"
        cursor.execute(deleteSubmission_sql, (taskId,))
        deleteTask_sql = "DELETE FROM " + taskTable + " WHERE TaskId = %s"
        cursor.execute(deleteTask_sql, (taskId,))
        connection.commit()
        flash("Task has been deleted successfully", 'task-deleted')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/adminTaskManage")


@app.route("/adminCompanyManage")
def adminCompanyManage():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    companies = []
    for company in retrieveAllComp():
        company = Company(company[0], company[1], company[2], company[3], company[4], company[5],
                          company[6], company[7], company[8], company[9], company[10], company[11], company[12])
        company.logo = get_object_url(company.logo)
        companies.append(company)

    return render_template("adminCompanyManage.html", admin=admin, companyList=companies)


@app.route("/adminCompanyViewUpdate")
def adminCompanyViewUpdate():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    compId = request.args.get('compId')
    company = retrieveCompById(compId)
    company = Company(company[0], company[1], company[2], company[3], company[4], company[5],
                      company[6], company[7], company[8], company[9], company[10], company[11], company[12])
    company.logo = get_object_url(company.logo)
    print(company.logo)
    company.ssmCert = get_object_url(company.ssmCert)

    personInCharge = retrievePICById(company.picId)
    personInCharge = CompanyPersonnel(
        personInCharge[0], personInCharge[1], personInCharge[2], personInCharge[3], personInCharge[4])

    success = get_flashed_messages(category_filter=['comp-approved'])
    if success:
        success = success[0]

    reject = get_flashed_messages(category_filter=['comp-rejected'])
    if reject:
        reject = reject[0]

    return render_template("adminCompanyViewUpdate.html", admin=admin, company=company, pic=personInCharge, approve=success, reject=reject)


@app.route("/UpdateCompanyRegistration")
def UpdateCompanyRegistration():
    compId = request.args.get('companyId')
    status = request.args.get('companyStatus')

    try:
        connection = create_connection()
        cursor = connection.cursor()

        updateCompany_sql = "UPDATE " + companyTable + \
            " SET CompanyStatus = %s WHERE CompanyId = %s"
        cursor.execute(updateCompany_sql, (status, compId))
        connection.commit()
        if status == "Approved":
            flash("Company registration has been approved", 'comp-approved')
        elif status == "Rejected":
            flash("Company registration has been rejected", 'comp-rejected')

    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/adminCompanyViewUpdate?compId=" + compId)


@app.route("/adminProfile")
def adminProfile():
    adminId = session['adminId']
    allAdmin = retrieveAllAdmin()
    for admin in allAdmin:
        if admin[0] == adminId:
            admin = Admin(admin[0], admin[1], admin[2], admin[3], admin[4])
            break

    success = get_flashed_messages(category_filter=['update-success'])
    if success:
        success = success[0]
    return render_template("adminProfile.html", admin=admin, success=success)


@app.route("/UpdateAdminProfile", methods=['POST'])
def UpdateAdminProfile():
    adminId = session['adminId']
    password = request.form['newPassword']
    name = request.form['name']
    email = request.form['email']

    if password == "":
        password = request.form['oldPassword']

    try:
        updateAdmin_sql = "UPDATE " + adminTable + \
            " SET Password = %s, Name = %s, Email = %s WHERE AdminId = %s"
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute(updateAdmin_sql, (password, name, email, adminId))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    flash("Your profile has been updated!", 'update-success')

    return redirect("/adminProfile")


@app.route("/AddTask", methods=['POST'])
def AddTask():
    # Task Table
    taskTitle = request.form['taskTitle']
    taskDesc = request.form['taskDesc']
    taskDeadline = request.form['taskDueDate']
    dueDate = datetime.strptime(taskDeadline, '%Y-%m-%d')
    desired_time = time(23, 59, 59)
    taskDeadline = datetime.combine(dueDate.date(), desired_time)

    print(taskDeadline)
    # Attachment Table (only 1 file)
    attachment = request.files['attachment']

    allStudents = retrieveAllStud()

    # Get this tasks belongs to which level of students (diploma/degree/both)
    openFor = request.form['assignTo']
    # by default, set these 2 to "N"
    diploma = "N"
    degree = "N"
    assignTo = ""

    if openFor == "diploma":
        diploma = "Y"
        assignTo = "Diploma"
    elif openFor == "degree":
        degree = "Y"
        assignTo = "Degree"
    elif openFor == "diplomaAndDegree":
        diploma = "Y"
        degree = "Y"
        assignTo = "Diploma and Degree"

    try:
        connection = create_connection()
        cursor = connection.cursor()
        # Insert Task
        taskSeqNo = retrieveSeqNoByTblName(taskTable)
        taskId = "TK" + fillLeftZero(4, taskSeqNo)
        insertTask_sql = "INSERT INTO " + \
            taskTable + " VALUES (%s, %s, %s, %s, %s, %s, %s)"
        attachmentName = attachment.filename
        attachmentURL = "Attachment/" + taskId + "/" + attachmentName
        uploadToS3(attachment, attachmentURL)
        cursor.execute(
            insertTask_sql, (taskId, taskTitle, taskDesc, taskDeadline, attachmentName, attachmentURL, assignTo))
        # Update task sequence number and attachment sequence number
        updateTaskSeq_sql = "UPDATE " + sequenceTable + \
            " SET SEQ_NO = SEQ_NO + 1 WHERE TBL_NAME = '" + taskTable + "'"
        cursor.execute(updateTaskSeq_sql)

        # Create Submission for every students that involved in the task
        insertSubmission_sql = "INSERT INTO " + submissionTable + \
            " (SubmissionId, StudentEmail, TaskId) VALUES (%s, %s, %s)"
        submissionSeqNo = retrieveSeqNoByTblName(submissionTable)
        rowCreated = 0
        for stud in allStudents:
            if (diploma == "Y" and stud[1] == "Diploma") or (degree == "Y" and stud[1] == "Bachelor"):
                submissionId = "S" + fillLeftZero(6, submissionSeqNo)
                cursor.execute(insertSubmission_sql,
                               (submissionId, stud[0], taskId))
                submissionSeqNo += 1
                rowCreated += 1
        print("row created: " + str(rowCreated))
        # Update submission sequence number
        updateSubmissionSeq_sql = "UPDATE " + sequenceTable + " SET SEQ_NO = SEQ_NO + " + \
            str(rowCreated) + " WHERE TBL_NAME = '" + submissionTable + "'"
        cursor.execute(updateSubmissionSeq_sql)

        # Commit the transaction
        connection.commit()
        flash("Task has been added successfully and assigned to students", 'task-added')
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return redirect("/adminTaskManage")
# --------------------- Admin ---------------------------


def AddCompRequest():
    # CompanyRequest Table
    # requestId = request.form['requestId']
    companyName = request.form['companyName']
    companyAddr = request.form['companyAddr']
    requestStatus = "Pending"
    # FK studEmail
    # FK adminId

    insertCompRequest_sql = "INSERT INTO " + \
        companyRequestTable + " VALUES (%s, %s, %s, %s)"
    connection = create_connection()
    cursor = connection.cursor()


def submitReport():
    # Submission Table
    # submissionId = request.form['submissionId']
    dateSubmitted = datetime.now()
    report = request.files['report']
    # taskId
    # studEmail

    insertSubmission_sql = "INSERT INTO " + submissionTable + \
        " (SubmissionId, DateSubmitted, Report, TaskId, StudentEmail) VALUES (%s, %s, %s, %s, %s)"
    connection = create_connection()
    cursor = connection.cursor()


def applyJob():
    # InternshipApplication Table
    # applicationId = request.form['applicationId']
    applicationStatus = "Pending"
    applyDate = datetime.now()
    # FK jobId
    # FK studEmail

    insertApplication_sql = "INSERT INTO " + internshipApplicationTable + \
        "(ApplicationId, ApplicationStatus, ApplyDate, JobId, StudentEmail) VALUES (%s, %s, %s, %s, %s)"
    connection = create_connection()
    cursor = connection.cursor()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
