import os
import time
import mysql.connector
import requests
from mysql.connector import Error
from prometheus_client import start_http_server, Enum

connection = None

mysql_health_status = Enum("mysql_health_status", "MySQL connection health", states=["healthy", "unhealthy"])
teams_num_non_zero = Enum("teams_num_non_zero", "There are more than one team in oncall", states=["true", "false"])
probe_status = Enum("probe_status", "My service status", states=["healthy", "unhealthy"])


def get_metrics():
    global connection
    service_health = True

    if connection and connection.is_connected():
        try:
            connection.ping(reconnect=True, attempts=3, delay=5)
            print('MySQL connection is still alive.')
            mysql_health_status.state("healthy")
        except Error as e:
            print(f'Error while checking MySQL connection: {e}')
            mysql_health_status.state("unhealthy")
            service_health = False
    else:
        try:
            connection = mysql.connector.connect(
                host=os.environ['MYSQL_HOST'],
                database=os.environ['MYSQL_DB'],
                user=os.environ['MYSQL_USER'],
                password=os.environ['MYSQL_PASS']
            )
            print('Connected to MySQL server.')
            mysql_health_status.state("healthy")
        except Error as e:
            print(f'Error while connecting to MySQL server: {e}')
            mysql_health_status.state("unhealthy")
            service_health = False
    try:
        teams = requests.get("http://oncall:8080/api/v0/teams/")
        if teams.status_code == 200 and len(teams.json()) > 0:
            teams_num_non_zero.state("true")
        else:
            teams_num_non_zero.state("false")
            service_health = False
    except:
        teams_num_non_zero.state("false")
        service_health = False
    
    if service_health:
        probe_status.state("healthy")
    else:
        probe_status.state("unhealthy")


if __name__ == '__main__':
    start_http_server(9000)
    while True:
        get_metrics()
        time.sleep(5)
