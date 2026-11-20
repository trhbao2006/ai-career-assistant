from typing import Dict, List, Tuple

backend_skills_tamoxy: Dict[str, Dict[str, List[str]]] = {
    # ------------------------------------------------------------------ #
    "languages": {
        "Python": ["python", "python3"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c-sharp", "csharp"],
        "Go": ["golang", "go"],
        "JavaScript": ["javascript", "js"],
        "TypeScript": ["typescript", "ts"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        # --- BỔ SUNG ---
        "PHP": ["php", "php7", "php8"],
        "Kotlin": ["kotlin"],
        "Ruby": ["ruby"],
        "Rust": ["rust"],
        "Scala": ["scala"],
    },
    # ------------------------------------------------------------------ #
    "frameworks": {
        "FastAPI": ["fastapi", "fast-api"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot", "spring-boot"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express.js", "expressjs", "express"],
        "NestJS": ["nestjs", "nest.js"],
        ".NET": [".net", "asp.net", ".net core", "dotnet"],
        # --- BỔ SUNG: PHP (rất phổ biến ở outsourcing/startup VN) ---
        "Laravel": ["laravel", "lumen"],
        "Symfony": ["symfony"],
        "CodeIgniter": ["codeigniter", "code igniter"],
        # --- BỔ SUNG: Java ecosystem ---
        "Spring Framework": ["spring framework", "spring mvc", "spring"],
        "Spring Cloud": ["spring cloud"],
        "Spring Security": ["spring security"],
        "Hibernate/JPA": ["hibernate", "jpa", "spring data jpa"],
        "MyBatis": ["mybatis", "my batis"],  # nhiều dự án outsourcing Nhật
        # --- BỔ SUNG: các framework khác ---
        "Ruby on Rails": ["ruby on rails", "rails", "ror"],
        "Go Web Frameworks": ["gin", "gin-gonic", "echo", "fiber", "beego"],
        "Entity Framework": ["entity framework", "ef core", "efcore"],
        "SQLAlchemy": ["sqlalchemy"],
        "TypeORM/Prisma/Sequelize": ["typeorm", "prisma", "sequelize", "mongoose"],
        "GraphQL": ["graphql", "apollo server"],
        "WebSocket/Socket.IO": ["websocket", "websockets", "socket.io", "socketio"],
    },
    # ------------------------------------------------------------------ #
    "databases": {
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "SQL Server": ["sql server", "mssql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
        # --- BỔ SUNG ---
        "Oracle": ["oracle", "oracle db", "oracle database"],  # ngân hàng, tài chính, outsourcing
        "MariaDB": ["mariadb"],
        "Cassandra": ["cassandra", "apache cassandra"],
        "DynamoDB": ["dynamodb"],
        "Firebase/Firestore": ["firebase", "firestore"],
        "ClickHouse": ["clickhouse"],
        "Neo4j": ["neo4j"],
        "Memcached": ["memcached"],
    },
    # ------------------------------------------------------------------ #
    "devops_tools": {
        "Git": ["git", "github", "gitlab", "bitbucket"],
        "Docker": ["docker", "docker-compose", "dockerfile"],
        "Kubernetes": ["kubernetes", "k8s"],
        "CI/CD": ["ci/cd", "ci-cd", "github actions", "gitlab ci", "jenkins", "circleci", "argocd"],
        "Linux": ["linux", "ubuntu", "bash", "centos", "shell script"],
        "Nginx": ["nginx", "apache http", "haproxy"],
        # --- BỔ SUNG ---
        "Terraform/IaC": ["terraform", "ansible", "infrastructure as code", "iac"],
        "Helm": ["helm"],
        "Maven/Gradle": ["maven", "gradle"],
    },
    #Cloud (tách AWS khỏi devops_tools, thêm GCP/Azure/cloud nội địa)
    "cloud": {
        "AWS": ["aws", "amazon web services", "ec2", "s3", "aws lambda", "rds", "ecs", "eks"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Azure": ["azure", "microsoft azure"],
        "Cloud VN": ["viettel cloud", "fpt cloud", "vnpt cloud", "vng cloud", "cmc cloud"],
    },
    #  NHÁNH MỚI: Message Queue / Streaming (tách Kafka, RabbitMQ ra khỏi devops_tools)
    "messaging": {
        "Kafka": ["kafka", "apache kafka"],
        "RabbitMQ": ["rabbitmq", "rabbit mq"],
        "ActiveMQ": ["activemq", "active mq"],
        "AWS SQS/SNS": ["sqs", "sns", "amazon sqs"],
        "Celery": ["celery"],
        "NATS/Pulsar": ["nats", "pulsar"],
        "Message Queue": ["message queue", "message broker", "hàng đợi"],
    },
    # ------------------------------------------------------------------ #
    # NHÁNH MỚI: Monitoring / Observability
    "observability": {
        "ELK Stack": ["elk", "elk stack", "logstash", "kibana", "elastic stack"],
        "Prometheus/Grafana": ["prometheus", "grafana"],
        "Sentry": ["sentry"],
        "Datadog/NewRelic": ["datadog", "new relic", "newrelic"],
        "OpenTelemetry/Tracing": ["opentelemetry", "jaeger", "zipkin", "distributed tracing"],
        "Logging & Monitoring": ["logging", "monitoring", "giám sát", "server log", "log server", "ghi log"],
    },
    # ------------------------------------------------------------------ #
    # NHÁNH MỚI: Bảo mật
    "security": {
        "OWASP/Web Security": ["owasp", "owasp top 10", "sql injection", "xss", "csrf", "bảo mật"],
        "RBAC/SSO": ["rbac", "sso", "keycloak", "saml", "ldap"],
        "Encryption/TLS": ["ssl", "tls", "https", "encryption", "mã hóa"],
    },
    # ------------------------------------------------------------------ #
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
        # --- BỔ SUNG ---
        "Database Design & Optimization": [
            "database design", "query optimization", "indexing", "database optimization",
            "thiết kế cơ sở dữ liệu", "thiết kế csdl", "tối ưu truy vấn", "tối ưu query",
        ],
        "Caching": ["caching", "cache", "cdn"],
        "Concurrency/Multithreading": [
            "multithreading", "multi-threading", "concurrency", "asyncio",
            "đa luồng", "bất đồng bộ", "async",
        ],
        "High Availability & Scalability": [
            "high availability", "scalability", "load balancing", "high traffic",
            "high load", "horizontal scaling", "tải cao", "khả năng mở rộng",
        ],
        "Event-Driven Architecture": ["event-driven", "event driven", "event sourcing", "cqrs"],
        "DDD": ["ddd", "domain-driven design", "domain driven design"],
        "SOLID": ["solid principles", "solid principle", "nguyên lý solid", "s.o.l.i.d"],
        "TDD/Integration Testing": ["tdd", "test-driven", "integration test", "integration testing", "e2e"],
        "API Documentation & Tools": ["swagger", "openapi", "postman", "api documentation"],
        "Code Review & Git Flow": ["code review", "git flow", "gitflow", "pull request"],
        "Payment Integration": [
            "payment gateway", "payment integration", "vnpay", "momo", "zalopay",
            "stripe", "paypal", "thanh toán", "cổng thanh toán",
        ],
        "Third-party API Integration": [
            "third-party api", "api integration", "webhook", "tích hợp api", "tích hợp hệ thống",
        ],
    },
}

# Alias chuẩn hóa tên
backend_skills_taxonomy = backend_skills_tamoxy


def get_skills() -> Dict[str, Tuple[str, str]]:
    """Trả về alias_map: alias (lowercase) -> (canonical, category).

    Lưu ý khi match: các alias ngắn/dễ nhiễu ("go", "js", "ts", "git", "log",
    "echo", "gin", "rust", "ruby", "async", "solid", "express", "spring"...)
    nên match theo ranh giới từ (regex lookaround), không dùng `in` trên chuỗi,
    và ưu tiên alias dài hơn trước ("spring boot" > "spring").
    """
    alias_map: Dict[str, Tuple[str, str]] = {}
    for category, skills in backend_skills_tamoxy.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                alias_map[alias.lower()] = (canonical, category)
    return alias_map


# Trọng số chấm điểm kỹ năng (40 điểm) theo 3 mô hình công ty
# Mỗi mô hình có tổng trọng số = 1.0
COMPANY_ARCHETYPES = {
    "product": {
        "languages": 0.20,
        "concepts": 0.20,      # Product rất coi trọng nền tảng, OOP, REST, Microservices
        "databases": 0.15,
        "frameworks": 0.12,
        "devops_tools": 0.10,
        "messaging": 0.08,     # Kafka/RabbitMQ thường xuất hiện ở JD product/fintech
        "cloud": 0.07,
        "observability": 0.04,
        "security": 0.04,
    },
    "outsourcing": {
        "frameworks": 0.27,    # Outsourcing cần làm được việc ngay với Framework/DB
        "databases": 0.22,
        "languages": 0.18,
        "devops_tools": 0.12,
        "concepts": 0.09,
        "cloud": 0.05,
        "messaging": 0.03,
        "security": 0.02,
        "observability": 0.02,
    },
    "startup": {
        "frameworks": 0.30,    # Startup ưu tiên tốc độ dựng sản phẩm và triển khai
        "databases": 0.20,
        "devops_tools": 0.15,
        "languages": 0.13,
        "cloud": 0.10,         # Startup thường deploy thẳng lên AWS/GCP
        "concepts": 0.05,
        "messaging": 0.03,
        "security": 0.02,
        "observability": 0.02,
    },
}

# Kiểm tra tổng trọng số để tránh lỗi khi chỉnh sửa về sau
for _name, _weights in COMPANY_ARCHETYPES.items():
    assert abs(sum(_weights.values()) - 1.0) < 1e-9, f"Tổng trọng số '{_name}' phải bằng 1.0"
    assert set(_weights) <= set(backend_skills_tamoxy), f"'{_name}' có category không tồn tại"

# Các kỹ năng cốt lõi (Core/Must-have) cho từng mô hình để báo cáo Skill Gap trọng tâm
ARCHETYPE_CORE_SKILLS = {
    "product": {
        "languages": ["Python", "Java", "Go", "C++"],
        "frameworks": ["FastAPI", "Django", "Spring Boot", "NestJS", "Express.js"],
        "databases": ["PostgreSQL", "MySQL", "Redis"],
        "devops_tools": ["Git", "Docker", "Linux"],
        "cloud": ["AWS"],
        "messaging": ["Kafka", "RabbitMQ"],
        "observability": ["ELK Stack", "Prometheus/Grafana"],
        "security": ["OWASP/Web Security"],
        "concepts": [
            "OOP", "Data Structures & Algorithms", "RESTful API", "System Design",
            "Unit Testing", "Microservices", "Caching", "Database Design & Optimization",
        ],
    },
    "outsourcing": {
        "languages": ["Java", "C#", "JavaScript", "TypeScript", "Python", "PHP"],
        "frameworks": [
            "Spring Boot", ".NET", "Node.js", "Express.js", "NestJS", "Django",
            "Laravel", "Hibernate/JPA",
        ],
        "databases": ["MySQL", "PostgreSQL", "SQL Server", "MongoDB", "Oracle"],
        "devops_tools": ["Git", "Docker", "CI/CD"],
        "cloud": ["AWS"],
        "messaging": [],
        "observability": [],
        "security": [],
        "concepts": ["OOP", "RESTful API", "Agile/Scrum", "API Documentation & Tools"],
    },
    "startup": {
        "languages": ["JavaScript", "TypeScript", "Python", "Go", "PHP"],
        "frameworks": ["Node.js", "Express.js", "NestJS", "FastAPI", "Laravel"],
        "databases": ["PostgreSQL", "MongoDB", "Redis"],
        "devops_tools": ["Git", "Docker", "CI/CD", "Nginx"],
        "cloud": ["AWS", "GCP"],
        "messaging": [],
        "observability": [],
        "security": [],
        "concepts": ["RESTful API", "Authentication (JWT/OAuth)", "Payment Integration"],
    },
}

# Động từ hành động mạnh (Action Verbs) chứng minh năng lực thực chiến
ACTION_VERBS = [
    # Tiếng Anh
    "built", "developed", "designed", "implemented", "optimized", "architected",
    "integrated", "deployed", "refactored", "automated", "created", "reduced",
    "improved", "scaled", "configured", "maintained", "engineered", "migrated",
    # --- BỔ SUNG (EN) ---
    "led", "launched", "delivered", "monitored", "debugged", "tested",
    "documented", "secured", "owned", "mentored",
    # Tiếng Việt
    "xây dựng", "phát triển", "thiết kế", "triển khai", "tối ưu", "tích hợp",
    "tự động hóa", "cải thiện", "nâng cấp", "cấu hình", "bảo trì", "rút ngắn", "giảm",
    # --- BỔ SUNG (VI) ---
    "viết", "lập trình", "vận hành", "giám sát", "kiểm thử", "di chuyển dữ liệu",
    "tái cấu trúc", "mở rộng", "dẫn dắt", "chịu trách nhiệm", "đảm nhận", "tăng",
]