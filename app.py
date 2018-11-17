#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by vellhe 2017/7/9
from flask import Flask, request
import cx_Oracle
import json
import os
import datetime
# Flask初始化参数尽量使用你的包名，这个初始化方式是官方推荐的，官方解释：http://flask.pocoo.org/docs/0.12/api/#flask.Flask
app = Flask(__name__)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 


@app.route('/MyBill/List', methods=['POST'])
def my_bill_List():
    uId = request.form.get('uId')
    sql = 'SELECT FIXNO,DEPNAME, NAME, E.EQUIPNAME, DESCRIPTION, TRANSTIME, STATUS FROM BREAKDOWN BREAK INNER JOIN DEPARTMENT DEP ON BREAK.DEPNO = DEP.DEPNO INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = BREAK.PID INNER JOIN EQUIPMENT E ON E.EQUIPNO = BREAK.EQUIPNO WHERE U.PId = \''  + uId + '\' ORDER BY TRANSTIME DESC' 
    json_string = getData(sql)
    return json_string

@app.route('/Auth/List', methods=['POST'])
def get_my_auth_list():
  uId = request.form.get('uId')
  sql = 'SELECT AUTHORITY,DEPNO FROM AUTHORITY WHERE PID = \''+uId+'\''
  json_string = getData(sql)
  return json_string

@app.route('/Equipment/List', methods=['POST'])
def get_equipment():
  sql = 'SELECT EQUIPNO, EQUIPNAME FROM EQUIPMENT ORDER BY EQUIPNO' 
  json_string = getData(sql)
  return json_string

@app.route('/Breakdown/Fixno', methods=['POST'])
def get_create_fixno():
  sql = 'SELECT TO_CHAR(TO_NUMBER(FIXNO)+1) "NewFixNo" FROM BREAKDOWN WHERE ROWNUM = 1 ORDER BY FIXNO DESC' 
  json_string = getData(sql)
  return json_string

@app.route('/Breakdown/Add', methods=['POST'])
def add_break_down():
  fixno = request.form.get('fixno')
  depno = request.form.get('depno')
  pId = request.form.get('pid')
  equipno = request.form.get('equipno')
  description = request.form.get('description')
  sql = 'INSERT INTO BREAKDOWN(FIXNO, DEPNO, PID, EQUIPNO, DESCRIPTION, STATUS, TRANSTIME) VALUES(\'' + fixno + '\', \''+depno+'\', \''+pId+'\', \''+equipno+'\', \''+description+'\',\'NEW\', SYSDATE)' 
  json_string = EditData(sql)
  return json_string


@app.route('/Sign/List', methods=['POST'])
def get_sign_list():
  sql = 'SELECT B.FIXNO, DEP.DEPNAME, U.NAME, E.EQUIPNAME, B.DESCRIPTION, B.TRANSTIME FROM BREAKDOWN B INNER JOIN DEPARTMENT DEP ON B.DEPNO = DEP.DEPNO  INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = B.PID  INNER JOIN EQUIPMENT E ON E.EQUIPNO = B.EQUIPNO WHERE B.STATUS = \'NEW\'  ORDER BY TRANSTIME DESC' 
  json_string = getData(sql)
  return json_string

@app.route('/Bill/GetDetail', methods=['POST'])
def get_bill_detail():
  fixno = request.form.get('fixno')
  json_string = getDetail(fixno)
  return json_string

@app.route('/Assign/List', methods=['POST'])
def get_assign_list():
  sql = 'SELECT B.FIXNO, DEP.DEPNAME, U.NAME, E.EQUIPNAME, B.DESCRIPTION, B.TRANSTIME FROM BREAKDOWN B INNER JOIN DEPARTMENT DEP ON B.DEPNO = DEP.DEPNO INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = B.PID INNER JOIN EQUIPMENT E ON E.EQUIPNO = B.EQUIPNO WHERE 1=1 AND B.STATUS = \'SIGNED\' ORDER BY TRANSTIME DESC' 
  json_string = getData(sql)
  return json_string

@app.route('/Disposal/List', methods=['POST'])
def get_disposal_list():
  sql = 'SELECT B.FIXNO, DEP.DEPNAME, U.NAME, E.EQUIPNAME, B.DESCRIPTION, B.TRANSTIME FROM BREAKDOWN B INNER JOIN DEPARTMENT DEP ON B.DEPNO = DEP.DEPNO INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = B.PID INNER JOIN EQUIPMENT E ON E.EQUIPNO = B.EQUIPNO WHERE 1=1 AND B.STATUS = \'ASSIGN\' ORDER BY TRANSTIME DESC' 
  json_string = getData(sql)
  return json_string

@app.route('/Check/List', methods=['POST'])
def get_check_list():
  sql = 'SELECT B.FIXNO, DEP.DEPNAME, U.NAME, E.EQUIPNAME, B.DESCRIPTION, B.TRANSTIME FROM BREAKDOWN B INNER JOIN DEPARTMENT DEP ON B.DEPNO = DEP.DEPNO INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = B.PID INNER JOIN EQUIPMENT E ON E.EQUIPNO = B.EQUIPNO WHERE 1=1 AND B.STATUS = \'DISPOSAL\' ORDER BY TRANSTIME DESC' 
  json_string = getData(sql)
  return json_string

@app.route('/Sign/Ok', methods=['POST'])
def sign_ok():
  fixno = request.form.get('fixno')
  depno = request.form.get('depno')
  pid = request.form.get('pid')
  sql = 'INSERT INTO BREAKDOWNSIGNLOG("DEPNO","PID","FIXNO","STATUS","CREATETIME") VALUES (\''+depno+'\',\''+pid+'\',\''+fixno+'\',\'APPR\',SYSDATE)'
  json_string = EditData(sql)
  return json_string

@app.route('/Sign/Reject', methods=['POST'])
def sign_reject():
  fixno = request.form.get('fixno')
  depno = request.form.get('depno')
  pid = request.form.get('pid')
  sql = 'INSERT INTO BREAKDOWNSIGNLOG("DEPNO","PID","FIXNO","STATUS","CREATETIME") VALUES (\''+depno+'\',\''+pid+'\',\''+fixno+'\',\'REJECT\',SYSDATE)'
  json_string = EditData(sql)
  return json_string

@app.route('/Disposal/Ok', methods=['POST'])
def disposal_ok():
  fixno = request.form.get('fixno')
  sql = 'UPDATE BREAKDOWN SET STATUS = \'DISPOSAL\', DISPOSTIME = SYSDATE WHERE FIXNO = \''+ fixno +'\'' 
  json_string = EditData(sql)
  return json_string

@app.route('/Check/Ok', methods=['POST'])
def check_ok():
  fixno = request.form.get('fixno')
  sql = 'UPDATE BREAKDOWN SET STATUS = \'CHECKED\', CHECKTIME = SYSDATE WHERE FIXNO = \''+ fixno +'\'' 
  json_string = EditData(sql)
  return json_string

@app.route('/Bill/Resend', methods=['POST'])
def bill_resend():
  fixno = request.form.get('fixno')
  equipno = request.form.get('equipno')
  description = request.form.get('description')
  sql = 'UPDATE BREAKDOWN SET EQUIPNO = \''+ equipno +'\' , DESCRIPTION = \''+ description +'\', STATUS = \'NEW\' WHERE FIXNO = \''+ fixno +'\'' 
  json_string = EditData(sql)
  return json_string
  

@app.route('/Vendor/List', methods=['POST'])
def get_vender_list():
  sql = 'SELECT VENDNO, VENDNAME FROM VENDOR ORDER BY VENDNO' 
  json_string = getVendorData(sql)
  return json_string

@app.route('/Assign/Ok', methods=['POST'])
def assign_ok():
  fixno = request.form.get('fixno')
  depno = request.form.get('depno')
  pid = request.form.get('pid')
  vendor = request.form.get('vendor')
  sql = 'INSERT INTO ASSIGN("DEPNO","PID","FIXNO","VENDNO","CREATETIME") VALUES (\''+depno+'\',\''+pid+'\',\''+fixno+'\',\''+vendor+'\',SYSDATE)'
  json_string = EditData(sql)
  return json_string


def EditData(sql):
  host = "140.117.69.58"
  port = "1521"
  sid = "ORCL"
  dsn = cx_Oracle.makedsn(host, port, sid)
  connection = cx_Oracle.connect("Group3", "groupgroup33", dsn)
  cursor = cx_Oracle.Cursor(connection)
  cursor.execute(sql)
  connection.commit()
  connection.close()
  str_result = 'Success'
  return str_result

def myconverter(o):
  if isinstance(o, datetime.datetime):
    return o.__str__()

def getDetail(fixno):
  host = "140.117.69.58"
  port = "1521"
  sid = "ORCL"
  dsn = cx_Oracle.makedsn(host, port, sid)
  connection = cx_Oracle.connect("Group3", "groupgroup33", dsn)
  sql = 'SELECT FIXNO, DEPNAME, BREAK.EQUIPNO, NAME, E.EQUIPNAME, DESCRIPTION, TRANSTIME, STATUS FROM BREAKDOWN BREAK INNER JOIN DEPARTMENT DEP ON BREAK.DEPNO = DEP.DEPNO INNER JOIN USER1 U ON U.DEPNO = DEP.DEPNO AND U.PID = BREAK.PID INNER JOIN EQUIPMENT E ON E.EQUIPNO = BREAK.EQUIPNO  WHERE BREAK.FIXNO = \''+ fixno +'\''
  cursor = cx_Oracle.Cursor(connection)
  res = cursor.execute(sql)
  data = res.fetchall()
  fields = res.description
  sql2 = ('SELECT BL.CREATETIME AS \"ACTION_TIME\",'
          +' CASE WHEN BL.STATUS = \'NEW\' THEN \'開單\''
          +' WHEN BL.STATUS = \'REJECT\' THEN \'退回\''
          +' WHEN BL.STATUS = \'APPR\' THEN \'核可\''
          +' WHEN BL.STATUS = \'RESEND\' THEN \'重送\''
          +' END AS \"ACTION_NAME\",'
          +' \'\' AS \"ASSIGN_TO\",'
          +' U.NAME AS \"USERNAME\",'
          +' 0 AS \"TYPE\"'
          +' FROM BREAKDOWNSIGNLOG BL'
          +' INNER JOIN USER1 U ON BL.PID = U.PID'
          +' WHERE BL.FIXNO = \'%s\'' % fixno.encode('utf-8')
          +' UNION'
          +' SELECT A.CREATETIME AS \"ACTION_TIME\",'
          +' \'指派\' AS \"ACTION_NAME\",'
          +' V.VENDNAME AS \"ASSIGN_TO\",'
          +' \'\' AS \"USERNAME\",'
          +' 1 AS \"TYPE\"'
          +' FROM ASSIGN A'
          +' INNER JOIN VENDOR V ON A.VENDNO = V.VENDNO'
          +' WHERE A.FIXNO = \'%s\'' % fixno.encode('utf-8')
          +' UNION'
          +' SELECT B.DISPOSTIME AS \"ACTION_TIME\",' 
          +' \'處置\' AS \"ACTION_NAME\",'
          +' \'\' AS \"ASSIGN_TO\",'
          +' \'\' AS \"USERNAME\",'
          +' 2 AS \"TYPE\"'
          +' FROM BREAKDOWN B'
          +' WHERE B.FIXNO = \'%s\'' % fixno.encode('utf-8')
          +' UNION'
          +' SELECT B.CHECKTIME AS \"ACTION_TIME\",'
          +' \'驗收歸檔\' AS \"ACTION_NAME\",'
          +' \'\' AS \"ASSIGN_TO\",'
          +' \'\' AS \"USERNAME\",'
          +' 3 AS \"TYPE\"'
          +' FROM BREAKDOWN B'
          +' WHERE B.FIXNO  = \'%s\'' % fixno.encode('utf-8')
          +' ORDER BY \"TYPE\"')
  res2 = cursor.execute(sql2)
  data2 = res2.fetchall()
  fields2 = res2.description
  res.close()
  connection.close()
  str_result = ''
  column_list = [] 
  for i in fields:
    column_list.append(i[0])
  rownum = 0
  result = {}
  for row in data:
    rowdata = {}
    for idx, i in enumerate(fields, start = 0):
      value = row[idx]
      if type(value) is datetime.datetime:
        rowdata[column_list[idx]] = myconverter(row[idx])
      else:
        rowdata[column_list[idx]] = row[idx].strip()
    rownum = rownum + 1
    result[rownum] = rowdata

  column_list2 = []
  for i in fields2:
    column_list2.append(i[0])
  result2 = []
  for row in data2:
    rowdata = {}
    for idx, i in enumerate(fields2, start = 0):
      value = row[idx]
      if type(value) is datetime.datetime:
        rowdata[column_list2[idx]] = myconverter(row[idx])
      else:
        rowdata[column_list2[idx]] = row[idx]
    result2.append(rowdata)
  result['2'] = result2
  str_result = json.dumps(result)
  return str_result


def getData(sql):
  host = "140.117.69.58"
  port = "1521"
  sid = "ORCL"
  dsn = cx_Oracle.makedsn(host, port, sid)
  connection = cx_Oracle.connect("Group3", "groupgroup33", dsn)
  cursor = cx_Oracle.Cursor(connection)
  res = cursor.execute(sql)
  data = res.fetchall()
  fields = res.description
  res.close()
  connection.close()

  str_result = ''
  column_list = [] 
  for i in fields:
    column_list.append(i[0])

  rownum = 0
  result = {}
  for row in data:
    rowdata = {}
    for idx, i in enumerate(fields, start = 0):
      value = row[idx]
      if type(value) is datetime.datetime:
        rowdata[column_list[idx]] = myconverter(row[idx])
      else:
        rowdata[column_list[idx]] = row[idx].strip()
    rownum = rownum + 1
    result[rownum] = rowdata
  str_result = json.dumps(result)
  return str_result

def getVendorData(sql):
  host = "140.117.69.58"
  port = "1521"
  sid = "ORCL"
  dsn = cx_Oracle.makedsn(host, port, sid)
  connection = cx_Oracle.connect("Group3", "groupgroup33", dsn)
  cursor = cx_Oracle.Cursor(connection)
  res = cursor.execute(sql)
  data = res.fetchall()
  fields = res.description
  res.close()
  connection.close()

  str_result = ''
  column_list = [] 
  for i in fields:
    column_list.append(i[0])

  result = []
  datas = {}
  for row in data:
    rowdata = {}
    for idx, i in enumerate(fields, start = 0):
      value = row[idx]
      if type(value) is datetime.datetime:
        rowdata[column_list[idx]] = myconverter(row[idx])
      else:
        rowdata[column_list[idx]] = row[idx].strip()
    result.append(rowdata)
  datas['1'] = result
  str_result = json.dumps(datas)
  return str_result
  


if __name__ == "__main__":
    # 这种是不太推荐的启动方式，我这只是做演示用，官方启动方式参见：http://flask.pocoo.org/docs/0.12/quickstart/#a-minimal-application
    app.run(debug=True)
