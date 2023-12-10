SHOW PROC '/frontends'\G;

CREATE DATABASE IF NOT EXISTS sr_hub;

USE sr_hub;
CREATE TABLE IF NOT EXISTS sr_member (
    sr_id            INT,
    name             STRING,
    city_code        INT,
    reg_date         DATE,
    verified         BOOLEAN
)
PARTITION BY RANGE(reg_date)
(
    PARTITION p1 VALUES [('2022-03-13'), ('2022-03-14')),
    PARTITION p2 VALUES [('2022-03-14'), ('2022-03-15')),
    PARTITION p3 VALUES [('2022-03-15'), ('2022-03-16')),
    PARTITION p4 VALUES [('2022-03-16'), ('2022-03-17')),
    PARTITION p5 VALUES [('2022-03-17'), ('2022-03-18'))
)
DISTRIBUTED BY HASH(city_code);

use sr_hub
INSERT INTO sr_member
WITH LABEL insertDemo
VALUES
    (001,"tom",100000,"2022-03-13",true),
    (002,"johndoe",210000,"2022-03-14",false),
    (003,"maruko",200000,"2022-03-14",true),
    (004,"ronaldo",100000,"2022-03-15",false),
    (005,"pavlov",210000,"2022-03-16",false),
    (006,"mohammed",300000,"2022-03-17",true);


SELECT * FROM sr_member;

SELECT sr_id, name
FROM sr_member
WHERE reg_date <= "2022-03-14";

SELECT sr_id, name  
FROM sr_member  
PARTITION (p2);

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

SHOW CATALOGS;