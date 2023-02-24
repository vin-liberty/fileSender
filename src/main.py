import os.path

import flask
from flask import Flask, render_template, request, send_from_directory, send_file
from util import uniquename, after, sql_execute, uniquekey, query_key, is_expire
from config import FILE_ABSOLUTE
from urllib.parse import quote

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# 200 上传成功
# 201 上传成功，用户选择自己指定提取码，但提取码重复，改为系统自动生成
# 500 上传失败
@app.post('/upload')
def upload():
    file = request.files['file']
    auto_ge = request.form.get('autoGeneKey')
    if file:
        file_key, ge = uniquekey(auto_ge, request.form.get('key'))
        filename = uniquename(file.filename)
        origin_name = file.filename
        expire_time = after(int(request.form.get('expireTime')))
        sql_execute(
            'INSERT INTO file (key,name,origin_name,expire_time) VALUES (?,?,?,?)',
            (file_key, filename, origin_name, expire_time)
        )
        file.save(os.path.join(FILE_ABSOLUTE, filename))
        if ge and auto_ge == 'false':
            return {'code': 201, 'key': file_key}
        return {'code': 200, 'key': file_key}
    else:
        return {'code': 500}


# 200 成功
# 500 文件不存在，提取码错误
# 501 文件存在但已经过期
@app.get('/download/<key>')
def download_file(key):
    file = query_key(key)
    if not file:
        return {'code': 500}
    key, filename, origin_name, date = file
    if is_expire(date):
        return {'code': 501}
    return send_file(os.path.join(FILE_ABSOLUTE, filename), download_name=origin_name)


# 获取文件名
@app.get('/filename/<key>')
def get_filename(key):
    file = query_key(key)
    _, _, origin_name, _ = file
    return origin_name


if __name__ == '__main__':
    app.run()
