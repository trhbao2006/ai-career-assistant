"""Taxonomy thống nhất cho nhóm ngành Công nghệ Thông tin (Software, Data, Cloud/DevOps, Systems/Support)."""

from typing import Dict, List, Tuple

IT_GENERAL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
    "software_and_data": {
        # Ngôn ngữ lập trình
        "Python": ["python", "python3"],
        "Java": ["java"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "c-sharp", "csharp"],
        "Go": ["golang", "go"],
        "JavaScript": ["javascript", "js"],
        "TypeScript": ["typescript", "ts"],
        "SQL": ["sql", "t-sql", "pl/sql"],
        "PHP": ["php", "php7", "php8"],
        "Kotlin": ["kotlin"],
        "Ruby": ["ruby"],
        "Rust": ["rust"],
        "Scala": ["scala"],
        # Frameworks (Backend, Frontend, Mobile)
        "FastAPI": ["fastapi", "fast-api"],
        "Django": ["django", "django rest framework", "drf"],
        "Flask": ["flask"],
        "Spring Boot": ["spring boot", "springboot", "spring-boot"],
        "Node.js": ["node.js", "nodejs", "node js"],
        "Express.js": ["express.js", "expressjs", "express"],
        "NestJS": ["nestjs", "nest.js"],
        ".NET": [".net", "asp.net", ".net core", "dotnet"],
        "Laravel": ["laravel", "lumen"],
        "Symfony": ["symfony"],
        "CodeIgniter": ["codeigniter", "code igniter"],
        "Spring Framework": ["spring framework", "spring mvc", "spring"],
        "Spring Cloud": ["spring cloud"],
        "Spring Security": ["spring security"],
        "Hibernate/JPA": ["hibernate", "jpa", "spring data jpa"],
        "MyBatis": ["mybatis", "my batis"],
        "Ruby on Rails": ["ruby on rails", "rails", "ror"],
        "Go Web Frameworks": ["gin", "gin-gonic", "echo", "fiber", "beego"],
        "Entity Framework": ["entity framework", "ef core", "efcore"],
        "SQLAlchemy": ["sqlalchemy"],
        "TypeORM/Prisma/Sequelize": ["typeorm", "prisma", "sequelize", "mongoose"],
        "GraphQL": ["graphql", "apollo server"],
        "WebSocket/Socket.IO": ["websocket", "websockets", "socket.io", "socketio"],
        "React": ["react", "reactjs", "react.js", "react native"],
        "Angular": ["angular", "angularjs"],
        "Vue.js": ["vue", "vue.js", "vuejs", "nuxt", "nuxt.js"],
        "Next.js": ["next.js", "nextjs"],
        "Flutter": ["flutter", "dart"],
        # Cơ sở dữ liệu & Data/BI
        "PostgreSQL": ["postgresql", "postgres"],
        "MySQL": ["mysql"],
        "SQL Server": ["sql server", "mssql"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
        "Oracle": ["oracle", "oracle db", "oracle database"],
        "MariaDB": ["mariadb"],
        "Cassandra": ["cassandra", "apache cassandra"],
        "DynamoDB": ["dynamodb"],
        "Firebase/Firestore": ["firebase", "firestore"],
        "ClickHouse": ["clickhouse"],
        "Neo4j": ["neo4j"],
        "Memcached": ["memcached"],
        "Data & BI": ["data analysis", "power bi", "tableau", "etl", "data warehouse", "pandas", "numpy"],
    },
    "engineering_and_concepts": {
        "OOP": ["oop", "object-oriented programming", "lập trình hướng đối tượng"],
        "Data Structures & Algorithms": [
            "data structures", "algorithms", "dsa", "cấu trúc dữ liệu", "thuật toán",
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
        "QA & Software Testing": [
            "qa", "qc", "manual testing", "automation testing", "selenium", "cypress", "playwright", "test case",
        ],
        "API Documentation & Tools": ["swagger", "openapi", "postman", "api documentation"],
        "Code Review & Git Flow": ["code review", "git flow", "gitflow", "pull request"],
        "Payment Integration": [
            "payment gateway", "payment integration", "vnpay", "momo", "zalopay",
            "stripe", "paypal", "thanh toán", "cổng thanh toán",
        ],
        "Third-party API Integration": [
            "third-party api", "api integration", "webhook", "tích hợp api", "tích hợp hệ thống",
        ],
        "IT Project & Documentation": [
            "project management", "documentation", "sdcl", "sdlc", "requirements", "user story", "jira",
        ],
    },
    "cloud_devops_security": {
        "Git": ["git", "github", "gitlab", "bitbucket"],
        "Docker": ["docker", "docker-compose", "dockerfile"],
        "Kubernetes": ["kubernetes", "k8s"],
        "CI/CD": ["ci/cd", "ci-cd", "github actions", "gitlab ci", "jenkins", "circleci", "argocd"],
        "Nginx": ["nginx", "apache http", "haproxy"],
        "Terraform/IaC": ["terraform", "ansible", "infrastructure as code", "iac"],
        "Helm": ["helm"],
        "Maven/Gradle": ["maven", "gradle"],
        "AWS": ["aws", "amazon web services", "ec2", "s3", "aws lambda", "rds", "ecs", "eks"],
        "GCP": ["gcp", "google cloud", "google cloud platform"],
        "Azure": ["azure", "microsoft azure"],
        "Cloud VN": ["viettel cloud", "fpt cloud", "vnpt cloud", "vng cloud", "cmc cloud"],
        "Kafka": ["kafka", "apache kafka"],
        "RabbitMQ": ["rabbitmq", "rabbit mq"],
        "ActiveMQ": ["activemq", "active mq"],
        "AWS SQS/SNS": ["sqs", "sns", "amazon sqs"],
        "Celery": ["celery"],
        "NATS/Pulsar": ["nats", "pulsar"],
        "Message Queue": ["message queue", "message broker", "hàng đợi"],
        "ELK Stack": ["elk", "elk stack", "logstash", "kibana", "elastic stack"],
        "Prometheus/Grafana": ["prometheus", "grafana"],
        "Sentry": ["sentry"],
        "Datadog/NewRelic": ["datadog", "new relic", "newrelic"],
        "OpenTelemetry/Tracing": ["opentelemetry", "jaeger", "zipkin", "distributed tracing"],
        "Logging & Monitoring": ["logging", "monitoring", "giám sát", "server log", "log server", "ghi log"],
        "OWASP/Web Security": ["owasp", "owasp top 10", "sql injection", "xss", "csrf", "bảo mật"],
        "RBAC/SSO": ["rbac", "sso", "keycloak", "saml", "ldap"],
        "Encryption/TLS": ["ssl", "tls", "https", "encryption", "mã hóa"],
        "Cybersecurity & Backup": [
            "security", "cybersecurity", "information assurance", "firewall", "disaster recovery", "backup",
        ],
    },
    "systems_and_support": {
        "Active Directory & Windows": ["active directory", "windows server", "windows 7", "windows 10", "group policy"],
        "Linux & Unix": ["linux", "ubuntu", "centos", "red hat", "bash", "shell", "shell script"],
        "Networking & Cisco": [
            "network", "networking", "cisco", "lan", "wan", "tcp/ip", "vpn", "dns", "dhcp", "routers", "switches",
        ],
        "Virtualization & Servers": ["vmware", "virtualization", "hyper-v", "servers", "server administration"],
        "Technical Support & Helpdesk": [
            "technical support", "help desk", "helpdesk", "troubleshooting", "ticketing", "itil",
        ],
        "Hardware & Infrastructure": ["hardware", "infrastructure", "installation", "configuration", "upgrades"],
    },
}


def get_it_skills() -> Dict[str, Tuple[str, str]]:
    """Trả về alias_map: alias (lowercase) -> (canonical, category)."""
    alias_map: Dict[str, Tuple[str, str]] = {}
    for category, skills in IT_GENERAL_TAXONOMY.items():
        for canonical, aliases in skills.items():
            for alias in aliases:
                alias_map[alias.lower()] = (canonical, category)
    return alias_map


IT_GENERAL_WEIGHTS = {
    "software_and_data": 0.35,
    "engineering_and_concepts": 0.25,
    "cloud_devops_security": 0.25,
    "systems_and_support": 0.15,
}
assert abs(sum(IT_GENERAL_WEIGHTS.values()) - 1.0) < 1e-6

IT_GENERAL_CORE_SKILLS = {
    "software_and_data": ["Python", "Java", "JavaScript", "SQL", "PostgreSQL", "MySQL", "React"],
    "engineering_and_concepts": [
        "RESTful API", "OOP", "Unit Testing", "Agile/Scrum", "Authentication (JWT/OAuth)",
    ],
    "cloud_devops_security": ["Git", "Docker", "CI/CD", "AWS", "Cybersecurity & Backup"],
    "systems_and_support": ["Linux & Unix", "Networking & Cisco", "Technical Support & Helpdesk"],
}

IT_GENERAL_TARGET_COUNTS = {
    "software_and_data": 4,
    "engineering_and_concepts": 3,
    "cloud_devops_security": 3,
    "systems_and_support": 1,
}

IT_GENERAL_DOMAIN_TERMS = {
    "crud", "index", "indexing", "schema", "jwt", "token", "middleware",
    "caching", "cache", "migration", "migrations", "api", "apis", "endpoint",
    "endpoints", "restful", "rest", "rest api", "auth", "authentication",
    "authorization", "transaction", "transactions", "acid", "query", "queries",
    "orm", "async", "asynchronous", "webhook", "webhooks", "microservice",
    "microservices", "docker", "pipeline", "queue", "payload", "validation",
    "mvc", "clean architecture", "repository", "unit test", "websocket",
    "websockets", "cors", "session", "oauth", "oauth2", "redis", "sql",
    "nosql", "sharding", "replica", "replication", "kafka", "rabbitmq",
    "ci/cd", "ci-cd", "pagination", "rate limiting", "server", "network",
    "security", "troubleshooting", "deployment", "infrastructure", "cloud",
    "linux", "active directory", "backup", "disaster recovery", "configuration",
    "virtualization", "monitoring", "database", "architecture", "system",
    "triển khai", "hệ thống", "bảo mật",
}

IT_ACTION_VERBS = [
    # Tiếng Anh
    "built", "developed", "designed", "implemented", "optimized", "architected",
    "integrated", "deployed", "refactored", "automated", "created", "reduced",
    "improved", "scaled", "configured", "maintained", "engineered", "migrated",
    "led", "launched", "delivered", "monitored", "debugged", "tested",
    "documented", "secured", "owned", "mentored",
    # Tiếng Việt
    "xây dựng", "phát triển", "thiết kế", "triển khai", "tối ưu", "tích hợp",
    "tự động hóa", "cải thiện", "nâng cấp", "cấu hình", "bảo trì", "rút ngắn", "giảm",
    "viết", "lập trình", "vận hành", "giám sát", "kiểm thử", "di chuyển dữ liệu",
    "tái cấu trúc", "mở rộng", "dẫn dắt", "chịu trách nhiệm", "đảm nhận", "tăng",
]
