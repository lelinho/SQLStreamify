import pymysql as MySQLdb
import time

# Open database connection
db = MySQLdb.connect("mysql","zabbix","z@bb1x","zabbix" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

inicio = time.time()
cursor.execute("SELECT `employees`.`first_name`, `employees`.`last_name`, `salaries`.`from_date`, `salaries`.`to_date`, `salaries`.`salary` FROM `employees` LEFT JOIN `salaries` ON `employees`.`emp_no` = `salaries`.`emp_no` ORDER BY `salary` DESC LIMIT 10")

data = cursor.fetchall()
fim = time.time()


for row in data:
    print(row[0], row[1]," - ", row[4])


print(f"Tempo de execucao da consulta: {(fim - inicio)}")

# disconnect from server
db.close()