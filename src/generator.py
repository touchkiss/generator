__author__ = 'touchkiss'

import os

import MySQLdb
from jinja2 import Environment, PackageLoader


class TableInfo(object):
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.class_name = table_name.title().replace('_', '')
        self.title_name = table_name[0:1] + self.class_name[1:]
        self.columns = list({
                                'column_name': column[0],  # 字段名
                                'origin_type': self.get_origin_type(column[1]),  # 字段类型
                                'model_field_name': self.get_model_field_name(column[1]),  # 字段在django models中的类型名
                                'max_digits': self.get_max_digits(column[1]),  # decimal类型的长度
                                'decimal_places': self.get_decimal_places(column[1]),  # decimal类型的精度
                                'max_length': self.get_max_length(column[1]),  # varchar类型的长度
                                'nullable': column[3],  # null
                                'verbose_name': column[8],  # 备注
                                'pri': column[4] == 'PRI',  # 是否主键
                                'filter_name': self.get_filter_name(column[1]),  # 字段在django filter中的类型名
                                'serializer_field_name': self.get_serializer_field_name(column[1])
                                # 字段在django serializer中的类型名
                            } for column in columns)

    def get_origin_type(self, column_type):
        return column_type[0:column_type.find('(')]

    def get_model_field_name(self, column_type):
        type_name = column_type[0:column_type.find('(')]
        type_map = {
            'int': 'IntegerField',
            'varchar': 'CharField',
            'bigint': 'BigIntegerField',
            'decimal': 'DecimalField',
            'float': 'FloatField',
            'date': 'DateField'
        }
        return type_map.get(type_name)

    def get_max_digits(self, column_type):
        return column_type[column_type.find("(") + 1:column_type.find(",")] if column_type.find(
            "(") and self.get_model_field_name(column_type) == 'DecimalField' else ''

    def get_decimal_places(self, column_type):
        return column_type[column_type.find(",") + 1:column_type.find(")")] if column_type.find(
            ",") and self.get_model_field_name(column_type) == 'DecimalField' else ''

    def get_max_length(self, column_type):
        return column_type[column_type.find("(") + 1:column_type.find(")")] if column_type.find(
            "(") and self.get_model_field_name(column_type) == 'CharField' else ''

    def get_filter_name(self, column_type):
        if column_type != 'bit(1)' and column_type.find('(') > -1:
            column_type = column_type[0:column_type.index('(')]
        type_map = {
            'int': 'NumberFilter',
            'varchar': 'CharFilter',
            'bigint': 'NumberFilter',
            'decimal': 'NumberFilter',
            'float': 'NumberFilter',
            'datetime': 'DateTimeFilter',
            'bit(1)': 'BooleanFilter',
            'date': 'DateFilter',
            'time': 'TimeFilter'
        }
        return type_map.get(column_type)

    def get_serializer_field_name(self, column_type):
        column_type = column_type[0:column_type.find('(')]
        type_map = {
            'int': 'IntegerField',
            'varchar': 'CharField',
            'bigint': 'IntegerField',
            'decimal': 'DecimalField',
            'float': 'FloatField'
        }
        return type_map.get(column_type)


def check_file(fullpath):
    if not os.path.isfile(fullpath):  # 无文件时创建
        fd = open(fullpath, mode="w", encoding="utf-8")
        fd.close()


if __name__ == '__main__':

    rootpath = 'D:\\python_generated\\'
    env = Environment(loader=PackageLoader('generator', 'templates'))
    #要生成的表名列表
    tables = ['tb_user']
    # 数据库信息
    db = MySQLdb.connect("localhost", 'username', 'password', 'database', charset='utf8')
    cursor = db.cursor()
    tablesMap = {}
    ignoreGenerateTheseColumnsInVue = ['createtime', 'lastmodifytime']
    print('django routers:\n\n')
    for table in tables:
        path = table[3:table.rfind('_')]
        if tablesMap.get(path) is None:
            tablesMap[path] = []

        cursor.execute("show full columns from " + table)
        results = cursor.fetchall()
        tableinfo = TableInfo(table, results)
        tablesMap[path].append(tableinfo)
        url = 'router.register(r\'^' + path + '/' + tableinfo.class_name + '\', ' + tableinfo.class_name + 'ViewSet)'
        print(url)
    print('\n\n\n')
    print('vue routers and menu:\n\n')
    for path in tablesMap:
        tbs = tablesMap[path]
        fullpath = rootpath + 'python\\' + path
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)

        # 生成models
        template = env.get_template('models.template')
        fullpath = rootpath + 'python\\' + path + '\\models.py'
        check_file(fullpath)
        with open(fullpath, 'w', encoding='utf-8') as modelsfile:
            modelsfile.write(template.render(tables=tbs))
            modelsfile.close()

        # 生成filter
        template = env.get_template('filters.template')
        fullpath = rootpath + 'python\\' + path + '\\filters.py'
        check_file(fullpath)
        with open(fullpath, 'w', encoding='utf-8') as modelsfile:
            modelsfile.write(template.render(basepackage='base.', path=path, tables=tbs))
            modelsfile.close()

        # 生成serializer
        template = env.get_template('serializer.template')
        fullpath = rootpath + 'python\\' + path + '\\serializer.py'
        check_file(fullpath)
        with open(fullpath, 'w', encoding='utf-8') as modelsfile:
            modelsfile.write(template.render(tables=tbs))
            modelsfile.close()

        # 生成views
        template = env.get_template('views.template')
        fullpath = rootpath + 'python\\' + path + '\\views.py'
        check_file(fullpath)
        with open(fullpath, 'w', encoding='utf-8') as modelsfile:
            modelsfile.write(template.render(basepackage='base.', path=path, tables=tbs))
            modelsfile.close()

        fullpath = rootpath + 'vue\\' + path
        if not os.path.isdir(fullpath):
            os.makedirs(fullpath)
        # 生成element admin template menu list：
        print('{')
        print('    text: \'' + path + '\',')
        print('    type: \'ios-paper\',')
        print('    children: [')
        for table in tbs:
            print('        {')
            print('            type: \'ios-grid\',')
            print('            name: \'' + table.title_name + 'List\',')
            print('            text: \'' + table.title_name + '\'')
            print('        },')
        print('    ]')
        print('}\n\n\n')

        # 生成vue list
        template = env.get_template('list.vue')
        for table in tbs:
            fullpath = rootpath + 'vue\\' + path + '\\' + table.class_name + 'List.vue'
            check_file(fullpath)
            with open(fullpath, 'w', encoding='utf-8') as modelsfile:
                modelsfile.write(
                    template.render(ignoreGenerateTheseColumnsInVue=ignoreGenerateTheseColumnsInVue, path=path,
                                    table=table))
                modelsfile.close()

        # 生成vue item
        template = env.get_template('item.vue')
        for table in tbs:
            fullpath = rootpath + 'vue\\' + path + '\\' + table.class_name + 'Item.vue'
            check_file(fullpath)
            table.columns = list(
                column for column in table.columns if column['column_name'] not in ignoreGenerateTheseColumnsInVue)
            with open(fullpath, 'w', encoding='utf-8') as modelsfile:
                modelsfile.write(
                    template.render(path=path,
                                    table=table))
                modelsfile.close()
            # 生成vue routers
            print(table.title_name + 'List: {')
            print('    path: \'' + path + '/' + table.title_name + 'List\',')
            print('    name: \'' + table.title_name + 'List\',')
            print('    component: () => import(\'../views/' + path + '/' + table.class_name + 'List.vue\')')
            print('},')
