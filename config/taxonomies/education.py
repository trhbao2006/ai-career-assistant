"""Taxonomy và trọng số cho nhóm ngành Giáo dục & Đào tạo (Teacher, Lecturer, Training)."""

EDUCATION_TAXONOMY = {
    "pedagogy_and_instruction": {
        "Curriculum Design": ["curriculum", "curriculum development", "syllabus", "thiết kế chương trình"],
        "Lesson Planning": ["lesson planning", "lesson plans", "instructional design", "soạn giáo án"],
        "Classroom Management": ["classroom management", "behavior management", "quản lý lớp học"],
        "Teaching & Instruction": ["teaching", "instruction", "lecturing", "tutoring", "giảng dạy", "gia sư"],
        "Differentiated Instruction": ["differentiated instruction", "special education", "iep", "giáo dục đặc biệt"],
        "Student Assessment": ["assessment", "grading", "evaluation", "progress monitoring", "đánh giá học sinh", "chấm điểm"],
    },
    "academic_domains": {
        "STEM & Mathematics": ["mathematics", "math", "science", "stem", "toán học"],
        "Languages & Literacy": ["english", "esl", "ielts", "literacy", "reading", "writing", "tiếng anh"],
        "Early Childhood & Elementary": ["early childhood", "elementary", "preschool", "mầm non", "tiểu học"],
        "Academic Research": ["research", "academic", "publications", "nghiên cứu khoa học"],
    },
    "edtech_and_tools": {
        "LMS & E-Learning": ["lms", "blackboard", "canvas", "moodle", "google classroom", "e-learning"],
        "Presentation & Content": ["powerpoint", "canva", "workshops", "training materials", "bài giảng"],
        "Office & Data Tracking": ["excel", "microsoft office", "word", "outlook", "database"],
    },
    "communication_and_mentoring": {
        "Parent & Student Communication": ["parents", "parent communication", "conferences", "tư vấn phụ huynh"],
        "Mentoring & Advising": ["mentoring", "coaching", "advising", "cố vấn học tập"],
        "Leadership & Collaboration": ["leadership", "teamwork", "curriculum committee", "làm việc nhóm"],
    },
}

EDUCATION_WEIGHTS = {
    "pedagogy_and_instruction": 0.45,
    "academic_domains": 0.20,
    "edtech_and_tools": 0.20,
    "communication_and_mentoring": 0.15,
}
assert abs(sum(EDUCATION_WEIGHTS.values()) - 1.0) < 1e-6

EDUCATION_CORE_SKILLS = {
    "pedagogy_and_instruction": ["Curriculum Design", "Lesson Planning", "Classroom Management", "Student Assessment"],
    "academic_domains": ["Languages & Literacy"],
    "edtech_and_tools": ["Office & Data Tracking", "Presentation & Content"],
    "communication_and_mentoring": ["Parent & Student Communication", "Mentoring & Advising"],
}

EDUCATION_TARGET_COUNTS = {
    "pedagogy_and_instruction": 3,
    "academic_domains": 1,
    "edtech_and_tools": 2,
    "communication_and_mentoring": 2,
}

EDUCATION_DOMAIN_TERMS = {
    "curriculum", "syllabus", "lesson", "classroom", "pedagogy", "assessment",
    "grading", "iep", "differentiated", "instruction", "student", "students",
    "teaching", "mentoring", "lms", "e-learning", "workshop", "academic",
    "giáo án", "giảng dạy", "chương trình học", "đánh giá", "lớp học", "học sinh",
}
