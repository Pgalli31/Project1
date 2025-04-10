# 📊 Database Normalization & Interactive SQL Tool

This project allows you to:

- Normalize a dataset based on functional dependencies (up to 3NF)
- Automatically generate SQL scripts to:
  - Create normalized tables
  - Populate them with data
- Connect to a MySQL database and run those scripts
- Use an interactive command-line interface to perform SQL operations:
  - `INSERT`, `UPDATE`, `DELETE`
  - View tables, run custom queries

---

## 📁 Project Structure

```
project/
│
├── main.py               # Main script: normalization + SQL pipeline
├── database.py           # SQL generation and MySQL interaction
├── employee_data.csv     # Sample dataset (can be replaced)
└── README.md             # This file
```

---

## 🧰 Requirements

- Python 3.7+
- MySQL Server (locally or remotely hosted)
- Python libraries:
  - `mysql-connector-python`
  - `pandas`

---

## 🔧 Installation

### 1. 📦 Install Python Dependencies

Use `pip` to install the required libraries:

```bash
pip install pandas mysql-connector-python
```

### 2. 🐬 Set Up Your MySQL Server

- Install MySQL (locally or cloud-hosted)
- Create a MySQL user with permissions to:
  - Create/drop databases
  - Create/modify tables
  - Insert and query data

---

## 🚀 Usage Instructions

### 1. ⚙️ Configure Your MySQL Settings

Open `main.py`, and update the connection settings near the bottom:

```python
execute_sql_script(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="your_database_name",
    sql_script=sql_script
)

interactive_sql(
    host="localhost",
    user="your_mysql_username",
    password="your_mysql_password",
    database="your_database_name"
)
```

---

### 2. 📂 Replace Dataset (Optional)

You can use your own CSV file by replacing `employee_data.csv`.

Make sure column headers are properly formatted (no empty values).

---

### 3. ▶️ Run the Tool

In your terminal:

```bash
python main.py
```

You’ll be prompted to:
- Enter functional dependencies (e.g. `DepartmentID -> Department`)
- Enter the primary key (e.g. `EmployeeID`)
- The program will:
  - Normalize the dataset
  - Generate `CREATE TABLE` and `INSERT` SQL
  - Connect to MySQL and run everything

---

### 4. 🧑‍💻 Interactive SQL Mode

After the database is created, the terminal will enter interactive mode:

```
1. INSERT
2. UPDATE
3. DELETE
4. Custom SQL Query
5. Show All Tables
6. View Table
7. Exit
```

You can:
- Insert or update data into any table
- Run custom queries like `SELECT AVG(...)`
- View entire tables by name

---

## 💡 Example Functional Dependency Input

When prompted:

```
Enter Functional Dependencies, enter 'done' when finished
FD: DepartmentID -> Department
FD: EmployeeID -> Name
FD: EmployeeID -> DepartmentID
FD: done

Enter Primary Keys separated by a comma: EmployeeID
```

---

## 📌 Notes

- Data will only show up in the interactive viewer **after inserts complete** and the `DROP DATABASE` line is disabled or modified.
- Default table names are `Table_1`, `Table_2`, etc.
- The tool currently assumes all columns are stored as `VARCHAR(100)`.

---

## 🛠️ To-Do / Suggested Enhancements

- Auto-detect column types (`INT`, `FLOAT`, `DATE`)
- Export results to CSV
- Add command-line arguments for `--file`, `--db`, etc.
- Detect BCNF and offer optional decomposition

---

## 📞 Support

If you encounter bugs or want to add features, feel free to open an issue or reach out!