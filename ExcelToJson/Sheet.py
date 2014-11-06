#coding=utf-8
import xlrd
import json
import math

from xlrd import XL_CELL_EMPTY, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_DATE, XL_CELL_BOOLEAN, XL_CELL_ERROR, \
    XL_CELL_BLANK

import SheetManager

class Field:
    def __init__(self):
        #字段名
        self.name = None
        #字段类型
        self.type = None
        #缺省值
        self.default = None
        #折叠属性
        self.folding = None
        #所在列
        self.col = -1

    def __str__(self):
        return "name:%r,type:%r,default:%r,folding:%r" % (self.name, self.type, self.default, self.folding)

class Sheet:
    def __init__(self, sh):
        self.sh = sh
        self.name = sh.name
        #是否完全初始化完毕（最后一个步骤是插入表的引用）
        self.inited = False
        #字段属性列表
        self.fieldList = []
        #引用的其他sheet名
        self.referenceSheets = set()
        #解析的数据
        self.python_obj = {}

        #
        self.defaultRow = -1
        self.foldingRow = -1
        self.defaultRow = -1
        self.foldingRow = -1
        self.typeRow = -1
        self.nameRow = -1
        self.descRow = -1
        self.tableNameRow = -1
        self.useFlagRow = -1
        self.dataStartRow = -1
        self.dataEndRow = -1
        self.dataEndRow = -1
  
        self.__findRow()
        self.__findCol()

        self.__parseField()
        self.__parseReferenceSheet()

        self.__convertPython()
        self.__executeFolding()

    #查找数据起始行数，格式行，缺省值行，类型行，数据终止行数
    def __findRow(self):
       
        self.defaultRow = -1
        self.foldingRow = -1

        for i in range(6):            
            value = self.sh.cell(i, 0).value
            
            if value == '__default__':
                self.defaultRow = i
            elif value == '__folding__':
                self.foldingRow = i
            elif value == '__type__':
                self.typeRow = i
            elif value == '__name__':
                self.nameRow = i
            elif value == '__desc__':
                self.descRow = i
            elif value == '__table_name__':
                self.tableNameRow = i
            elif value == '__use_flag__':
                self.useFlagRow = i
            else:               
                self.dataStartRow = i
                break

        for row in range(self.sh.nrows):
            if self.sh.cell(row, 1).ctype == XL_CELL_EMPTY:
                self.dataEndRow = row
                break

        if row == self.sh.nrows - 1:
            self.dataEndRow = self.sh.nrows

        print self.dataStartRow

    #查找数据终止列数
    def __findCol(self):
        #遍历查找，如果在excel中存在多余的注释，列数为第一个空字符串出现的单元格下标#
        for col in range(self.sh.ncols):
            if self.sh.cell(self.nameRow, col).ctype == XL_CELL_EMPTY:
                self.dataEndCol = col
                break

        #若col未定义，则表示在excel中不存在多余的注释，则列数为整个表的列数#
        if col == self.sh.ncols - 1:
            self.dataEndCol = self.sh.ncols

    #解析字段属性
    def __parseField(self):

        for col in range(1, self.dataEndCol):

            #过滤客户端不使用的字段
            useFlag = self.sh.cell(self.useFlagRow, col).value
            if 0 != useFlag and 1 != useFlag:
                continue
            
            field = Field()
            self.fieldList.append(field)

            #字段类型
            field.type = str(self.sh.cell(self.typeRow, col).value).strip()

            #字段名字
            field.name = str(self.sh.cell(self.nameRow, col).value).strip()

            #字段所在列
            field.col = col

            #字段缺省值
            if self.defaultRow == -1:
                field.default = None
            else:
                type = field.type
                ctype = self.sh.cell(self.defaultRow, col).ctype
                value = self.sh.cell(self.defaultRow, col).value

                if col == 0:  #第一位缺省值，占位符
                    field.default = None
                elif ctype == XL_CELL_EMPTY:  #空白格
                    field.default = None
                elif value == 'null':  #null格
                    field.default = None
                elif type == 'i':
                    field.default = int(value)
                elif type == 'f':
                    field.default = value
                elif type == 's':
                    field.default = value
                elif type == 'b':
                    field.default = bool(value)
                elif type == 'as' or type == 'ai' or type == 'af':  #数组
                    field.default = self.__convertStrToList(value, type)
                elif type == 'd':  #字典
                    field.default = self.__convertStrToDict(value)
                elif type == 'r':  #引用
                    field.default = value                

            #字段折叠
            if self.foldingRow == -1:
                field.folding = None
            else:
                ctype = self.sh.cell(self.foldingRow, col).ctype
                value = self.sh.cell(self.foldingRow, col).value

                if ctype == XL_CELL_EMPTY:
                    field.folding = None
                else:
                    field.folding = value

            #for field in self.fieldList:
            #    print field.type, "---", field.name

    def __parseReferenceSheet(self):
        for row in range(self.dataStartRow, self.dataEndRow):
            for col in range(len(self.fieldList)):
                field = self.fieldList[col]
                fieldType = field.type
                value = self.sh.cell(row, col).value

                if fieldType == 'r':  #引用，保存引用字符串，以备插入引用表
                    sheetName = value.split(".")[0]
                    self.referenceSheets.add(sheetName)

    #转换字符串为list
    def __convertStrToList(self, str, typeStr):
        type = typeStr[1]
        list = str.split(',')
        for i in range(len(list)):
            if type == 's':
                list[i] = list[i]
            elif type == 'i':
                list[i] = int(list[i])
            elif type == 'f':
                list[i] = float(list[i])

        return list

    #转换字符串为dict
    def __convertStrToDict(self, str):
        dict = {}
        list = str.split(',')
        for i in range(len(list)):
            kv = list[i].split(':')
            key = kv[0]
            value = kv[1]

            if value.isdigit() and '.' in value:
                dict[key] = float(value)
            elif value.isdigit():
                dict[key] = int(value)
            else:
                dict[key] = value

        return dict

    def log(self):
        print '备注行',self.descRow
        print '缺省值行', self.defaultRow
        print '折叠行', self.foldingRow
        print '类型行', self.typeRow
        print '字段名行', self.nameRow
        print '数据起始行', self.dataStartRow
        print '数据终止行', self.dataEndRow
        print '数据终止列', self.dataEndCol
        print '字段属性'
        for field in self.fieldList:
            print field
        print '引用表', self.referenceSheets

    #获得当前行的recordId
    def __getRecordId(self, row):
        recordId = self.sh.cell(row, 0).value
        ctype = self.sh.cell(row, 0).ctype
        if ctype == XL_CELL_TEXT:
            pass
        elif ctype == XL_CELL_NUMBER:
            #处理为整数做主键
            recordId = int(recordId)
            #TODO 并不支持小数做主键

        return recordId

    #解析自身数据为python，并折叠。不包括引用数据。
    def __convertPython(self):
        #dump数据#
        for row in range(self.dataStartRow, self.dataEndRow):
            recordId = self.__getRecordId(row)
            record = self.python_obj[recordId] = {}

            for col in range(len(self.fieldList)):
                field = self.fieldList[col]

                fieldName = field.name
                fieldType = field.type
                fieldCol = field.col

                #encodeValue = unicode(self.sh.cell(row, fieldCol).value).encode('UTF-8')
                value = self.sh.cell(row, fieldCol).value
                ctype = self.sh.cell(row, fieldCol).ctype

                print col, "   ", fieldType, "  ", value

                if ctype == XL_CELL_EMPTY:  #如果是空的，就填入缺省值
                    #continue
                    if fieldType == 'i':                        
                        record[fieldName] = 0
                    elif fieldType == 'f':
                        record[fieldName] = 0.0
                    elif fieldType == 'b':
                        record[fieldName] = 0
                    elif fieldType == 's':
                        record[fieldName] = ''
                    else:
                        record[fieldName] = None
                        
                elif value == 'null' or value == '': #null为保留字
                    record[fieldName] = None
                else:
                    #如果没有类型字段，就自动判断类型，只支持i、f、s
                    #if fieldType == '' or fieldType == None:
                    #    fieldType = self.__autoDecideType(value)

                    if fieldType == 'i':
                        strValue = str(value).strip()
                        if strValue != '':
                            record[fieldName] = int(float(strValue))                           
                    elif fieldType == 'f':
                        strValue = str(value).strip()
                        if strValue != '':
                            record[fieldName] = float(strValue)
                    elif fieldType == 's':
                        record[fieldName] = value
                    elif fieldType == 'b':
                        record[fieldName] = bool(value)
                    elif fieldType == 'as' or fieldType == 'ai' or fieldType == 'af':
                        record[fieldName] = self.__convertStrToList(value, fieldType)
                    elif fieldType == 'd':
                        record[fieldName] = self.__convertStrToDict(value)
                    elif fieldType == 'r':  #引用，保存引用字符串，以备插入引用表
                        record[fieldName] = value

    def __autoDecideType(self,value):
        if isinstance(value,float):
            if math.ceil(value) == value:
                return 'i'
            else:
                return 'f'
        else:
            return 's'

    def __executeFolding(self):

        while (True):
            foldingType = None
            #查找右侧括号#
            for i in range(len(self.fieldList)):
                field = self.fieldList[i]
                folding = field.folding
                if folding == None or folding == '':
                    continue

                if folding[0] == '}':
                    foldingType = "brace"
                elif folding[0] == ']':
                    foldingType = "bracket"
                else:  #未找到右括号，进入下一轮循环
                    continue

                #记录折叠终止格
                endIndex = i

                #清除括号
                field.folding = folding[1:]
                break

            #未找到折叠字段类型，就跳出
            if foldingType == None:
                break

            #查找左侧括号#
            for i in range(endIndex - 1, -1, -1):
                field = self.fieldList[i]
                folding = field.folding
                if folding == None or folding == '':
                    continue

                if foldingType == "brace":
                    bracketIndex = folding.rfind('{')
                elif foldingType == "bracket":
                    bracketIndex = folding.rfind('[')

                #未找到括号，跳过
                if bracketIndex == -1:
                    continue

                #记录折叠起始格
                startIndex = i

                #取折叠后的名字
                foldingName = folding[bracketIndex + 1:]

                #清除括号和名字
                field.folding = folding[:bracketIndex]
                break

            #折叠数据#
            for row in range(self.dataStartRow, self.dataEndRow):
                #取记录
                recordId = self.__getRecordId(row)
                record = self.python_obj[recordId]

                #生成新对象
                if foldingType == "brace":
                    foldingObj = {}
                elif foldingType == "bracket":
                    foldingObj = []

                for col in range(startIndex, endIndex + 1):
                    field = self.fieldList[col]

                    #保存折叠后的数据
                    if foldingType == "brace":
                        foldingObj[field.name] = record[field.name]
                    elif foldingType == "bracket":
                        foldingObj.append(record[field.name])

                    del record[field.name]

                #挂接新对象
                record[foldingName] = foldingObj

            #折叠字段#
            #需要清除的字段索引表
            delFieldList = []
            for col in range(startIndex + 1, endIndex + 1):
                field = self.fieldList[col]
                delFieldList.append(field)

            #如果最后一格有内容，则复制给合并后的格子
            if field.folding != None or field.folding != '':
                folding = field.folding
            else:
                folding = None

            #执行清除
            for field in delFieldList:
                self.fieldList.remove(field)

            #刷新折叠后的字段
            field = self.fieldList[startIndex]
            field.name = foldingName
            field.type = 'd'  #折叠后变为字典类型
            if folding != None:
                field.folding = folding

            #刷新列表长度
            self.dataEndCol -= endIndex - startIndex

    def toPython(self, sheet_output_field=[]):
        #插入引用表
        if not self.inited:
            self.__mergePython()
            self.inited = True

        #选择性输出
        if sheet_output_field == []:
            #这里把dic的数值换成list型的，这样做，是为了不产生键值对的json，而是数组的json--刘元斌
            sheet_output_arr = []
            print("test")
            for recordId in self.python_obj:
                sheet_output_arr.append(self.python_obj[recordId])       
            return sheet_output_arr
        else:
            new_python_obj = self.python_obj.copy()
            for recordId in new_python_obj:
                delFieldNameList = []

                for fieldName in new_python_obj[recordId]:
                    if fieldName in sheet_output_field:
                        pass
                    else:
                        delFieldNameList.append(fieldName)

                for delFieldName in delFieldNameList:
                    del new_python_obj[recordId][delFieldName]
            
            
            return new_python_obj

    #合并引用表到当前表
    def __mergePython(self):
        for row in range(self.dataStartRow, self.dataEndRow):

            recordId = self.__getRecordId(row)
            record = self.python_obj[recordId]

            for col in range(len(self.fieldList)):
                field = self.fieldList[col]
                fieldName = field.name
                fieldType = field.type

                if fieldType == 'r':  #引用
                    value = record[fieldName]
                    reference_sheetName = value.split('.')[0]
                    reference_recordId = value.split('.')[1]

                    if reference_recordId.isdigit():
                        reference_recordId = int(reference_recordId)
                    #TODO 并不支持小数做主键

                    referenceSheet = SheetManager.getSheet(reference_sheetName)
                    reference_python_obj = referenceSheet.toPython()

                    record[fieldName] = reference_python_obj[reference_recordId]

    def toJSON(self,sheet_output_field=[]):
        json_obj = json.dumps(self.toPython(sheet_output_field), sort_keys=True, ensure_ascii=False)
        return json_obj

def openSheet(sh):
    if sh.nrows < 6:
        return None        
    
    return Sheet(sh)
