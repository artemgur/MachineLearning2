import pandas as pd
import sys
from clickhouse_driver import Client
import json
import itertools
import dask.dataframe as dd

from dfclient import DfClient

# Source: https://stackoverflow.com/questions/8991506/iterate-an-iterator-by-chunks-of-n-in-python
def grouper(iterable, n):
    '''
    Группирует iterable в n групп.
    Вспомогательный метод DaskClient. Нужен для того, чтобы не загружать все данные сразу, а обрабатывать их по блокам.
    '''
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk

class DaskClient(DfClient):
    '''
    Класс-наследник DfClient, дающий возможность работать с Clickhouse с помощью Dask.
    Используется так же, как DfClient.
    К Dask адаптированы все методы DfClient, кроме insert и insert_to_new_table.
    Методы insert и insert_to_new_table на данный момент не адаптированы к Dask, так как в проекте для Dask они не пригодились. При необходимости это можно сделать в будущем.
    '''
    def query(self, columns, query):
    '''
    Выполняет произвольный SQL-запрос query и возращает его результат в виде dd.DataFrame.
    columns – список названий столбцов возвращаемого dd.DataFrame.
    Метод используется как вспомогательный многими другими методами DfClient, поэтому его адаптация к Dask автоматически адаптирует к Dask большую часть методов DfClient.
    Метод не загружает все данные из таблицы сразу, а обрабатывает их по блокам.
    '''
        block_size = 10000
        settings = {'max_block_size': block_size}
        rows_iter = self.execute_iter(query, settings=settings)
        result = None
        for chunk in grouper(rows_iter, block_size):
            df = pd.DataFrame(chunk, columns=columns)
            if result is None:
                result = dd.from_pandas(df, chunksize=block_size)
            else:
                result = result.concat([df])
        return result
