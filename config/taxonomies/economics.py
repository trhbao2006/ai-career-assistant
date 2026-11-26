"""Taxonomy và trọng số cho nhóm ngành Kinh tế (Finance, Accounting, Banking, Sales, Business)."""

ECONOMICS_TAXONOMY = {
    "core_finance_accounting": {
        "Financial Analysis": ["financial analysis", "financial modeling", "valuation", "phân tích tài chính"],
        "Accounting & GAAP": ["accounting", "gaap", "ifrs", "general ledger", "journal entries", "kế toán", "chuẩn mực kế toán"],
        "Financial Reporting": ["financial statements", "financial reporting", "balance sheet", "income statement", "báo cáo tài chính"],
        "Accounts Payable & Receivable": ["accounts payable", "accounts receivable", "invoicing", "billing", "công nợ"],
        "Budgeting & Forecasting": ["budgeting", "budget", "forecasting", "cash flow", "lập ngân sách", "dự báo tài chính"],
        "Auditing & Compliance": ["audit", "auditing", "internal audit", "internal controls", "compliance", "kiểm toán"],
        "Taxation": ["tax", "taxation", "tax preparation", "thuế", "kê khai thuế"],
        "Reconciliation": ["reconciliation", "reconciliations", "month end", "month-end closing", "đối chiếu"],
        "Banking & Credit": ["banking", "credit", "loan", "underwriting", "risk management", "tín dụng", "ngân hàng", "thẩm định"],
    },
    "business_sales_marketing": {
        "Sales & Revenue Growth": ["sales", "b2b", "b2c", "revenue growth", "closing", "bán hàng", "doanh số"],
        "Business Development": ["business development", "lead generation", "prospecting", "account management", "phát triển kinh doanh"],
        "Marketing & Strategy": ["marketing", "digital marketing", "market research", "branding", "seo", "tiếp thị", "nghiên cứu thị trường"],
        "Customer Relationship": ["customer service", "client acquisition", "client retention", "negotiation", "đàm phán", "khách hàng"],
        "Operations & Supply Chain": ["supply chain", "procurement", "inventory", "logistics", "vendor management", "chuỗi cung ứng", "mua hàng"],
        "Business Analysis": ["business analysis", "requirements", "kpi", "roi", "strategy", "phân tích nghiệp vụ"],
    },
    "tools_and_software": {
        "Microsoft Excel": ["excel", "ms excel", "vlookup", "pivot table", "spreadsheets"],
        "SAP / ERP": ["sap", "erp", "oracle financials", "peoplesoft", "netsuite"],
        "QuickBooks / Accounting Software": ["quickbooks", "misa", "fast accounting", "xero"],
        "CRM Systems": ["crm", "salesforce", "hubspot"],
        "BI & Data Visualization": ["power bi", "powerbi", "tableau", "sql"],
        "Office Suite": ["microsoft office", "ms office", "powerpoint", "word", "outlook"],
    },
    "soft_and_management": {
        "Leadership & Management": ["leadership", "management", "supervising", "quản lý"],
        "Communication & Presentation": ["communication", "presentation", "giao tiếp", "thuyết trình"],
        "Project Management": ["project management", "planning", "quản lý dự án"],
        "Contract Management": ["contracts", "contract management", "hợp đồng"],
    },
}

ECONOMICS_WEIGHTS = {
    "core_finance_accounting": 0.35,
    "business_sales_marketing": 0.30,
    "tools_and_software": 0.20,
    "soft_and_management": 0.15,
}
assert abs(sum(ECONOMICS_WEIGHTS.values()) - 1.0) < 1e-6

ECONOMICS_CORE_SKILLS = {
    "core_finance_accounting": ["Financial Analysis", "Budgeting & Forecasting", "Financial Reporting"],
    "business_sales_marketing": ["Sales & Revenue Growth", "Customer Relationship", "Business Development"],
    "tools_and_software": ["Microsoft Excel", "Office Suite"],
    "soft_and_management": ["Communication & Presentation", "Leadership & Management"],
}

ECONOMICS_TARGET_COUNTS = {
    "core_finance_accounting": 3,
    "business_sales_marketing": 2,
    "tools_and_software": 2,
    "soft_and_management": 2,
}

ECONOMICS_DOMAIN_TERMS = {
    "revenue", "roi", "kpi", "budget", "forecast", "audit", "ledger", "gaap",
    "reconciliation", "cash flow", "margin", "profit", "b2b", "crm", "pipeline",
    "quota", "portfolio", "credit", "underwriting", "compliance", "invoice",
    "payable", "receivable", "tax", "procurement", "inventory", "doanh thu",
    "lợi nhuận", "ngân sách", "báo cáo tài chính", "công nợ", "kiểm toán",
}
