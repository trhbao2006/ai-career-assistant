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
    },
}

def get_skills() -> Dict[str, Dict[str, str]]:   
    alias_map = {}
    for category, skills in backend_skills_tamoxy.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                alias_map[alias.lower()] = (canonical, category)
    return alias_map


if __name__ == "__main__":
    skill_map = get_skills()
    print(f"Tổng số kỹ năng chuẩn hóa: {len(skill_map)}")
    print("5 kỹ năng đầu tiên:", list(skill_map.items())[:5])