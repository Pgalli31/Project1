import pandas as pd
from itertools import combinations
from database import execute_sql_script
from database import generate_sql_script
from database import interactive_sql


# Importing Dataset
def import_data(file):
    data = pd.read_csv(file)
    rows = data.shape[0]
    columns = data.shape[1]
    print(f"Number of rows: {rows}")
    print(f"Number of columns: {columns}")
    print(f"Sample: \n{data.head(5)}")
    print(f"Attributes: \n{data.dtypes}")
    return 'Done!'


def functional_dependency_id(data):
    df = data
    print("Enter Functional Dependencies, enter 'done' when finished")
    fds = []
    while True:
        # User input for functional dependencies
        fd = input("FD: ").strip()
        if fd.lower() == 'done':
            break
        if '->' in fd:
            # Creating tuples for the fds inputed
            deter, depend = fd.split("->")
            deter = tuple(attr.strip() for attr in deter.split(","))
            depend = tuple(attr.strip() for attr in depend.split(","))
            fds.append((deter, depend))

    # Retreiving primary key(s) from the user
    primary_key_input = input("Enter Primary Keys separated by a comma: ")
    primary_key = tuple(attr.strip() for attr in primary_key_input.split(","))

    print("Functional Dependencies:")
    for deter, depend in fds:
        print(f"{','.join(deter)} -> {','.join(depend)}")

    print(f"Primary Key: {', '.join(primary_key)}")

    # Computing closure
    closure = compute_closure(primary_key, fds)
    print(f"\nClosure of primary key ({', '.join(primary_key)}: {', '.join(closure)})")
    all_attributes = set(df.columns)

    # Checking if primary key is superkey
    if closure == all_attributes:
        print("Primary Key is superkey")
    else:
        print("Primary Key does not determine all attributes")

    partial_and_trans_depend(df, fds, primary_key)

    canidate_keys(df, fds)

    check_1NF(df)

    decomposed_tables = check_3NF(df, fds, primary_key)

    bcnf(df, fds)

    return decomposed_tables


def compute_closure(attributes, fds):
    '''
    This function takes in two parameters attributes and functional
    dependencies. Then computes the closure of attribute sets.
    '''
    closure = set(attributes)
    compute = True

    while compute:
        compute = False
        for deter, depend in fds:
            if set(deter).issubset(closure):
                new_attributes = set(depend)
                if not new_attributes.issubset(closure):
                    closure.update(new_attributes)
                    compute = True
    return closure


def partial_and_trans_depend(data, fds, primary_key):
    '''
    This function takes in three parameters. The data,
    the functional dependencies, and the primary key(s).
    It detects any partial and/or transitive dependenicies.
    '''
    all_attributes = set(data.columns)
    primary_keys = set(primary_key)

    primary_attr = set(primary_key)
    non_key = all_attributes - primary_attr

    for deter, depend in fds:
        determinants = set(deter)
        dependents = set(depend)

        # Check to see if the dependents rely on the full primary key
        if len(primary_key) > 1:
            if determinants.issubset(primary_keys) and not determinants == primary_keys:
                if dependents.issubset(non_key):
                    print(f"Partial Dependency found: {','.join(determinants)} -> {','.join(dependents)}")

        # Checking for transitive dependencies
        if not determinants >= primary_keys and dependents & non_key:
            if not determinants.issubset(primary_keys):
                print(f"Transitive Dependency Found: {','.join(determinants)} -> {','.join(dependents)}")


def canidate_keys(df, fds):
    all_attributes = set(df.columns)
    canidate_keys = []
    print("\n Searching for Candidate Keys...")

    for i in range(1, len(all_attributes) + 1):
        for attr in combinations(all_attributes, i):
            closure = compute_closure(attr, fds)

        if set(closure) == all_attributes:
            if not any(set(existing).issubset(set(attr)) for existing in canidate_keys):
                canidate_keys.append(attr)

    if canidate_keys:
        print("\n Candidate Keys Found:")
        for ck in canidate_keys:
            print(f"- {','.join(ck)}")
    else:
        print("No Candidate Keys Found.")

    return canidate_keys


def check_1NF(df):
    print("\n Checking If Dataset Satisfies 1NF...")
    multi_values_cols = set()
    delimeters = [",", ":", "/"]

    for column in df.columns:
        for value in df[column].astype(str):
            for delim in delimeters:
                if delim in value and len(value.strip()) > 1:
                    parts = value.split(delim)
                    if len([part for part in parts if part.strip()]) > 1:
                        multi_values_cols.add(column)
                        break

    if multi_values_cols:
        print("\n These columns violate 1NF")
        for col in multi_values_cols:
            print(f"- {col}")
    else:
        print("\n The dataset satisfies 1NF")


def check_2NF(df, fds, primary_key):
    print("\n Detecting and Resolving Partial Dependencies...")

    all_attributes = set(df.columns)
    primary_key_set = set(primary_key)
    non_primary_attr = all_attributes - primary_key_set
    partial_dep = []

    for deter, depend in fds:
        determinants = set(deter)
        dependents = set(depend)

        if len(primary_key) > 1:
            if determinants.issubset(primary_key_set) and not determinants == primary_key_set:
                if dependents.issubset(non_primary_attr):
                    print(f"Partial Dependency: {','.join(deter)} -> {','.join(depend)}")
                    partial_dep.append((determinants, dependents))

    if not partial_dep:
        print("No Partial Dependencies Found")
        return

    print("\n Suggested Decomposition to 2NF")

    decomposed_tables = []

    for deter, depend in partial_dep:
        attributes = list(deter.union(depend))
        decomposed_tables.append({
            "attributes": attributes,
            "primary_key": list(deter)
        })

    all_partial_attr = set()
    for _, depend in partial_dep:
        all_partial_attr.update(depend)

    remaining_attrs = list(all_attributes - all_partial_attr)
    decomposed_tables.append({
        "attributes": remaining_attrs,
        "primary_key": list(primary_key)
    })

    return decomposed_tables


def check_3NF(df, fds, primary_key):
    print("\n Identifying and Resolving Transitive Dependencies...")

    all_attributes = set(df.columns)
    primary_keys = set(primary_key)
    non_key_attributes = all_attributes - primary_keys
    transitive_dep = []

    for deter, depend in fds:
        determiants = set(deter)
        dependents = set(depend)

        if determiants >= primary_keys:
            continue

        if determiants.issubset(non_key_attributes) and dependents.issubset(non_key_attributes):
            print(f"Transitive Dependency: {', '.join(deter)} -> {', '.join(depend)}")
            transitive_dep.append((determiants, dependents))

    if not transitive_dep:
        print("No Transitive Dependencies Found")
        return [{
            "attributes": list(df.columns),
            "primary_key": list(primary_key)
        }]

    print("\n Suggested Decomposition to 3NF:")

    decomposed_tables = []
    table_num = 1
    for deter, depend in transitive_dep:
        attributes = list(deter.union(depend))
        decomposed_tables.append({
            "attributes": attributes,
            "primary_key": list(deter)
        })
        print(f"- Table {table_num}: {', '.join(attributes)} (PK: {', '.join(deter)})")
        table_num += 1

    all_transitive_attr = set()
    for _, depend in transitive_dep:
        all_transitive_attr.update(depend)

    remaining_attrs = list(all_attributes - all_transitive_attr)
    decomposed_tables.append({
        "attributes": remaining_attrs,
        "primary_key": list(primary_key)
    })

    print(f"- Table {table_num}: {', '.join(remaining_attrs)} (PK: {', '.join(primary_key)})")

    return decomposed_tables


def bcnf(df, fds):
    print("\n Checking for BCNF Violations...")

    all_attributes = set(df.columns)
    bcnf_violations = []

    for deter, depend in fds:
        determiants = set(deter)
        dependents = set(depend)
        closure = compute_closure(determiants, fds)

        if closure != all_attributes:
            print(f"BCNF Violation Found: {', '.join(deter)} -> {', '.join(depend)}")
            bcnf_violations.append((determiants, dependents))

    if not bcnf_violations:
        print("No BCNF Violations Found")
        return

    print("\n Suggested Decompostion:")

    table_num = 1
    used_attributes = set()

    for deter, depend in bcnf_violations:
        new_table = deter.union(depend)
        used_attributes.update(depend)

        print(f"- Table {table_num}: {', '.join(new_table)} (PK: {', '.join(deter)})")
        table_num += 1

    remaining_attrs = all_attributes - used_attributes
    if remaining_attrs:
        print(f"- Table {table_num}: {', '.join(remaining_attrs.union(deter))} (PK: {', '.join(deter)})")


if __name__ == '__main__':
    file = 'employee_data.csv'
    df = pd.read_csv(file)
    # print(import_data(file))
    table_definitions = functional_dependency_id(df)
    sql_script = generate_sql_script(df, table_definitions)

    execute_sql_script(
        host="localhost",
        user="root",
        password="12345678",
        database="project_1",
        sql_script=sql_script
    )

    interactive_sql(
        host="localhost",
        user='root',
        password='12345678',
        database='project_1'
    )
