CREATE EXTERNAL CATALOG jdbc_mysql
    PROPERTIES
    (
        "type"="jdbc",
        "user"="root",
        "password"="",
        "jdbc_uri"="jdbc:mysql://mysql:3306",
        "driver_url"="https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.28/mysql-connector-java-8.0.28.jar",
        "driver_class"="com.mysql.cj.jdbc.Driver"
    );