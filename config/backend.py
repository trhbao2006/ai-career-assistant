from typing import Dict, List

backend_skills_tamoxy: Dict[str, Dict[str, List[str]]] = {
    "languages": {
        "Python": ["python", "python3"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c-sharp", "csharp"],
        "Go": ["golang", "go"],
        "JavaScript": ["javascript", "js"],
        "TypeScript": ["typescript", "ts"],
        "SQL": ["sql", "t-sql", "pl/sql"],
    },
    "frameworks": {
        "FastAPI": ["fastapi", "fast-api"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot", "spring-boot"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express.js", "expressjs", "express"],
        "NestJS": ["nestjs", "nest.js"],
        ".NET": [".net", "asp.net", ".net core", "dotnet"],
    },
    "databases": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "SQL Server": ["sql server", "mssql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
    },
    "devops_tools": {
        "Git": ["git", "github", "gitlab"],
        "Docker": ["docker", "docker-compose", "dockerfile"],
        "Kubernetes": ["kubernetes", "k8s"],
        "CI/CD": ["ci/cd", "ci-cd", "github actions", "gitlab ci", "jenkins"],
        "Linux": ["linux", "ubuntu", "bash"],
        "Kafka": ["kafka", "apache kafka"],
        "RabbitMQ": ["rabbitmq"],
        "AWS": ["aws", "amazon web services"],
        "Nginx": ["nginx"],
    },
    "concepts": {
        "OOP": ["oop", "object-oriented programming", "lập trình hướng đối tượng"],
        "Data Structures & Algorithms": [
            "data structures",
            "algorithms",
            "dsa",
            "cấu trúc dữ liệu",
            "thuật toán",
        ],
        "RESTful API": ["restful api", "rest api", "restful", "rest apis"],
        "gRPC": ["grpc"],
        "Microservices": ["microservices", "microservice", "micro-services"],
        "Clean Architecture": ["clean architecture"],
        "Design Patterns": ["design patterns", "design pattern"],
        "Unit Testing": ["unit test", "unit testing", "pytest", "junit"],
        "System Design": ["system design", "thiết kế hệ thống"],
        "Agile/Scrum": ["agile", "scrum", "kanban"],
        "Authentication (JWT/OAuth)": ["jwt", "oauth", "oauth2", "authentication", "xác thực"],
    },
}

# Alias chuẩn hóa tên
backend_skills_taxonomy = backend_skills_tamoxy


def get_skills() -> Dict[str, Dict[str, str]]:   
    alias_map = {}
    for category, skills in backend_skills_tamoxy.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                alias_map[alias.lower()] = (canonical, category)
    return alias_map


# Trọng số chấm điểm kỹ năng (40 điểm) theo 3 mô hình công ty
COMPANY_ARCHETYPES = {
    "product": {
        "languages": 0.25,
        "concepts": 0.25,      # Product rất coi trọng nền tảng, OOP, REST, Microservices
        "databases": 0.20,
        "frameworks": 0.15,
        "devops_tools": 0.15,
    },
    "outsourcing": {
        "frameworks": 0.30,    # Outsourcing cần làm được việc ngay với Framework/DB
        "databases": 0.25,
        "languages": 0.20,
        "devops_tools": 0.15,
        "concepts": 0.10,
    },
    "startup": {
        "frameworks": 0.35,    # Startup ưu tiên tốc độ dựng sản phẩm và triển khai
        "databases": 0.25,
        "devops_tools": 0.20,
        "languages": 0.15,
        "concepts": 0.05,
    },
}

# Các kỹ năng cốt lõi (Core/Must-have) cho từng mô hình để báo cáo Skill Gap trọng tâm
ARCHETYPE_CORE_SKILLS = {
    "product": {
        "languages": ["Python", "Java", "Go", "C++"],
        "frameworks": ["FastAPI", "Django", "Spring Boot", "NestJS", "Express.js"],
        "databases": ["PostgreSQL", "MySQL", "Redis"],
        "devops_tools": ["Git", "Docker", "Linux"],
        "concepts": ["OOP", "Data Structures & Algorithms", "RESTful API", "System Design", "Unit Testing"],
    },
    "outsourcing": {
        "languages": ["Java", "C#", "JavaScript", "TypeScript", "Python"],
        "frameworks": ["Spring Boot", ".NET", "Node.js", "Express.js", "NestJS", "Django"],
        "databases": ["MySQL", "PostgreSQL", "SQL Server", "MongoDB"],
        "devops_tools": ["Git", "Docker", "CI/CD"],
        "concepts": ["OOP", "RESTful API", "Agile/Scrum"],
    },
    "startup": {
        "languages": ["JavaScript", "TypeScript", "Python", "Go"],
        "frameworks": ["Node.js", "Express.js", "NestJS", "FastAPI"],
        "databases": ["PostgreSQL", "MongoDB", "Redis"],
        "devops_tools": ["Git", "Docker", "CI/CD", "AWS", "Nginx"],
        "concepts": ["RESTful API", "Authentication (JWT/OAuth)"],
    },
}

# Động từ hành động mạnh (Action Verbs) chứng minh năng lực thực chiến
ACTION_VERBS = [
    # Tiếng Anh
    "built", "developed", "designed", "implemented", "optimized", "architected",
    "integrated", "deployed", "refactored", "automated", "created", "reduced",
    "improved", "scaled", "configured", "maintained", "engineered", "migrated",
    # Tiếng Việt
    "xây dựng", "phát triển", "thiết kế", "triển khai", "tối ưu", "tích hợp",
    "tự động hóa", "cải thiện", "nâng cấp", "cấu hình", "bảo trì", "rút ngắn", "giảm"
]
