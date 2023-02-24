import sqlite3
import uuid
import os
from datetime import datetime, timedelta
import random
import string
from config import SQLITE_ABSOLUTE


# 获取唯一的提取码
def uniquekey(auto_gene: str, key: str):
    k = ''
    ge = True
    if auto_gene == 'false':
        k = key
        ge = False
    else:
        k = generate_key()
    conn = sqlite3.connect(SQLITE_ABSOLUTE)
    cur = conn.cursor()
    cur.execute('SELECT key FROM file')
    rows = cur.fetchall()
    keys = set(row[0] for row in rows)
    if k in keys and auto_gene == 'false':
        k = generate_key()
        ge = True
    while k in keys:
        k = generate_key()
    cur.close()
    conn.close()
    return k, ge


# 获取唯一的文件名
def uniquename(filename: str) -> str:
    uid = uuid.uuid4()
    _, ext = os.path.splitext(filename)
    return f'{uid.hex}{ext}'


# 获取当前日期
def now() -> datetime:
    return datetime.now()


# 获取days天后的日期
def after(days: int) -> datetime:
    return now() + timedelta(days=days)


# 传入一个日期字符串，判断日期是否过期了
# 字符串的格式就是datetime对象调用__str__()的结果,如2023-02-25 18:43:00.683743
def is_expire(date: str) -> bool:
    fmt = '%Y-%m-%d %H:%M:%S.%f'
    # 将字符串转换成datetime对象
    dt_obj = datetime.strptime(date, fmt)
    return now() > dt_obj


# 自动生成提取码
# 1.提取码为4位
# 2.提取码是小写字母+数字的组合，可以只有小写字母，也可以只有数字
def generate_key() -> str:
    # 生成包含数字和小写字母的所有字符集合
    all_chars = string.digits + string.ascii_lowercase
    # 生成4位长度的提取码
    code = ''.join(random.choice(all_chars) for _ in range(4))
    return code


def sql_execute(sql: str, data):
    conn = sqlite3.connect(SQLITE_ABSOLUTE)
    conn.execute(sql, data)
    conn.commit()
    conn.close()


def sql_execute_without_data(sql: str):
    conn = sqlite3.connect(SQLITE_ABSOLUTE)
    conn.execute(sql)
    conn.commit()
    conn.close()


# 查询给定提取码的文件信息
# 文件存在返回 ('123', 'e703551326754875987bff959cf428f1.docx', '大学生职业生涯规划书.docx', '2023-03-01 19:49:42.754141')
# 不存在返回None
def query_key(key: str):
    conn = sqlite3.connect(SQLITE_ABSOLUTE)
    cur = conn.cursor()
    cur.execute('SELECT * FROM file WHERE key = ? LIMIT 1', (key,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return None
    return rows[0]
