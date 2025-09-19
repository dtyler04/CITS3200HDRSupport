# Project: HDR Support at Time of Need
University of Western Australia (UWA) Professional Computing (CITS3200) Project

## Overview
The HDR Support at Time of Need project centres around developing an enriched and personal communication application for Higher Degree by Research (HDR) students at the University of Western Australia. The application will provide HDR students with custom reminders, messages and resources aimed to support their study based on their individual circumstances and needs.

## Problem
Not all HDR students are the same represent a diverse group of individuals with differing needs. Currently, HDR students recieve generic reminders and messages for support services, available resources and research training events. The areas in which HDR students differ include...
* Location (online or on-campus)
* Degree Type (Masters or PhD)
* Support Needs (personal wellbeing and/or academic support)
* Enrollment Status (part-time or full-time)
* Stage of candidature

Due to messages and reminders not being suited to the specific needs of each HDR student, students recieve irrelevant information or may miss out on information specific to their requirements due to the mass of irrelevant information.

## Goals
* Develop a communications application for HDR students that is more personalised.
* Reduce the overload of information through delivering relevant and timely messages/reminders.
* Enhance HDR student engagament with available support resources that match their needs.

## Target Users
* Primary Users: HDR students.
* Secondary Users: University of Western Australia (UWA) Administration and support staff for HDR students.
    
## Key Features of Application
### 1. Personalised System for Communication
* ($40)
* Personalised reminders and messages need to be tailored to each students needs and circumstances.
* The messages need to be able to dynamically adapt to the parameters the student provides to the system. (degree type, support needs, enrollment status, stage of candidature and location).
* Messages and reminders should take into account and reflect based on student status. (i.e. If a student is part time then they will receive one message for every two weeks (double duration of full-time). In the case where a student takes annual leave then the system should suspend all messages and reminders until the end of that duration, however, if a student decides to suspend their degree then messages and reminders will still be pushed by the system to the user).
        
### 2. Management Portal for Students
* Profile Creation and User Registration (Seperate system from StudentConnect, so students will need to create brand new login details).
* Profile Editing: Students will need to manually update their enrollment status throughout their candidature.
* Reminder/Message History: past messages/reminders will be in a list or calander format for the user to be aware in a visually engaging way.
        
### 3. Administartion Dashboard
* ($30)
* Content Management System (CMS): this allows administrators to create and update message content. This will include both a text editor and access to a file explorer to attach any relevent files.
* Analytics: displays metrics such as total number of students, number of logged in users, number of clicks on certain pages, most frequently visited wellbeing resources.
* Student List: a list of students with information on each student can be accessed by administators.
        
### 4. Past and New Message View
* ($10)
* User has the ability to view new messages and reminders or previous ones.
* Messages and reminders will be sorted by date and the user can choose to view the messages and reminders by the day, the week or the month.
* Messages and Reminders will be displayed in either a list view or a calander view based on user preference.

### 5. Email-Based Reminder/Message System
* ($5)
* All messages and remidners will be sent through an MailChimp which is out bulk email delivery service of choice.

### 6. Automatic Message/Reminder Scheduling
* ($5)
* Administrators will have the ability to schedule messages and reminders for future dates.
* The scheduling logic will happen on the server Flask where it will laise with MailChimp to deliver messages and reminders according to the specified dates.

### 7. Progression Status Bar/Timeline
* ($5)
* This is the progression status of an HDR students progress through their candidature.
* This will take the form of a circular progress wheel or a horizontal progress bar.

### 8. User Statistics Dashboard Showing Utilisation Through Visits
* ($5)
* This is a page within the administrator dashboard which has useful insights such as page visits, active users, login times and button clicks. This will allow HDR support staff to better cater messages and relevent support infomration to students based on their needs.

## Github Directory Structure
<pre>
CITS3200HDRSupport
├── .gitignore
├── HowToVenv.md
├── License
├── README.md
├── Sprint_1_Tests
│   ├── Test_A.py
│   └── Test_C.py
├── app
│   ├── .env
│   ├── __init__.py
│   ├── check.py
│   ├── config.py
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   ├── routes_OTP.py
│   ├── routes_admin.py
│   └── services
│       ├── __pycache__
│       ├── emailOTP.py
│       └── mailchimp_service.py
├── instance
├── requirements.txt
├── static
│   ├── .gitkeep
│   ├── email_editor.css
│   ├── email_editor.js
│   ├── favicon.ico
│   ├── fonts
│   │   └── SchussSlabPro
│   │       ├── SchussSlabPro-Bold.eot
│   │       ├── SchussSlabPro-Bold.ttf
│   │       ├── SchussSlabPro-Bold.woff
│   │       ├── SchussSlabPro-Bold.woff2
│   │       ├── SchussSlabPro-BoldItalic.eot
│   │       ├── SchussSlabPro-BoldItalic.ttf
│   │       ├── SchussSlabPro-BoldItalic.woff
│   │       ├── SchussSlabPro-BoldItalic.woff2
│   │       ├── SchussSlabPro-Heavy.eot
│   │       ├── SchussSlabPro-Heavy.ttf
│   │       ├── SchussSlabPro-Heavy.woff
│   │       ├── SchussSlabPro-Heavy.woff2
│   │       ├── SchussSlabPro-HeavyItalic.eot
│   │       ├── SchussSlabPro-HeavyItalic.ttf
│   │       ├── SchussSlabPro-HeavyItalic.woff
│   │       ├── SchussSlabPro-HeavyItalic.woff2
│   │       ├── SchussSlabPro-Italic.eot
│   │       ├── SchussSlabPro-Italic.ttf
│   │       ├── SchussSlabPro-Italic.woff
│   │       ├── SchussSlabPro-Italic.woff2
│   │       ├── SchussSlabPro-Light.eot
│   │       ├── SchussSlabPro-Light.ttf
│   │       ├── SchussSlabPro-Light.woff
│   │       ├── SchussSlabPro-Light.woff2
│   │       ├── SchussSlabPro-LightItalic.eot
│   │       ├── SchussSlabPro-LightItalic.ttf
│   │       ├── SchussSlabPro-LightItalic.woff
│   │       ├── SchussSlabPro-LightItalic.woff2
│   │       ├── SchussSlabPro-Medium.eot
│   │       ├── SchussSlabPro-Medium.ttf
│   │       ├── SchussSlabPro-Medium.woff
│   │       ├── SchussSlabPro-Medium.woff2
│   │       ├── SchussSlabPro-MediumItalic.eot
│   │       ├── SchussSlabPro-MediumItalic.ttf
│   │       ├── SchussSlabPro-MediumItalic.woff
│   │       ├── SchussSlabPro-MediumItalic.woff2
│   │       ├── SchussSlabPro-Regular.eot
│   │       ├── SchussSlabPro-Regular.ttf
│   │       ├── SchussSlabPro-Regular.woff
│   │       ├── SchussSlabPro-Regular.woff2
│   │       └── stylesheet.css
│   └── style.css
├── style.md
├── templates
│   ├── admin_dashboard.html
│   ├── base.html
│   ├── email_editor.html
│   ├── login.html
│   ├── select_message.html
│   ├── signup.html
│   ├── student_dashboard.html
│   ├── weekly_email.html
│   └── welcome.html
├── tests
│   └── .gitkeep
</pre>

## Client
 * Name: Jo Edmonston
 * Email: joanne.edmondston@uwa.edu.au

## Google Drive File System
### The GDrive used for administration can be found here: https://drive.google.com/drive/folders/1zuWFkEv78LdiFtAIFUiUnC4dWI558r5X 
* This link should be removed before the Repo is made Public

## Development Team
* Jordan Joseph (23332309@student.uwa.edu.au)
* Tom Tran (23459091@student.uwa.edu.au)
* Darcy Tyler (23390948@student.uwa.edu.au)
* Ganesh Chinnasamy (23970776@student.uwa.edu.au)
* Nate Htut (23484347@student.uwa.edu.au)
* Brandon Fong (24339304@student.uwa.edu.au)

## License and Intellectual Property
This is an open-source project.


**Last Updated** 20 Aug 2025
