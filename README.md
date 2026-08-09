# 🛍️ Sweesa E-Commerce Analytics & Management System

An end-to-end **e-commerce data management and analytics system** built with **MySQL, Python, Pandas, SQLAlchemy, and Streamlit**.

The project combines relational database design, data generation, SQL analytics, interactive CRUD operations, business dashboards, and a product recommendation system in one integrated application.

It provides a practical example of how database management, data analysis, and business intelligence can be connected through a user-friendly web interface.

---

## ✨ Features

### Interactive Dashboard

The Streamlit dashboard provides live business insights directly from the MySQL database, including:

* Total revenue
* Total number of products
* Total number of orders
* Total number of customers
* Orders grouped by status
* Order activity over time
* Products grouped by category
* Low-stock product alerts
* Excel report export

### Product Management

The system supports product management operations through the web interface:

* Add new products
* Assign products to categories
* Set prices and stock quantities
* Update product prices
* Update inventory levels
* View recently added products

### Order Management

Users can manage customer orders directly from the dashboard:

* Search for orders
* Filter orders by customer or status
* Update order status
* Delete orders
* Track orders across different stages

Supported order statuses include:

* قيد الانتظار
* تم الشحن
* تم التوصيل

### 💡 Product Recommendation System

The project includes a simple **item-based recommendation system** based on customer purchasing patterns.

The recommendation pipeline:

1. Retrieves order-item data from MySQL.
2. Creates an **orders × products Pivot Table** using Pandas.
3. Calculates product-to-product correlations.
4. Identifies products that are frequently purchased together.
5. Returns the **Top 3 recommended products** for a selected item.

The recommendation engine uses **Pearson Correlation** to identify relationships between products based on historical order behavior.

### SQL Business Reports

The project also includes standalone SQL analytics reports for:

* Monthly sales performance
* Top 10 customers by total spending
* Low-stock products
* Product category information

---

## 🛠️ Technologies Used

* **Python**
* **MySQL**
* **SQL**
* **Pandas**
* **Streamlit**
* **SQLAlchemy**
* **MySQL Connector**
* **Plotly**
* **OpenPyXL**
* **Faker**
* **NumPy**

---

## 📁 Project Structure

```text
sweesa_ecommerce_project/
├── app.py
├── db_config.py
├── recommendations.py
├── requirements.txt
├── schema.sql
├── seeding.py
├── sql_reports.py
├── sweesa_ecommerce_db.sql
└── README.md
```

### Main Files

| File                      | Description                                                                   |
| ------------------------- | ----------------------------------------------------------------------------- |
| `app.py`                  | Streamlit dashboard, CRUD operations, analytics, and recommendation interface |
| `db_config.py`            | Shared MySQL and SQLAlchemy database connection configuration                 |
| `schema.sql`              | Database schema, tables, relationships, and constraints                       |
| `seeding.py`              | Generates and inserts sample Saudi Arabic e-commerce data                     |
| `sql_reports.py`          | Standalone SQL-based business analytics reports                               |
| `recommendations.py`      | Item-based product recommendation system                                      |
| `sweesa_ecommerce_db.sql` | Exported MySQL database containing the schema and sample data                 |
| `requirements.txt`        | Python dependencies required to run the project                               |

---

## 🗄️ Database Design

The database contains five relational tables:

```text
customers
    │
    └── orders
          │
          └── order_items
                 │
                 └── products
                        │
                        └── categories
```

### Tables

* `customers` — customer information and registration data
* `categories` — product categories
* `products` — product information, prices, and stock levels
* `orders` — customer orders and order status
* `order_items` — products, quantities, and prices associated with each order

The database uses:

* Primary Keys
* Foreign Keys
* Unique Constraints
* Check Constraints
* Cascading updates
* Referential integrity

The database is configured using **UTF-8 (`utf8mb4`)** to correctly support Arabic data.

---

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd sweesa_ecommerce_project
```

### 2. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure MySQL

Open:

```text
db_config.py
```

and enter your local MySQL password:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "PUT_YOUR_MYSQL_PASSWORD_HERE",
    "database": "sweesa_ecommerce_db",
    "charset": "utf8mb4",
}
```

> Do not commit your real database password to a public GitHub repository.

---

## Import the Database

The repository includes a ready-to-use MySQL database export:

```text
sweesa_ecommerce_db.sql
```

You can import it using **MySQL Workbench**, **phpMyAdmin**, or the terminal.

### Using Terminal

```bash
mysql -u root -p --default-character-set=utf8mb4 < sweesa_ecommerce_db.sql
```

Using `utf8mb4` is important to ensure that Arabic text and order-status values are imported correctly.

---

## Rebuild the Database from Scratch

If you prefer to recreate the database instead of importing the provided SQL dump:

### 1. Create the database and tables

```bash
mysql -u root -p --default-character-set=utf8mb4 < schema.sql
```

### 2. Configure the database connection in `seeding.py`

Enter your local MySQL credentials.

### 3. Generate sample data

```bash
python seeding.py
```

The script uses **Faker (`ar_SA`)** to generate realistic Arabic sample data for testing the application.

---

## Run the Streamlit Dashboard

```bash
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

The dashboard provides access to:

```text
📊 Dashboard
➕ Add Products
✏️ Update Prices & Inventory
📦 Order Management
💡 Recommendation System
```

---

## Run the SQL Analytics Reports

The business reports can also be executed independently:

```bash
python sql_reports.py
```

The script generates:

* Monthly sales report
* Top 10 customers by spending
* Low-stock product report

---

## Run the Recommendation System

The recommendation engine can be executed independently:

```bash
python recommendations.py
```

The system:

```text
MySQL Order Data
        ↓
Pandas DataFrame
        ↓
Orders × Products Pivot Table
        ↓
Product Correlation Matrix
        ↓
Top 3 Related Products
```

---

## 📊 Excel Report Export

The Streamlit dashboard can generate and download an Excel business report containing multiple sheets, including:

* Business summary
* Orders over time
* Products by category
* Low-stock products

This functionality is implemented using **Pandas and OpenPyXL**.

---

## Key Concepts Demonstrated

This project demonstrates practical experience with:

* Relational database design
* MySQL database management
* SQL joins and aggregation
* CRUD operations
* Data modeling
* Database constraints and relationships
* Python database integration
* Pandas data analysis
* Business intelligence dashboards
* Interactive Streamlit applications
* Data visualization with Plotly
* Item-based recommendation systems
* Pivot tables and correlation analysis
* Arabic data and UTF-8 encoding
* Synthetic data generation
* Excel report generation

---

## Project Workflow

```text
MySQL Database
      ↓
Python / SQLAlchemy
      ↓
Data Processing with Pandas
      ↓
Business Analytics
      ↓
Streamlit Dashboard
      ↓
CRUD + Visualization + Recommendations
      ↓
Excel Report Export
```

---

## 🔮 Possible Future Improvements

* Add user authentication and role-based access.
* Move database credentials to environment variables.
* Add advanced sales forecasting.
* Develop personalized customer recommendations.
* Add customer segmentation.
* Add inventory demand forecasting.
* Create additional business KPIs.
* Add date-range filters to dashboard analytics.
* Deploy the application with a cloud-hosted database.
* Build an API layer for database operations.

---

## License

This project was created for **educational and portfolio purposes**.
