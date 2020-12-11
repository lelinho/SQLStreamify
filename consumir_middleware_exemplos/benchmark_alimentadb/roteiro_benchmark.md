sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000  prepare 

sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000 --report-interval=5 --threads=32 --time=200 run 2>&1




100000 registros com apenas escrita
Busca de um pequeno grupo dos dados

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000  cleanup

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000  prepare

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000 --report-interval=2 --threads=8 --time=200 --rate=5 run > bench_only.txt



500 registros com apenas escrita - 8 threads - 5 p/segundo
busca de todos os dados 

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=500 prepare

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=500 --report-interval=2 --threads=8 --time=200 --rate=5 run > SQLStreamify.txt



5000 registros com apenas escrita - 32 threads - 60 p/segundo

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=5000 prepare

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=5000 --report-interval=2 --threads=32 --time=200 --rate=60 run > bench_only.txt


100000 registros com apenas escrita - 32 threads - 60 p/segundo

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000 prepare

sysbench /usr/share/sysbench/oltp_write_only.lua --mysql-host=127.0.0.1 --mysql-port=3306 --mysql-user=root --mysql-password='password' --mysql-db=sbtest --db-driver=mysql --tables=1 --table-size=100000 --report-interval=2 --threads=32 --time=200 --rate=60 run > bench_only.txt