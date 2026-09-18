Suba os bancos com Docker:
```bash
docker run -d --name mysql-cp01 -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 mysql:8
docker run -d --name mongo-cp01 -p 27017:27017 mongo:7
```
Instale os pacotes:
```bash
pip install pymongo mysql-connector-python scikit-learn numpy
```

