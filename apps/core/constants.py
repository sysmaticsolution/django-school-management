"""
Indian-specific constants for School Management System.
"""

# Indian States and Union Territories
INDIAN_STATES = [
    ('AN', 'Andaman and Nicobar Islands'),
    ('AP', 'Andhra Pradesh'),
    ('AR', 'Arunachal Pradesh'),
    ('AS', 'Assam'),
    ('BR', 'Bihar'),
    ('CH', 'Chandigarh'),
    ('CT', 'Chhattisgarh'),
    ('DL', 'Delhi'),
    ('DN', 'Dadra and Nagar Haveli and Daman & Diu'),
    ('GA', 'Goa'),
    ('GJ', 'Gujarat'),
    ('HR', 'Haryana'),
    ('HP', 'Himachal Pradesh'),
    ('JK', 'Jammu and Kashmir'),
    ('JH', 'Jharkhand'),
    ('KA', 'Karnataka'),
    ('KL', 'Kerala'),
    ('LA', 'Ladakh'),
    ('LD', 'Lakshadweep'),
    ('MP', 'Madhya Pradesh'),
    ('MH', 'Maharashtra'),
    ('MN', 'Manipur'),
    ('ML', 'Meghalaya'),
    ('MZ', 'Mizoram'),
    ('NL', 'Nagaland'),
    ('OR', 'Odisha'),
    ('PY', 'Puducherry'),
    ('PB', 'Punjab'),
    ('RJ', 'Rajasthan'),
    ('SK', 'Sikkim'),
    ('TN', 'Tamil Nadu'),
    ('TG', 'Telangana'),
    ('TR', 'Tripura'),
    ('UP', 'Uttar Pradesh'),
    ('UK', 'Uttarakhand'),
    ('WB', 'West Bengal'),
]

# Indian Board Types
BOARD_TYPES = [
    ('cbse', 'CBSE - Central Board of Secondary Education'),
    ('icse', 'ICSE - Indian Certificate of Secondary Education'),
    ('state', 'State Board'),
    ('ib', 'IB - International Baccalaureate'),
    ('igcse', 'IGCSE - Cambridge'),
]

# CBSE Grading System
CBSE_GRADES = [
    ('A1', 'A1 (91-100)'),
    ('A2', 'A2 (81-90)'),
    ('B1', 'B1 (71-80)'),
    ('B2', 'B2 (61-70)'),
    ('C1', 'C1 (51-60)'),
    ('C2', 'C2 (41-50)'),
    ('D', 'D (33-40)'),
    ('E', 'E (Below 33)'),
]

# Category/Reservation
CATEGORIES = [
    ('general', 'General'),
    ('obc', 'OBC (Other Backward Class)'),
    ('sc', 'SC (Scheduled Caste)'),
    ('st', 'ST (Scheduled Tribe)'),
    ('ews', 'EWS (Economically Weaker Section)'),
]

# Blood Groups
BLOOD_GROUPS = [
    ('A+', 'A Positive'),
    ('A-', 'A Negative'),
    ('B+', 'B Positive'),
    ('B-', 'B Negative'),
    ('AB+', 'AB Positive'),
    ('AB-', 'AB Negative'),
    ('O+', 'O Positive'),
    ('O-', 'O Negative'),
]

# Gender
GENDERS = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Common Indian Religions
RELIGIONS = [
    ('hinduism', 'Hinduism'),
    ('islam', 'Islam'),
    ('christianity', 'Christianity'),
    ('sikhism', 'Sikhism'),
    ('buddhism', 'Buddhism'),
    ('jainism', 'Jainism'),
    ('other', 'Other'),
]

# Fee Types
FEE_TYPES = [
    ('admission', 'Admission Fee'),
    ('tuition', 'Tuition Fee'),
    ('exam', 'Examination Fee'),
    ('transport', 'Transport Fee'),
    ('hostel', 'Hostel Fee'),
    ('library', 'Library Fee'),
    ('lab', 'Laboratory Fee'),
    ('sports', 'Sports Fee'),
    ('computer', 'Computer Fee'),
    ('annual', 'Annual Charges'),
    ('development', 'Development Fee'),
    ('misc', 'Miscellaneous'),
]

# Attendance Status
ATTENDANCE_STATUS = [
    ('present', 'Present'),
    ('absent', 'Absent'),
    ('late', 'Late'),
    ('half_day', 'Half Day'),
    ('leave', 'On Leave'),
]
