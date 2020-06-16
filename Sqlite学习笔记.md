## Sqlite学习笔记

**1.Sqlite是什么**

SQLite是一个进程内的库，实现了自给自足的、无服务器的、零配置的、事务性的 SQL 数据库引擎。它是一个零配置的数据库，这意味着与其他数据库一样，您不需要在系统中配置。

就像其他数据库，SQLite 引擎不是一个独立的进程，可以按应用程序需求进行静态或动态连接。SQLite 直接访问其存储文件。

**2.ubuntu1604下安装sqlite**

1.先检查是否已安装

```shell
$ sqlite3
SQLite version 3.11.0 2016-02-15 17:29:24
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite> 
```

如果已安装sqlite会出现上述版本信息．

2.安装

进入[sqlite官网下载](https://www.sqlite.org/download.html)源码压缩档，sqlite-autoconf-3320200.tar.gz

![1592271367049](/home/ubuntu/.config/Typora/typora-user-images/1592271367049.png)

解压压缩档`$tar xvzf sqlite-autoconf-3320200.tar.gz`进入到解压后的根目录，执行如下命令

```shell
$ ./configure --prefix=/usr/local
$ make
$ make install
```

安装完再按照第一步查看版本信息

**sqlite基础命令**

sqlite有点命令和分号命令两大类，即.xxx和xxx;两种形式

---------------------------------

点命令

| 命令              | 功能                                           |
| ----------------- | ---------------------------------------------- |
| .help             | 列出sqlite帮助信息                             |
| .databases        | 列出数据库名称及其依附文件                     |
| .exit .quit       | 这两个都是退出sqlite命令                       |
| .show             | 显示各种设置的当前值                           |
| .header(s) ON/OFF | 开启或关闭表头显示                             |
| .mode MODE        | 设置结果显示模式，通常使用.mode column列左对齐 |
| .timer ON/OFF     | 开启或关闭CPU定时器                            |
| .tables           | 列出数据表                                     |
| .schema table1    | 得到table1的表头创建信息                       |
| .width 10,20,20   | 设置显示的宽度(第一列10,第二列20,第三列20)     |

分号命令:以数据表名table1为例

| 命令                                                         | 功能                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| create table table1;                                         | 创建一个名为table1的数据表，需要携带数据表表头信息           |
| drop table table1;                                           | 在当前数据库中删除数据表table1                               |
| drop table database_name.table1;                             | 删除database_name数据库中的数据表table1                      |
| insert into table1 [(c1,c2,c3,...,cn)] values(v1,v2,v3,...,vn); | 向table1中插入一条数据，其中指定的列c1...cn的值为v1...vn     |
| insert into table1 values(v1,v2,v3,...,vn);                  | 向table1中插入一条数据，按列的顺序设为v1...vn                |
| select * from table1                                         | 查询table1的所有数据                                         |
| select c1,c2..cn from table1                                 | 查询table1的指定列数据                                       |
| insert into table1 [(c1, c2, ... cn)] select c1, c2, ...cn  from table2 [where conditon]; | 将table2中符合条件的数据插入到table1中，where condition可选，contion条件根据后面介绍的运算符自由设计(可参考Mysql) |
| update table1 set c1=v1,c2=v2,.. where [condition];          | 修改数据表已有的数据                                         |
| delete from table1 where [condition];                        | 删除数据表已有的数据                                         |
将table1中id为6的数据行中的adress项修改为texas
```
sqlite> UPDATE table1 SET ADDRESS = 'Texas' WHERE ID = 6;
```

删除table1中id为6的数据行

```
sqlite> delete table1 WHERE ID = 6;
```

创建数据库

```
$ sqlite3 database_name.db
```

创建数据表

```shell
sqlite> create table table1(
    ID INT PRIMARY KEY NOT NULL,
    NAME TEXT NOT NULL,
    AGE INT NOT NULL,
    ADDRESS CHAR(20),
    SALARY REAL);
```
运算符

| 运算符      | 功能                         |
| ----------- | ---------------------------- |
| +           | 加法                         |
| -           | 减法                         |
| *           | 乘法                         |
| /           | 除法                         |
| %           | 取余                         |
| ==(=)       | 相等为真                     |
| !=(<>)      | 不等为真                     |
| < (<=)(!>)  | 小于(小于等于)(小于等于)为真 |
| \> (>=)(!<) | 大于(大于等于)(大于等于)为真 |

## python操作sqlite

**连接数据库**

```python
import sqlite3
conn = sqlite3.connect('test.db')
# save the changes
conn.commit()
#-------不需要时关闭游标-----
# close the connection with the database
conn.close()
```

**执行sqlite命令**(直接将sqlite命令语句加入execute中执行)

```python
import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()
c.execute('''CREATE TABLE COMPANY
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')
#-------不需要时关闭游标-----
conn.commit()  # 对内容产生影响才需要
conn.close()
```

**获取执行后的结果**

```python
import sqlite3
conn = sqlite3.connect('test.db')
c = conn.cursor()
cursor = c.execute("SELECT id, name, address, salary  from COMPANY")
for row in cursor:
   print "ID = ", row[0]
   print "NAME = ", row[1]
   print "ADDRESS = ", row[2]
   print "SALARY = ", row[3], "\n"
conn.close()
```

## C++操作sqlite

安装sqlite3的lib库

```shell
$ apt-get install libsqlite3-dev
```

导入头文件

```c++
#include <sqlite3.h>
```

编译时需要加上链接库

```shell
$ g++ csqlite.cpp -lsqlite3 -o testsql
```

**接口API**

| API                                                          | 用法及功能                                                   |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| sqlite3_open(const char *filename, sqlite3 **ppdb)           | 链接数据库，返回一个数据库连接对象．filename参数为数据库的文件名，当为NULL或':memory'时，则会在RAM中创建一个临时数据库，并只会在session的有效时间内持续．如果文件名不为上述两种，则打开数据库文件，数据库文件不存在则新建并打开． |
| sqlite3_exec(sqlite3 *, const char *sql, sqlite_callback, void *data, char **errmsg) | 执行sqlite命令，第一个参数 *sqlite3* 是打开的数据库对象，*sqlite_callback* 是一个回调，*data* 作为其第一个参数，errmsg 将被返回用来获取程序生成的任何错误。 |
| sqlite3_close(sqlite3 *)                                     | 关闭数据库连接                                               |

**链接数据库**

```c++
#include <iostream>
#include <sqlite3.h>

int main(int argc, char* argv[])
{
   sqlite3 *db;  // 数据库指针
   int rc;  // 标志值
   rc = sqlite3_open("db.sqlite3", &db); // 成功返回０，否则返回-1
   if( rc ){
      std::cout << "Can't open database" << std::endl;
   }else{
      std::cout << "Opened database successfully" << std::endl;
   }
   sqlite3_close(db);
}
```

**执行sqlite命令**

```c++
#include <iostream>
#include <sqlite3.h>

static int callback(void *NotUsed, int argc, char **argv, char **azColName){
  int i;
  for(i=0; i<argc; i++){
    std::cout << azColName[i] << "=" << argv[i] << std::endl;
  }
  return 0;
}

int main(int argc, char* argv[])
{
  sqlite3 *db;
  char *zErrMsg = 0;
  int  rc;
  char *sql;

  /* Open database */
  rc = sqlite3_open("db.sqlite3", &db);
  if( rc ){
    std::cout<<"Can't open database"<<std::endl;
    return 0;
  }else{
    std::cout<<"Opened database successfully"<<std::endl;
  }

  /* Create SQL statement */
  sql = "select * from app_detectresult";

  /* Execute SQL statement */
  rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
  if( rc != SQLITE_OK ){
    std::cout << "SQL error: "<< zErrMsg << std::endl;
  }else{
    std::cout << "Table created successfully" << std::endl;
  }
  sqlite3_close(db);
  return 0;
}
```

callback回调操作查询到的每一条数据！

显示如下

```shell
Opened database successfully
id=1
timestamp=23456982435
time=2020-06-10 13:23:05
result=1
numpass=1
locatepass=1
statupass=1
id=2
timestamp=23456982436
time=2020-06-10 13:23:06
result=1
numpass=1
locatepass=1
statupass=1
id=3
timestamp=23456982437
time=2020-06-10 13:23:07
result=1
numpass=1
locatepass=1
statupass=1
id=4
timestamp=23456982438
time=2020-06-10 13:23:08
result=1
numpass=1
locatepass=1
statupass=1
id=5
timestamp=23456982439
time=2020-06-10 13:23:09
result=1
numpass=1
locatepass=1
statupass=1
id=6
timestamp=298736234
time=2020-06-10 15:06:24
result=1
numpass=1
locatepass=1
statupass=1
id=7
timestamp=298736234
time=2020-06-10 15:06:24
result=1
numpass=1
locatepass=1
statupass=1
id=8
timestamp=23456982449
time=2020-06-10 13:23:19
result=1
numpass=1
locatepass=1
statupass=1
Table created successfully
```

