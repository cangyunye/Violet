# /usr/bin/python3
# -*- coding :utf-8 -*-
# @author :cangyunye
# @email :cangyunye@gmail.com
# version:1.0
from subprocess import Popen, PIPE,check_output,run
import re
"""
小结：
1.使用communicate会直接关闭stdin，管道无法设计连续的sql语句在dbdriver中输入
2.如果要将Pin作为with语句输入，实现with内作为一次session模拟连续性输入
参考1不可行，但可采取特别方案，将communicate作为结尾，只调用一次，中间循环接受stdin.write
每次stdin.write必须存在一个用于区分每次
"""
class DataBaseOperator():
	def __init__(self, user, passwd, host, db='oracle'):
		self.user = user
		self.passwd = passwd
		self.host = host
		self.db = db
		self.Pin = None

	def _oraclePin(self):
		try:
			initset = """set head off;
			set linesize 5000;
			set pagesize 0;
			set colsep '|';
			set numwidth 15"""
			conn = 'sqlplus -s %s/%s@%s' % (self.user, self.passwd, self.host)
			Pin = Popen(conn, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			Pin.stdin.write(initset.encode('ascii')+b'\n')
			return Pin
		except Exception as e:
			print(e)

	def _timestenPin(self):
		try:
			conn = 'ttIsqlCS -v 1 -connStr "dsn=%s;uid=%s;pwd=%s" ' % (
				self.host, self.user, self.passwd)
			Pin = Popen(conn, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			return Pin
		except Exception as e:
			print(e)

	def _mysqlPin(self):
		try:
			conn = 'mysql -u%s -p%s -h%s -B' % (self.user,
												self.passwd, self.host)
			# conn = 'mysql -u%s -p%s -h%s -s -N'%(self.user,self.passwd,self.host)
			print(conn)
			Pin = Popen(conn, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
			# print(Pin.stdout.readline().decode('utf-8'))
			return Pin
		except Exception as e:
			print(e)

	def runscript(self, script):
		if self.db == 'oracle':
			run('sqlplus -s %s/%s@%s @%s' % (self.user, self.passwd,
												   self.host, script), shell=True, stdin=PIPE,check=True)
		elif self.db == 'timesten':
			run('ttIsqlCS -connStr "dsn=%s;uid=%s;pwd=%s" -f %s' % (self.host, self.user,
																		  self.passwd, script), shell=True, stdin=PIPE,check=True)
		elif self.db == 'mysql':
			run('mysql -u%s -p%s -h%s < %s' % (self.user, self.passwd,
													 self.host, script), shell=True, stdin=PIPE,check=True)
		else:
			raise NotImplementedError("%s not exist!" % (self.db))

	def run(self, sql):
		if self.db == 'oracle':
			self.Pin = self._oraclePin()
		elif self.db == 'timesten':
			self.Pin = self._timestenPin()
		elif self.db == 'mysql':
			self.Pin = self._mysqlPin()
		else:
			raise NameError("DB not exist!")
		self.Pin.stdin.write(sql.encode('ascii')+b'\n')
		stdout= self.Pin.communicate()[0]
		assert self.Pin.returncode == 0, 'Popen cmd failed.'
		return stdout

	def output(self, stdout, decode='utf-8'):
		text = stdout.decode(decode)
		if self.db == 'oracle':
			pattern = re.compile(r'\s')
			output = re.sub(pattern, "", text).split('|')
			row = len(text.split('\n'))
			col = len(text.split('\n')[0].split('|'))
		elif self.db == 'timesten':
			pattern = re.compile(r'\s|<|>')
			output = re.sub(pattern, "", text).split(',')
			row = len(text.split('\n'))
			col = len(text.split('\n')[0].split(','))
		elif self.db == 'mysql':
			output = re.sub(r'\n', "\t", text)
			output = re.sub(r'\r', "", output).split('\t')
			row = len(text.split('\n'))
			col = len(text.split('\n')[0].split('\t'))
		else:
			raise NotImplementedError("%s not exist!" % (self.db))
		return output,row,col


def main():
	# 测试
	DB = DataBaseOperator('xiaoying', 'wy123', '127.0.0.1', 'mysql')
	sql = 'select * from mysql.db;'
	# sql = 'select * from sakila.film  limit 0,5;'
	ret = DB.run(sql)

	print(ret.decode('utf-8'))

	r2c = ret.decode('utf-8').split('\n')
	print("分行为列",r2c)
	from collections import namedtuple
	col_d = {}
	del r2c[-1]
	for i in range(len(r2c)):
		if i==0:
			column = namedtuple('col', r2c[0].split('\t'))
			continue
		col_d[i] = column._make(r2c[i].split('\t'))
	print(col_d)

	for line in r2c:
		print(line)
	o,r,c = DB.output(ret)
	print("行数:",r,"列数",c,"\n输出：",o)
	for line in range(r):
		print(f"第{line+1}行：",line*c,(line+1)*c)
		print(o[line*c:(line+1)*c])

if __name__ == "__main__":
	main()

