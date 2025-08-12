def personalised_message_reminder_test():
    student_info = {
        'name': 'John Doe',
        'student_number': '123456789',
        'enrolment_date': '01/01/2025',
        'degree_type': 'PhD',
        'enrolment_status': 'full-time',
        'annual_leave_taken': False,
        'support_needs': "Physical Wellbeing, Mental Stability Support"
    }

    custom_message = generate_personalised_email(
        template_ref = 'First-year Milestone',
        student_info = student_info
    )

    assert 'John' in custom_message.content
    assert 'First-year Milstone of Candidature' in custom_message.content
    assert '14/08/2025' in custom_message.content