# Roteiro de passos para funcionamento e links úteis

## config.ini:

### DB

- type = mysql
- host = local onde está o BD
- port = porta para acesso ao BD
- db = nome_do_banco
- user = usuario
- password = senha

### EXPOSICAO

- ip = IP no qual será exposto o middleware

### Queries [nome_para_query]

- query = SELECT
- modo = full_dataset ou only_diff

---

## Alterações no MySQL:

- Liberar acesso ao mysql do IP desejado:
  https://receitasdecodigo.com.br/banco-de-dados/liberar-acesso-remoto-para-servidores-mysql

- Liberar porta 3306:

```
ufw allow from 172.17.0.0/24 to any port 3306
```

- Alterações nas configurações do mysql:

```
log_bin = /var/log/mysql/mysql-bin.log
expire_logs_days = 1
max_binlog_size = 10M
binlog_format = row
```

- Comando para verificar alterações:

```
  mysqlbinlog --no-defaults -v mysql-bin.000001
```

- Logs mysql/mariadb: https://mariadb.com/kb/en/general-query-log/

- checar alterações em tabela: https://aws.amazon.com/pt/blogs/database/streaming-changes-in-a-database-with-amazon-kinesis/

- Serialização dos dados: https://medium.com/galvanize/streaming-structured-json-18da4edd4f20

- Documentação do MariaDB: https://mariadb.com/resources/blog/data-streaming-with-mariadb/

- Parser SQL em Python: https://github.com/mozilla/moz-sql-parser

---

## Docker:

- Executar container do phpMyAdmin:

```
  docker run --rm --name myadmin -it -e PMA_HOST=172.17.0.1 -e PMA_PORT=3306 -p 8080:80 phpmyadmin/phpmyadmin
```

- Construir imagem:

```
  docker build -t container_consulta .
```

- Executar o container:

```
  docker run -it --rm --name consulta container_consulta
```

---

## rsync: atualizar arquivos no servidor

- Syncar arquivos com o servidor para produção rsync:

```
rsync -avz --delete ~/Documents/GitHub/StreamDB_middleware root@200.145.181.62:/opt
```
