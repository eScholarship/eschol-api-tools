import pymysql
from datetime import datetime

from dotenv import dotenv_values
system_creds = dotenv_values(".env")

mysql_conn = pymysql.connect(
    host=system_creds['ESCHOL_DB_SERVER'],
    user=system_creds['ESCHOL_DB_USER'],
    password=system_creds['ESCHOL_DB_PASSWORD'],
    database=system_creds['ESCHOL_DB_DATABASE'],
    cursorclass=pymysql.cursors.DictCursor)

with mysql_conn.cursor() as cursor:
    cursor.execute("SELECT queue, count(*) as count FROM queues GROUP BY queue;")
    queue_counts = cursor.fetchall()
    current_time = datetime.now().replace(microsecond=0).isoformat()

    for row in queue_counts:
        print(f"{current_time},{row['queue']},{row['count']}")

    cursor.close()

mysql_conn.close()
