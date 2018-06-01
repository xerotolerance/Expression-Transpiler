''' @Author Cj Maxwell - NJIT 
    @Date 3.16.18
'''
class DartParseTree:
	class Token:
		specialtokens = {
			'(': 'LPAR', '{': 'LCRL', '_': 'UNDR',
			'/': 'FSLH', ',': 'COM', '-': 'DASH',
			'>': 'CRT', '}': 'RCRL', ')': 'RPAR',
			'\n': 'NL', '\r': 'NL', '\r\n': 'NL'
		}

		def __init__(self, tokentype='END', item=None):
			self.tokentype = tokentype
			self.item = item

		def __repr__(self):
			return '< ' + str(self.tokentype) + ': ' + str(self.item) + ' >'

		def __str__(self):
			return str(self.getitem())

		def gettokentype(self):
			return self.tokentype

		def getitem(self):
			return self.item

	class Function:

		class Parameters:
			def __init__(self, left=None, right=None):
				self._left = left
				self._right = right

			def __str__(self):
				rtn = ''
				rtn = rtn + str(self._left) if self._left else rtn
				rtn = rtn + ',' + str(self._right) if self._right else rtn
				return rtn[:-1] if len(rtn) > 0 and rtn[-1] == ',' else rtn

		class Lambda:

			class LambdaParam:
				def __init__(self, left=None, right=None):
					self._left = left
					self._right = right

				def __str__(self):
					rtn = ''
					rtn = rtn + str(self._left) if self._left else rtn
					rtn = rtn + ',' + str(self._right) if self._right else rtn
					return rtn[:-1] if len(rtn) > 0 and rtn[-1] == ',' else rtn

				def getleft(self):
					return self._left

				def getright(self):
					return self._right

			class LambdaStmt:
				def __init__(self, lt=None, rt=None):
					self._left = lt
					self._right = rt

				def __str__(self):
					rtn = ''
					rtn = rtn + str(self.getleft()) + ';' if self._left else rtn
					rtn = rtn + str(self.getright()) if self.getright() else rtn
					return rtn

				def getleft(self):
					return self._left

				def getright(self):
					return self._right

			def __init__(self, left=None, right=None):
				self._lparam = left
				self._lstmt = right

			def __str__(self):
				if self._lparam and self._lstmt:
					return '({}){{{}}}'.format(self._lparam, self._lstmt)
				elif self._lparam:
					return '({}){{}}'.format(self._lparam)
				elif self._lstmt:
					return '(){{{}}}'.format(self._lstmt)
				else:
					return '(){}'

		def __init__(self, expr=None, parameters=None, lamb=None):
			self._expr = expr
			self._params = parameters
			self._lamb = lamb

		def __repr__(self):
			rtn_str = ''
			rtn_str += 'This function\'s expression is a ' + str(type(self._expr)) + ' object\n'
			if self._params:
				rtn_str += 'This function\'s params are in a ' + str(type(self._params)) + ' object\n'
			if self._lamb:
				rtn_str += 'This function\'s trailing lambda is a ' + str(type(self._lamb)) + ' object\n'
			rtn_str += '\n'
			return rtn_str

		def __str__(self):
			rtn = str(self._expr)
			if self._params and self._lamb:
				rtn += '({},{})'.format(self._params, self._lamb)
			elif self._params:
				rtn += '({})'.format(self._params)
			elif self._lamb:
				rtn += '({})'.format(self._lamb)
			else:
				rtn += '()'
			return rtn

	@staticmethod
	def srctokenizer(strexpression):
		lst = list(strexpression)
		tlist = []
		curritem = ''
		mode = 'START'
		while lst:
			char = lst.pop(0)
			if not char.isalnum():
				if char == '_':
					if mode == 'START':
						mode = 'VAR'
					curritem += char
					continue
				if curritem:
					tlist.append(DartParseTree.Token(mode, curritem))
					curritem = ''
				if char in DartParseTree.Token.specialtokens:
					tlist.append(DartParseTree.Token(DartParseTree.Token.specialtokens[char], char))
				elif not char.isspace():
					return None
				mode = 'START'
				continue
			if char.isdigit():
				if mode == 'START':
					mode = 'NUM'
				if mode != 'NUM' and mode != 'VAR':
					if curritem:
						tlist.append(DartParseTree.Token(mode, curritem))
					curritem = ''
					mode = 'NUM'
			elif char.isalpha():
				if mode == 'START':
					mode = 'VAR'
				if mode != "VAR":
					if curritem:
						tlist.append(DartParseTree.Token(mode, curritem))
					curritem = ''
					mode = 'VAR'
			else:
				return None
			curritem += char
		if curritem:
			tlist.append(DartParseTree.Token(mode, curritem))
		tlist.append(DartParseTree.Token())
		return tlist

	@staticmethod
	def convert(funclist):
		transprog = ''
		for func in funclist:
			transprog += str(func) + '\n'
		return transprog.strip()

	def __init__(self, kotlincode=None):
		self._src_token_list = DartParseTree.srctokenizer(kotlincode)
		self._funclist = []
		while self._src_token_list:
			while self._src_token_list[0].gettokentype() == 'NL':
				self._src_token_list.pop(0)
			func = self.isfunction(self._src_token_list)
			if func:
				self._funclist.append(func)
			else:
				self._funclist.clear()
				return
			if self._src_token_list and self._src_token_list[0].gettokentype() == 'END':
				break

	def __str__(self):
		return DartParseTree.convert(self._funclist)

	def nexttoken(self):
		while self._src_token_list and self._src_token_list[0].gettokentype() == 'NL':
			self._src_token_list.pop(0)
		return self._src_token_list.pop(0) if self._src_token_list else DartParseTree.Token()

	def isfunction(self, tokenlist):
		expr = self.isexpression(tokenlist)
		if not expr:
			return None

		param = None
		# noinspection PyUnusedLocal
		lamb = None
		lp, rp = self.nexttoken(), None

		if lp.gettokentype() == 'LPAR':
			param = self.isparameter(tokenlist)
			rp = self.nexttoken()

			if rp.gettokentype() != 'RPAR':
				return None

			lamb = self.islambda(tokenlist)
			return self.Function(expr, param, lamb)
		else:
			tokenlist[0:0] = [lp]
			lamb = self.islambda(tokenlist)

		return self.Function(expr, param, lamb) if lamb else None

	def isparameter(self, tokenlist):
		lt, rt = self.isexpression(tokenlist), None
		if lt:
			com = self.nexttoken()
			if com.gettokentype() == 'COM':
				rt = self.isparameter(tokenlist)
				if not rt:
					tokenlist[0:0] = [com]
					return None
			else:
				tokenlist[0:0] = [com]
			return self.Function.Parameters(lt, rt)
		return None

	def isexpression(self, tokenlist):
		lamb = self.islambda(tokenlist)
		if not lamb:
			tok = self.nexttoken()
			if tok.gettokentype() not in ['VAR', 'NUM', 'NL']:
				tokenlist[0:0] = [tok]
				return None
			return tok if tok.gettokentype() != 'NL' else None
		return lamb

	def islambda(self, tokenlist):

		# noinspection PyShadowingNames
		def unpop(node, tokenlist):
			while node.getright():
				unpop(node.getright(), tokenlist)
			if node.getleft():
				tokenlist[0:0] = [node.getleft()]

		lc = self.nexttoken()
		if lc.getitem() != '{':
			tokenlist[0:0] = [lc]  # identical to insert lc @ index 0
			return None

		leftside = self.islambdaparam(tokenlist)
		if leftside:
			dash, carrot = self.nexttoken(), self.nexttoken()
			if dash.gettokentype() != 'DASH' or carrot.gettokentype() != 'CRT':
				tokenlist[0:0] = [dash, carrot]  # identical to insert dash,carrot @ index 0
				unpop(leftside, tokenlist)
				leftside = None

		rightside = self.islambdastmt(tokenlist)

		rc = self.nexttoken()
		if rc.getitem() != '}':
			return None

		return self.Function.Lambda(leftside, rightside)

	def islambdaparam(self, tokenlist):
		nt = self.nexttoken()
		if nt.gettokentype() in ['VAR', 'NUM']:
			nnt = self.nexttoken()
			if nnt.gettokentype() == 'COM':
				return self.Function.Lambda.LambdaParam(nt, self.islambdaparam(tokenlist))
			else:
				tokenlist.insert(0, nnt)
				return self.Function.Lambda.LambdaParam(nt)
		tokenlist.insert(0, nt)
		return None

	def islambdastmt(self, tokenlist):
		nt = self.nexttoken()
		if nt.gettokentype() in ['VAR', 'NUM']:
			rt = self.islambdastmt(tokenlist)
			return self.Function.Lambda.LambdaStmt(nt, rt)
		tokenlist.insert(0, nt)
		return None


# noinspection PyShadowingNames
def transpile(expression):
	dartprogram = DartParseTree(expression)
	transpiledsrc = str(dartprogram)
	return transpiledsrc
