import sqlite3
conn = sqlite3.connect('test.sqlite')
cur=conn.cursor()
sqlstr='''CREATE TABLE articleinfo(
    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, 
    artWriter TEXT NOT NULL,
    artContent TEXT NOT NULL
)'''
cur.execute(sqlstr)
conn.commit()
conn.close()