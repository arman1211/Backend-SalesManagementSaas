# Sales Management SaaS — Backend API

Django + DRF backend with JWT, Swagger, and modular app architecture.

## Quick Start

```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Swagger: http://127.0.0.1:8000/api/docs/

## API Endpoints (v1)

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/v1/auth/register/` | Register tenant + admin + default entity |
| POST | `/api/v1/auth/login/` | Login (JWT) |
| POST | `/api/v1/auth/logout/` | Logout (blacklist refresh) |
| POST | `/api/v1/auth/token/refresh/` | Refresh token |
| GET | `/api/v1/auth/me/` | Current user |

### Tenant & Entities
| Method | URL | Description |
|--------|-----|-------------|
| GET/PATCH | `/api/v1/tenants/me/` | Tenant company profile |
| CRUD | `/api/v1/tenants/entities/` | Company entities (multi-TRN) |

### Customers
| Method | URL | Description |
|--------|-----|-------------|
| CRUD | `/api/v1/customers/` | Customer management |
| GET | `/api/v1/customers/{id}/history/` | Customer 360 + account summary |

### Quotations
| Method | URL | Description |
|--------|-----|-------------|
| CRUD | `/api/v1/quotations/` | Quotation management |
| POST | `/api/v1/quotations/{id}/convert-to-invoice/` | Convert to tax invoice |

### Invoices
| Method | URL | Description |
|--------|-----|-------------|
| CRUD | `/api/v1/invoices/` | Tax invoice management |
| POST | `/api/v1/invoices/{id}/finalize/` | Issue invoice + calc receivables |
| POST | `/api/v1/invoices/{id}/refresh-receivable/` | Recalc balance/overdue/late fee |
| GET | `/api/v1/invoices/outstanding/` | Unpaid invoices |
| GET | `/api/v1/invoices/overdue/` | Overdue invoices |

### Service Reports
| Method | URL | Description |
|--------|-----|-------------|
| CRUD | `/api/v1/service-reports/` | Work completion reports |
| POST | `/api/v1/service-reports/{id}/complete/` | Mark completed |

### Credit Notes
| Method | URL | Description |
|--------|-----|-------------|
| GET/POST | `/api/v1/credit-notes/` | Create/list credit notes |
| POST | `/api/v1/credit-notes/{id}/issue/` | Issue credit note |

### Payments
| Method | URL | Description |
|--------|-----|-------------|
| GET/POST | `/api/v1/payments/` | Record & list payments |

### Dashboard
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/dashboard/` | KPIs, outstanding, recent activity |

### Reports
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/v1/reports/aging/` | Aging report (0-30, 31-60, 61-90, 90+) |
| GET | `/api/v1/reports/account-statement/?customer={id}` | Customer statement |
| GET | `/api/v1/reports/vat-summary/` | VAT report for filing |
| GET | `/api/v1/reports/collections/` | Payments received |
| GET | `/api/v1/reports/sales-summary/` | Sales by period |

## Business Rules (Paramount Excel parity)

- **VAT:** 5% default on net amount
- **Retention:** 10% held from invoice total
- **Late fee:** 3% on balance when overdue
- **Payment terms:** Configurable days (default 30)
- **Due date:** Invoice date + payment terms
- **Status:** Paid when balance = 0

## Modular App Structure

```
apps/invoices/
├── models/
│   ├── __init__.py
│   └── invoice.py
├── serializers/
├── views/
├── services/
├── urls.py
└── admin.py
```

## Apps

| App | Purpose |
|-----|---------|
| core | Base models, calculations, permissions |
| tenants | Tenant + CompanyEntity |
| accounts | Users + JWT auth |
| customers | Customer CRM |
| quotations | Quotes with line items |
| service_reports | Work completion reports |
| invoices | Tax invoices + receivables |
| credit_notes | Tax credit notes |
| payments | Payment recording |
| dashboard | Dashboard KPIs |
| reports | Aging, VAT, collections, statements |
