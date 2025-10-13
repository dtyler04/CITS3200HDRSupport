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

### 9. Weekly Digest Email System
* ($15)
* Automated weekly digest emails sent every Monday morning to all verified HDR students
* Collects all messages scheduled for the student's current week in their candidature
* Messages are personalized with student-specific details (name, degree type, location, etc.)
* Uses MailChimp for professional email delivery with HTML templates
* Includes message targeting based on degree code, type, location, and study stage
* Admin dashboard provides scheduler management, manual sending, and preview capabilities
* Background task scheduler handles automatic Monday morning delivery
* Comprehensive error handling and logging for reliable operation

## Weekly Digest System Architecture

### Components:
1. **WeeklyDigestService** (`app/services/weekly_digest_service.py`)
   - Core logic for collecting and personalizing messages
   - Calculates student's current week in candidature
   - Filters messages based on targeting criteria
   - Generates personalized email content

2. **ScheduledTaskManager** (`app/services/scheduled_task_manager.py`)
   - Handles automatic scheduling using the `schedule` library
   - Runs background thread for Monday morning email delivery
   - Provides start/stop controls and status monitoring

3. **MailChimpService** (`app/services/mailchimp_service.py`)
   - Extended with digest email functionality
   - Creates HTML email templates with CSS styling
   - Handles MailChimp campaign creation and sending

4. **Admin Dashboard Integration**
   - New "Weekly Digest" tab in admin interface
   - Real-time scheduler status monitoring
   - Manual digest sending for testing
   - User-specific preview functionality
   - Comprehensive system information display

### Email Targeting Logic:
- **Primary Filter**: Student's current week must match message's `week_released`
- **Degree Code**: Must match student's enrolled degree
- **Optional Targeting**: Messages can specify degree type, location, or study stage
- **Personalization**: Student details dynamically inserted into message content

### Scheduling:
- Automatic delivery every Monday at 9:00 AM
- Only verified users receive digest emails
- Background process continues running independently
- Admin controls for starting/stopping scheduler
- Manual override for immediate sending

## Github Directory Structure
<pre>
CITS3200HDRSupport/
├── .gitignore
├── HowToVenv.md
├── init_enrollment_history.py
├── License
├── README.md
├── requirements.txt
├── run.py
├── SETUP.md
├── style.md
├── test_weekly_digest.py
├── app/
│   ├── __init__.py
│   ├── app.db
│   ├── check.py
│   ├── config.py
│   ├── forms.py
│   ├── models.py
│   ├── routes_admin.py
│   ├── routes_OTP.py
│   ├── routes_unit.py
│   ├── routes_webhook.py
│   ├── routes.py
│   ├── __pycache__/
│   │   ├── __init__.cpython-312.pyc
│   │   ├── check.cpython-312.pyc
│   │   ├── config.cpython-312.pyc
│   │   ├── forms.cpython-312.pyc
│   │   ├── models.cpython-312.pyc
│   │   ├── routes_admin.cpython-312.pyc
│   │   ├── routes_OTP.cpython-312.pyc
│   │   ├── routes_unit.cpython-312.pyc
│   │   └── routes.cpython-312.pyc
│   └── services/
│       ├── emailOTP.py
│       ├── mailchimp_service.py
│       ├── message_personalisation.py
│       ├── scheduled_task_manager.py
│       ├── weekly_digest_service.py
│       └── __pycache__/
│           ├── emailOTP.cpython-312.pyc
│           └── mailchimp_service.cpython-312.pyc
├── logs/
│   └── app.log
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   ├── __pycache__/
│   │   └── env.cpython-312.pyc
│   └── versions/
│       ├── fix_admin_column_name.py
│       └── __pycache__/
│           ├── c411f3e91be1_add_title_to_messages.cpython-312.pyc
│           └── fix_admin_column_name.cpython-312.pyc
├── Sprint_1_Tests/
│   ├── Test_A.py
│   └── Test_C.py
├── static/
│   ├── admin_dashboard.js
│   ├── detectmobilebroswer.js
│   ├── favicon.ico
│   ├── style.css
│   ├── tinymce.js
│   ├── fonts/
│   │   └── SchussSlabPro/
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
│   └── tinymce/
│       ├── CHANGELOG.md
│       └── js/
├── templates/
│   ├── assessment_dates.html
│   ├── base.html
│   ├── login.html
│   ├── manage_users.html
│   ├── profile.html
│   ├── reset_password.html
│   ├── select_message.html
│   ├── signup.html
│   ├── student_dashboard.html
│   ├── update_enrollment.html
│   ├── update_password.html
│   ├── user_stats.html
│   ├── verify_email.html
│   ├── verify_password.html
│   ├── weekly_email.html
│   ├── welcome.html
│   └── admin/
│       ├── _assessments_tab.html
│       ├── _compose_tab.html
│       ├── _digest_tab.html
│       ├── _flashes.html
│       ├── _forms.html
│       ├── _history.html
│       ├── _rights_tab.html
│       ├── _support_content.html
│       ├── _tinyMCE_tab.html
│       └── admin_dashboard.html
├── tests/
│   ├── test_create_user_fr.py
│   ├── test_create_user.py
│   └── __pycache__/
│       ├── test_create_user_fr.cpython-312.pyc
│       └── test_create_user.cpython-312.pyc
</pre>

## Installation and Setup

### Prerequisites
- Python 3.12+
- MailChimp API credentials
- Flask development environment

### Quick Start
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CITS3200HDRSupport
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `app/` directory:
   ```env
   SECRET_KEY=your-secret-key
   MAILCHIMP_API_KEY=your-mailchimp-api-key
   MAILCHIMP_SERVER_PREFIX=your-server-prefix
   DATABASE_URL=sqlite:///app.db
   ```

4. **Initialize the database**
   ```bash
   flask db upgrade
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

### Weekly Digest System Setup

#### 1. MailChimp Configuration
- Obtain MailChimp API key from your MailChimp account
- Set `MAILCHIMP_API_KEY` and `MAILCHIMP_SERVER_PREFIX` in your environment
- Ensure MailChimp account has permission to create campaigns

#### 2. Test the System
Run the test script to verify all components:
```bash
python test_weekly_digest.py
```

#### 3. Admin Dashboard Management
1. Login as an admin user (permission level 1)
2. Navigate to the "Weekly Digest" tab in the admin dashboard
3. Start the scheduler to enable automatic Monday morning emails
4. Use preview functionality to test with real user data

#### 4. Message Creation for Digest
When creating messages in the admin dashboard:
- Set `week_released` to specify which week students should receive the message
- Use targeting fields to filter by degree type, location, or study stage
- Messages are automatically included in weekly digests based on these criteria

#### 5. Scheduler Management
- **Start Scheduler**: Enables automatic Monday 9:00 AM email delivery
- **Stop Scheduler**: Disables automatic delivery
- **Send Now**: Manually trigger digest emails for testing
- **Preview**: Test digest content for specific users and weeks

#### 6. Monitoring and Logs
- Application logs are stored in `logs/app.log`
- Weekly digest operations are logged with detailed information
- Admin dashboard shows real-time scheduler status

### API Endpoints

#### Weekly Digest Management
- `GET /admin/weekly-digest/status` - Get scheduler status
- `POST /admin/weekly-digest/start` - Start the scheduler
- `POST /admin/weekly-digest/stop` - Stop the scheduler
- `POST /admin/weekly-digest/send-now` - Manual digest sending
- `GET /admin/weekly-digest/preview/<user_id>` - Preview digest for user
- `GET /admin/weekly-digest/preview/<user_id>/html` - View digest HTML

#### Student Dashboard
- `GET /student-dashboard` - Main student interface with timeline
- `GET /api/timeline-data` - Student progression data
- `GET /api/assessments` - Assessment dates and details

#### User Management
- `POST /signup` - User registration
- `POST /login` - User authentication
- `POST /admin/change_right` - Modify user permissions

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
