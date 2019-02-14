import datetime as dt

from constants import FIELDS


def get_table(ifs, tablename, query={}, fields=[]):
    now = dt.datetime.now()
    row_count = ifs.DataService('count', tablename, {})
    print(f'Pulling {tablename}: {row_count} records')
    lookup_fields = []
    if not fields:
        lookup_fields += FIELDS[tablename][:]
    else:
        lookup_fields = fields
    table = []
    page = 0
    while True:
        table_page = ifs.DataService('query',
                                     tablename,
                                     1000,
                                     page,
                                     query,
                                     lookup_fields)
        if isinstance(table_page, tuple):
            raise ValueError(
                f'InfusionsoftAPIError: Error getting '
                f'{tablename} table {table_page[1]}')
        if not table_page:
            break
        table += table_page
        page += 1
    print(f'{tablename} returned {len(table)} records')
    print(dt.datetime.now() - now)
    return table