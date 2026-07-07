import boto3
import os
import sys
import pymysql

client = boto3.client("ssm", region_name="us-east-2")

# Read parameters from AWS SSM Parameter Store
params = {
    os.path.basename(p["Name"]): p["Value"] 
    for p in client.get_parameters_by_path(
        Path="/application/banking",
        WithDecryption=True
    )["Parameters"]
}

required = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_PORT"]
missing = [k for k in required if k not in params]

# Check required parameters
for k in required:
    if k in params:
        print(f"{k} ✅")
    else:
        print(f"{k} ❌")

if missing:
    print(f"Failed: Missing parameters {missing}")
    sys.exit(1)

# Connect to MySQL database and list tables
try:
    connection = pymysql.connect(
        host=params["DB_HOST"],
        user=params["DB_USER"],
        password=params["DB_PASSWORD"],
        database=params["DB_NAME"],
        port=int(params["DB_PORT"]),
        connect_timeout=10
    )

    cur = connection.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]

    connection.close()

    print(f"\nDatabase: {params['DB_NAME']}")
    print(f"Tables: {tables}")

except Exception as e:
    print("DB ERROR ❌:", e)
    sys.exit(1)

print("✅ Smoke test Done")