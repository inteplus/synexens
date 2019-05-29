import sqlalchemy as _sa

def table_sql(table_name, schema_name=None):
    return table_name if schema_name is None else '{}.{}'.format(schema_name, table_name)

def list_schemas(conn):
    '''Lists all schemas.

    Parameters
    ----------
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`

    Returns
    -------
        out : list
            list of all schema names
    '''
    return _sa.inspect(conn).get_schema_names()


def list_tables(schema_name, conn):
    '''Lists all tables of a given schema.

    Parameters
    ----------
        schema_name : str
            a valid schema name returned from `list_schemas()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`

    Returns
    -------
        out : list
            list of all table names
    '''
    return conn.table_names(schema=schema_name)


