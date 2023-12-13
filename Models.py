class Student:
    def __init__(self, studEmail, eduLvl, cohort, programme, tutGrp, latestCgpa, studId, supervisorId, name, nric, gender, ownTransport, healthRemark, personalEmail, termAddr, permAddr, contactNo, profilePic):
        self.studEmail = studEmail
        self.eduLvl = eduLvl
        self.cohort = cohort
        self.programme = programme
        self.tutGrp = tutGrp
        self.latestCgpa = latestCgpa
        self.studId = studId
        self.supervisorId = supervisorId
        self.name = name
        self.nric = nric
        self.gender = gender
        self.ownTransport = ownTransport
        self.healthRemark = healthRemark
        self.personalEmail = personalEmail
        self.termAddr = termAddr
        self.permAddr = permAddr
        self.contactNo = contactNo
        self.profilePic = profilePic
        
class Admin:
    def __init__(self, adminId, username, password, name, email):
        self.adminId = adminId
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        
class UniversitySupervisor:
    def __init__(self, staffId, email, password, name, contact):
        self.staffId = staffId
        self.email = email
        self.password = password
        self.name = name
        self.contact = contact

class Company:
    def __init__(self, companyId, companyName, username, password, otClaim, address, ssmCert, industry, logo, totalStf, companyStatus, website, picId):
        self.companyId = companyId
        self.companyName = companyName
        self.username = username
        self.password = password
        self.otClaim = otClaim
        self.address = address
        self.ssmCert = ssmCert
        self.industry = industry
        self.logo = logo
        self.totalStf = totalStf
        self.companyStatus = companyStatus
        self.website = website
        self.picId = picId

class CompanyPersonnel:
    def __init__(self, picId, name, designation, contactNo, email):
        self.picId = picId
        self.name = name
        self.designation = designation
        self.contactNo = contactNo
        self.email = email

class InternshipJob:
    def __init__(self, jobId, jobTitle, jobDesc, allowance, workingDay, workingHour, diploma, degree, accessoryProvide, accommodation, companyId):
        self.jobId = jobId
        self.jobTitle = jobTitle
        self.jobDesc = jobDesc
        self.allowance = allowance
        self.workingDay = workingDay
        self.workingHour = workingHour
        self.diploma = diploma
        self.degree = degree
        self.accessoryProvide = accessoryProvide
        self.accommodation = accommodation
        self.companyId = companyId
        
        
class InternshipApplication:
    def __init__(self, applicationId, applicationStatus, applyDate, reviewDate, remarks, jobId, studentEmail):
        self.applicationId = applicationId
        self.applicationStatus = applicationStatus
        self.applyDate = applyDate
        self.reviewDate = reviewDate
        self.remarks = remarks
        self.jobId = jobId
        self.studentEmail = studentEmail

class Task:
    def __init__(self, taskId, taskName, taskDesc, dueDate, attachmentName, attachmentURL, assignTo):
        self.taskId = taskId
        self.taskName = taskName
        self.taskDesc = taskDesc
        self.dueDate = dueDate
        self.attachmentName = attachmentName
        self.attachmentURL = attachmentURL
        self.assignTo = assignTo

class Submission:
    # status is the approved/reject by university supervisor
    # same goes to remarks
    # report is the URL
    # Nullable: reportStatus, dateSubmitted, report, remarks
    def __init__(self, submissionId, reportStatus, dateSubmitted, report, remarks, studentEmail, taskId):
        self.submissionId = submissionId
        self.reportStatus = reportStatus
        self.dateSubmitted = dateSubmitted
        self.report = report
        self.remarks = remarks
        self.studentEmail = studentEmail
        self.taskId = taskId

class CompanyRequest:
    # adminId is the admin who approved/reject the request
    # requestStatus is the approved/reject by admin
    # Nullable: adminId
    def __init__(self, requestId, companyName, companyAddress, requestStatus, studentEmail, adminId):
        self.requestId = requestId
        self.companyName = companyName
        self.companyAddress = companyAddress
        self.requestStatus = requestStatus
        self.studentEmail = studentEmail
        self.adminId = adminId
    
# Internship - the student have already secured a placement    
class Internship:
    # companyAcceptanceForm, parentAckForm, indemnityLetter are the URL
    def __init__(self, studentEmail, companyName, companyAddress, monthlyAllowance, companySupervisorName, companySupervisorEmail, companyAcceptanceForm, parentAckForm, indemnityLetter):
        self.studentEmail = studentEmail
        self.companyName = companyName
        self.companyAddress = companyAddress
        self.monthlyAllowance = monthlyAllowance
        self.companySupervisorName = companySupervisorName
        self.companySupervisorEmail = companySupervisorEmail
        self.companyAcceptanceForm = companyAcceptanceForm
        self.parentAckForm = parentAckForm
        self.indemnityLetter = indemnityLetter



