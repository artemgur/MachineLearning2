import pandas as pd
import sys
from clickhouse_driver import Client
import json


def connection_parameters_from_json(path):
    '''
    Получает параметры подключения к Clickhouse из файла в формате json, и преобразует их к виду, с которым работает Client.
    В бесплатной версии ngrok доменные имена непостоянны, поэтому параметры подключения непостоянны и параметры подключения не будут работать. Для запуска проекта можно
    обратиться за актуальными параметрами подключения к нам.
    '''
    with open(path) as json_file:
        data = json.load(json_file)
    url = data['host']
    split_result = url.split(':')
    data['host'] = split_result[0]
    data['port'] = split_result[1]
    return data


default_type_mapping = {'object': 'String', 'int64': 'UInt64', 'float64': 'Float64', 'datetime64[ns]': 'DateTime'}

class DfClient(Client):
    '''
    DfClient расширяет Client, дает возможность работать с Clickhouse с помощью Pandas.
    Объект этого класса создается так же, как объект класса Client. С DfClient есть возможность работать так же, как с Client.
    Для работы с Pandas нужно использовать методы, определенные ниже.
    У этого класса есть класс-наследник, дающий возможность работать с Clickhouse с помощью Dask.
    '''
    
    def columns(self, tablename):
    '''По имени таблицы возвращает список всех ее столбцов.'''
        result = self.execute('DESCRIBE TABLE ' + tablename)
        columnlist = list(map(lambda x: x[0], result))
        return columnlist


    def query(self, columns, query):
    '''
    Выполняет произвольный SQL-запрос query и возращает его результат в виде pd.DataFrame.
    columns – список названий столбцов возвращаемого pd.DataFrame.
    Метод используется как вспомогательный многими другими методами DfClient.
    '''
        result = self.execute(query)
        return pd.DataFrame(result, columns=columns)
        

    def select(self, tablename, columns, where_and_after=''):
    '''
    Выполняет SELECT-запрос и возвращает его результат в виде pd.DataFrame.
    tablename – имя таблицы.
    columns – список столбцов, которые нужно получить.
    where_and_after – часть запроса, которая следует после FROM {tablename}. Например, WHERE, LIMIT. Значение по-умолчанию – пустая строка.
    '''
        columns_string = ', '.join(columns)
        return self.query(columns, f'SELECT {columns_string} FROM {tablename} {where_and_after}')

    def select_all_columns(self, tablename, where_and_after=''):
    '''
    Выполняет SELECT-запрос, запрашивая все столбцы таблицы. Остальное аналогично методу select.
    '''
        # Просто * не подойдет, так как не включает столбцы Materialized и Alias
        columns = self.columns(tablename)
        return self.select(tablename, columns, where_and_after)

    def insert(self, tablename, df):
    '''
    Выполняет INSERT-запрос, вставляет в таблицу с именем tablename pd.DataFrame df.
    Типы и порядок столбцов pd.DataFrame должны соответствовать таблице, в которую происходит вставка. Названия столбцов игнорируются.
    '''
        tuples = df.to_dict(orient='records')
        self.execute(f'INSERT INTO {tablename} VALUES', tuples)

    def insert_to_new_table(self, tablename, df, order_key=None, engine='MergeTree()', type_mapping=default_type_mapping):
    '''
    Создает таблицу с именем tablename, соответствующую по структуре pd.DataFrame df и записывает df в эту таблицу.
    order_key – столбец, по которому будет отсортирована таблица. По умолчанию – первый столбец pd.DataFrame.
    engine – движок таблицы. По умолчанию – MergeTree(), наиболее универсальный и функциональный движок.
    type_mapping – соответствие между типами Pandas и типами Clickhouse.
    '''
        if order_key is None:
            order_key = df.columns[0]
        query = f'CREATE TABLE {tablename} ('
        for column, dtype in df.dtypes.iteritems():
            query += f'{column} {type_mapping[str(dtype)]},'
        query = query[:-1] # Удаление последнего символа (лишней запятой)
        query += f') ENGINE = {engine} ORDER BY {order_key}'
        self.execute(query)
        self.insert(tablename, df)

    def drop(self, tablename):
    '''Удаляет таблицу с именем tablename.'''
        self.execute('DROP TABLE ' + tablename)

    def truncate(self, tablename):
    '''
    Удаляет все данные из таблицы с именем tablename.
    Для удаления используется TRUNCATE, поэтому удаление происходит быстро.
    '''
        self.execute('TRUNCATE TABLE ' + tablename)
    
    def create_column(self, tablename, column_name, type, default_expression, column_type='ALIAS'):
    '''
    Создает столбец с названием column_name в таблице tablename.
    type – тип данных Clickhouse столбца.
    default_expression – выражение, с помощью которого вычисляются значения столбца. В выражении можно использовать названия других столбцов.
    column_type – тип столбца. По умолчанию – ALIAS.
    '''
        self.execute(f'ALTER TABLE {tablename} ADD COLUMN {column_name} {type} {column_type} {default_expression}')
