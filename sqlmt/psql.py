'''Useful modules for accessing PostgreSQL'''

import pandas as _pd
import pandas.util as _pu
import numpy as _np
import re as _re
import basemt.path as _p
import psycopg2 as _ps
import sqlalchemy.exc as _se
from basemt.bg_invoke import BgInvoke
from basemt.logging import dummy_scope
import pandasmt.csv as _mc

from .sql import *


# ----- debugging functions -----


def pg_get_locked_transactions(conn, schema=None):
    '''Obtains a dataframe representing transactions which have been locked by the server.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        connection engine
    schema : str or None
        If None, then all schemas are considered and not just the public schema. Else, scope down to a single schema.

    Returns
    -------
    pd.DataFrame
        A table containing the current backend transactions
    '''
    if schema is None:
        query_str = """
            SELECT
                t1.*, t2.relname, t3.nspname
              FROM pg_locks t1
                INNER JOIN pg_class t2 ON t1.relation=t2.oid
                INNER JOIN pg_namespace t3 ON t2.relnamespace=t3.oid
              WHERE NOT t2.relname ILIKE 'pg_%%'
            ;"""
    else:
        query_str = """
            SELECT
                t1.*, t2.relname, t3.nspname
              FROM pg_locks t1 
                INNER JOIN pg_class t2 ON t1.relation=t2.oid
                INNER JOIN pg_namespace t3 ON t2.relnamespace=t3.oid
              WHERE NOT t2.relname ILIKE 'pg_%%'
                AND t3.nspname = '{}'
            ;""".format(schema)
    return _pd.read_sql(query_str, conn)


def pg_cancel_backend(conn, pid):
    '''Cancels a backend transaction given its pid.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        connection engine
    pid : int
        the backend pid to be cancelled
    '''
    query_str = "SELECT pg_cancel_backend('{}');".format(pid)
    return _pd.read_sql(query_str, conn)


def pg_cancel_all_backends(conn, schema=None, logger=None):
    '''Cancels all backend transactions.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        connection engine
    schema : str or None
        If None, then all schemas are considered and not just the public schema. Else, scope down to a single schema.
    logger: logging.Logger or None
        logger for debugging
    '''
    df = pg_get_locked_transactions(conn, schema=schema)
    pids = df['pid'].drop_duplicates().tolist()
    for pid in pids:
        if logger:
            logger.info("Cancelling backend pid {}".format(pid))
        pg_cancel_backend(conn, pid)


# ----- functions dealing with sql queries to overcome OperationalError -----


def run_func(func, *args, nb_trials=3, logger=None, **kwargs):
    '''Attempt to run a function a number of times to overcome OperationalError exceptions.

    Parameters
    ----------
    func : function
        function to be invoked
    args : sequence
        arguments to be passed to the function
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    kwargs : dict
        keyword arguments to be passed to the function
    '''
    for x in range(nb_trials):
        try:
            return func(*args, **kwargs)
        except _se.ProgrammingError as e:
            raise
        except (_se.DatabaseError, _se.OperationalError, _ps.OperationalError) as e:
            if logger:
                with logger.scoped_warn("Ignored an exception raised by failed attempt {}/{} to execute `{}.{}()`".format(x+1, nb_trials, func.__module__, func.__name__)):
                    logger.warn_last_exception()
    raise RuntimeError("Attempted {} times to execute `{}.{}()` but failed.".format(
        nb_trials, func.__module__, func.__name__))


def read_sql(sql, conn, index_col=None, set_index_after=False, nb_trials=3, logger=None, **kwargs):
    """Read an SQL query with a number of trials to overcome OperationalError.

    Parameters
    ----------
    index_col: string or list of strings, optional, default: None
        Column(s) to set as index(MultiIndex). See pandas.read_sql().
    set_index_after : bool
        whether to set index specified by index_col via the pandas.read_sql() function or after the function has been invoked
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    kwargs : dict
        other keyword arguments to be passed directly to pandas.read_sql()

    pandas.read_sql:

    """ + _pd.read_sql.__doc__
    if index_col is None or not set_index_after:
        return run_func(_pd.read_sql, sql, conn, index_col=index_col, nb_trials=nb_trials, logger=logger, **kwargs)
    df = run_func(_pd.read_sql, sql, conn,
                  nb_trials=nb_trials, logger=logger, **kwargs)
    return df.set_index(index_col, drop=True)


def read_sql_query(sql, conn, index_col=None, set_index_after=False, nb_trials=3, logger=None, **kwargs):
    """Read an SQL query with a number of trials to overcome OperationalError.

    Parameters
    ----------
    index_col: string or list of strings, optional, default: None
        Column(s) to set as index(MultiIndex). See pandas.read_sql_query().
    set_index_after : bool
        whether to set index specified by index_col via the pandas.read_sql_query() function or after the function has been invoked
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    kwargs : dict
        other keyword arguments to be passed directly to pandas.read_sql_query()

    pandas.read_sql_query:

    """ + _pd.read_sql_query.__doc__
    if index_col is None or not set_index_after:
        return run_func(_pd.read_sql_query, sql, conn, index_col=index_col, nb_trials=nb_trials, logger=logger, **kwargs)
    df = run_func(_pd.read_sql_query, sql, conn,
                  nb_trials=nb_trials, logger=logger, **kwargs)
    return df.set_index(index_col, drop=True)


def read_sql_table(table_name, conn, nb_trials=3, logger=None, **kwargs):
    """Read an SQL table with a number of trials to overcome OperationalError.

    Parameters
    ----------
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    pandas.read_sql_table:

    """ + _pd.read_sql_table.__doc__
    return run_func(_pd.read_sql_table, table_name, conn, nb_trials=nb_trials, logger=logger, **kwargs)


def indices(df):
    '''Returns the list of named indices of the dataframe, ignoring any unnamed index.'''
    a = list(df.index.names)
    return a if a != [None] else []


def compliance_check(df):
    '''Checks if a dataframe is compliant to PSQL. It must has no index, or indices which do not match with any column. Raises ValueError when an error is encountered.'''
    for x in indices(df):
        if x in df.columns:
            raise ValueError(
                "Index '{}' appears as a non-primary column as well".format(x))


def to_sql(df, name, conn, schema=None, if_exists='fail', nb_trials=3, logger=None, **kwargs):
    """Writes records stored in a DataFrame to an SQL database, with a number of trials to overcome OperationalError.

    Parameters
    ----------
    df : pandas.DataFrame
        dataframe to be sent to the server
    conn : sqlalchemy.engine.Engine or sqlite3.Connection
        the connection engine
    schema : string, optional
        Specify the schema. If None, use default schema.
    if_exists : str
        what to do when the table exists. Beside all options available from pandas.to_sql(), a new option called 'gently_replace' is introduced, in which it will avoid dropping the table by trying to delete all entries and then inserting new entries. But it will only do so if the remote table contains exactly all the columns that the local dataframe has, and vice-versa.
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Raises
    ------
    sqlalchemy.exc.ProgrammingError if the local and remote frames do not have the same structure

    Notes
    -----
    The original pandas.DataFrame.to_sql() function does not turn any index into a primary key in PSQL. This function attempts to fix that problem. It takes as input a PSQL-compliant dataframe (see `compliance_check()`). It ignores any input `index` or `index_label` keyword. Instead, it considers 2 cases. If the dataframe's has an index or indices, then the tuple of all indices is turned into the primary key. If not, there is no primary key and no index is uploaded.

    pandas.DataFrame.to_sql:

    """ + _pd.DataFrame.to_sql.__doc__

    if kwargs:
        if 'index' in kwargs:
            raise ValueError(
                "The `sqlmt.psql.to_sql()` function does not accept `index` as a keyword.")
        if 'index_label' in kwargs:
            raise ValueError(
                "This `sqlmt.psql.to_sql()` function does not accept `index_label` as a keyword.")

    compliance_check(df)
    frame_sql_str = frame_sql(name, schema=schema)

    # if the remote frame does not exist, force `if_exists` to 'replace'
    if not frame_exists(name, conn, schema=schema, nb_trials=nb_trials, logger=logger):
        if_exists = 'replace'
    local_indices = indices(df)

    # not 'gently replace' case
    if if_exists != 'gently_replace':
        if not local_indices:
            return run_func(df.to_sql, name, conn, schema=schema, if_exists=if_exists, index=False, index_label=None, nb_trials=nb_trials, logger=logger, **kwargs)
        retval = run_func(df.to_sql, name, conn, schema=schema, if_exists=if_exists,
                          index=True, index_label=None, nb_trials=nb_trials, logger=logger, **kwargs)
        if if_exists == 'replace':
            exec_sql("ALTER TABLE {} ADD PRIMARY KEY ({});".format(frame_sql_str, ','.join(
                local_indices)), conn, nb_trials=nb_trials, logger=logger)
        return retval

    # the remaining section is the 'gently replace' case

    # remote indices
    remote_indices = list_primary_columns(
        name, conn, schema=schema, nb_trials=nb_trials, logger=logger)
    if local_indices != remote_indices:
        raise _se.ProgrammingError("SELECT * FROM {} LIMIT 1;".format(frame_sql_str), remote_indices,
                                   "Remote index '{}' differs from local index '{}'.".format(remote_indices, local_indices))

    # remote columns
    remote_columns = list_columns(
        name, conn, schema=schema, nb_trials=nb_trials, logger=logger)
    remote_columns = [x for x in remote_columns if not x in remote_indices]
    columns = list(df.columns)
    if columns != remote_columns:
        raise _se.ProgrammingError("SELECT * FROM {} LIMIT 1;".format(frame_sql_str), "matching non-primary fields",
                                   "Local columns '{}' differ from remote columns '{}'.".format(columns, remote_columns))

    exec_sql("DELETE FROM {};".format(frame_sql_str),
             conn, nb_trials=nb_trials, logger=logger)
    return run_func(df.to_sql, name, conn, schema=schema, if_exists='append', index=bool(local_indices), index_label=None, nb_trials=nb_trials, logger=logger, **kwargs)


def exec_sql(sql, conn, *args, nb_trials=3, logger=None, **kwargs):
    """Execute an SQL query with a number of trials to overcome OperationalError. See sqlalchemy.Engine.execute() for more details.

    Parameters
    ----------
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    """
    return run_func(conn.execute, sql, *args, nb_trials=nb_trials, logger=logger, **kwargs)


# ----- simple functions -----


def rename_schema(old_schema, new_schema, conn, nb_trials=3, logger=None):
    '''Renames a schema.

    Parameters
    ----------
    old_schema : str
        old schema name
    new_schema : str
        new schema name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    '''
    exec_sql('ALTER SCHEMA "{}" RENAME TO "{}";'.format(
        old_schema, new_schema), conn, nb_trials=nb_trials, logger=logger)


def list_views(conn, schema=None, nb_trials=3, logger=None):
    '''Lists all views of a given schema.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : list
        list of all view names
    '''
    if schema is None:
        query_str = "select distinct viewname from pg_views;"
    else:
        query_str = "select distinct viewname from pg_views where schemaname='{}';".format(
            schema)
    df = read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)
    return df['viewname'].tolist()


def list_matviews(conn, schema=None, nb_trials=3, logger=None):
    '''Lists all materialized views of a given schema.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : list
        list of all materialized view names
    '''
    if schema is None:
        schema = 'public'
    query_str = "select distinct matviewname from pg_matviews where schemaname='{}';".format(
        schema)
    df = read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)
    return df['matviewname'].tolist()


def list_frames(conn, schema=None, nb_trials=3, logger=None):
    '''Lists all dataframes (tables/views/materialized views) of a given schema.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : pd.DataFrame(columns=['name', 'type'])
        list of all dataframes of types {'table', 'view', 'matview'}
    '''
    data = []
    for item in list_tables(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        data.append((item, 'table'))
    for item in list_views(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        data.append((item, 'view'))
    for item in list_matviews(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        data.append((item, 'matview'))
    return _pd.DataFrame(data=data, columns=['name', 'type'])


def list_all_frames(conn, schema=None, nb_trials=3, logger=None):
    '''Lists all dataframes (tables/views/materialized views) across all schemas.

    Parameters
    ----------
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : pd.DataFrame(columns=['name', 'schema', 'type'])
        list of all dataframes of types {'table', 'view', 'matview'}
    '''
    dfs = []
    for schema in list_schemas(conn, nb_trials=nb_trials, logger=logger):
        df = list_frames(conn, schema=schema,
                         nb_trials=nb_trials, logger=logger)
        if len(df) > 0:
            df['schema'] = schema
            dfs.append(df)
    return _pd.concat(dfs, sort=False).reset_index(drop=True)


def get_frame_length(frame_name, conn, schema=None, nb_trials=3, logger=None):
    '''Gets the number of rows of a dataframes (tables/views/materialized views).

    Parameters
    ----------
    frame_name : str
        name of the dataframe
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : int
        number of rows

    Notes
    -----
    The dataframe must exist.
    '''
    frame_sql_str = frame_sql(frame_name, schema=schema)
    return read_sql_query("SELECT COUNT(*) a FROM {};".format(frame_sql_str), conn, nb_trials=nb_trials, logger=logger)['a'][0]


def get_frame_dependencies(frame_name, conn, schema=None, nb_trials=3, logger=None):
    '''Gets the list of all frames that depend on the given frame.
    '''
    query_str = """
        SELECT dependent_ns.nspname as dependent_schema
        , dependent_view.relname as dependent_view 
        , source_ns.nspname as source_schema
        , source_table.relname as source_table
        , pg_attribute.attname as column_name
        FROM pg_depend 
        JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid 
        JOIN pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid 
        JOIN pg_class as source_table ON pg_depend.refobjid = source_table.oid 
        JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid 
            AND pg_depend.refobjsubid = pg_attribute.attnum 
        JOIN pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
        JOIN pg_namespace source_ns ON source_ns.oid = source_table.relnamespace
        WHERE 
        source_ns.nspname = '{}'
        AND source_table.relname = '{}'
        AND pg_attribute.attnum > 0 
        ORDER BY 1,2;
    """.format('public' if schema is None else schema, frame_name)
    return read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)


def get_view_sql_code(view_name, conn, schema=None, nb_trials=3, logger=None):
    '''Gets the SQL string of a view.

    Parameters
    ----------
    view_name : str
        view name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    retval : str
        SQL query string defining the view
    '''
    return read_sql_query("SELECT pg_get_viewdef('{}', true) a".format(frame_sql(view_name, schema=schema)),
                          conn, nb_trials=nb_trials, logger=logger)['a'][0]


def rename_table(schema, old_table_name, new_table_name, conn, nb_trials=3, logger=None):
    '''Renames a table of a schema.

    Parameters
    ----------
    old_table_name : str
        old table name
    new_table_name : str
        new table name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    whatever exec_sql() returns
    '''
    frame_sql_str = frame_sql(old_table_name, schema=schema)
    exec_sql('ALTER TABLE {} RENAME TO "{}";'.format(frame_sql_str,
                                                     new_table_name), conn, nb_trials=nb_trials, logger=logger)


def drop_table(table_name, conn, schema=None, restrict=True, nb_trials=3, logger=None):
    '''Drops a table if it exists, with restrict or cascade options.

    Parameters
    ----------
    table_name : str
        table name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    restrict : bool
        If True, refuses to drop table if there is any object depending on it. Otherwise it is the 'cascade' option which allows you to remove those dependent objects together with the table automatically.
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    whatever exec_sql() returns
    '''
    frame_sql_str = frame_sql(table_name, schema=schema)
    query_str = "DROP TABLE IF EXISTS {} {};".format(
        frame_sql_str, "RESTRICT" if restrict else "CASCADE")
    return exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


def rename_view(old_view_name, new_view_name, conn, schema=None, nb_trials=3, logger=None):
    '''Renames a view of a schema.

    Parameters
    ----------
    old_view_name : str
        old view name
    new_view_name : str
        new view name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    '''
    frame_sql_str = frame_sql(old_view_name, schema=schema)
    exec_sql('ALTER VIEW {} RENAME TO "{}";'.format(frame_sql_str,
                                                    new_view_name), conn, nb_trials=nb_trials, logger=logger)


def drop_view(view_name, conn, schema=None, restrict=True, nb_trials=3, logger=None):
    '''Drops a view if it exists, with restrict or cascade options.

    Parameters
    ----------
    view_name : str
        view name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    restrict : bool
        If True, refuses to drop table if there is any object depending on it. Otherwise it is the 'cascade' option which allows you to remove those dependent objects together with the table automatically.
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    whatever exec_sql() returns
    '''
    frame_sql_str = frame_sql(view_name, schema=schema)
    query_str = "DROP VIEW IF EXISTS {} {};".format(
        frame_sql_str, "RESTRICT" if restrict else "CASCADE")
    return exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


def rename_matview(old_matview_name, new_matview_name, conn, schema=None, nb_trials=3, logger=None):
    '''Renames a materialized view of a schema.

    Parameters
    ----------
    old_matview_name : str
        old materialized view name
    new_matview_name : str
        new materialized view name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    '''
    frame_sql_str = frame_sql(old_matview_name, schema=schema)
    exec_sql('ALTER MATERIALIZED VIEW {} RENAME TO "{}";'.format(
        frame_sql_str, new_matview_name), conn, nb_trials=nb_trials, logger=logger)


def drop_matview(matview_name, conn, schema=None, restrict=True, nb_trials=3, logger=None):
    '''Drops a mateiralized view if it exists, with restrict or cascade options.

    Parameters
    ----------
    matview_name : str
        materialized view name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    restrict : bool
        If True, refuses to drop table if there is any object depending on it. Otherwise it is the 'cascade' option which allows you to remove those dependent objects together with the table automatically.
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    whatever exec_sql() returns
    '''
    frame_sql_str = frame_sql(matview_name, schema=schema)
    query_str = "DROP MATERIALIZED VIEW IF EXISTS {} {};".format(
        frame_sql_str, "RESTRICT" if restrict else "CASCADE")
    return exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


def frame_exists(frame_name, conn, schema=None, nb_trials=3, logger=None):
    '''Checks if a frame exists.

    Parameters
    ----------
    frame_name : str
        name of table or view
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    retval : bool
        whether a table or a view exists with the given name
    '''
    if frame_name in list_tables(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        return True
    if frame_name in list_views(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        return True
    return frame_name in list_matviews(conn, schema=schema, nb_trials=nb_trials, logger=logger)


def drop_frame(frame_name, conn, schema=None, restrict=True, nb_trials=3, logger=None):
    '''Drops a frame (table/view/mateiralized view) if it exists, with restrict or cascade options.

    Parameters
    ----------
    frame_name : str
        frame name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    restrict : bool
        If True, refuses to drop table if there is any object depending on it. Otherwise it is the 'cascade' option which allows you to remove those dependent objects together with the table automatically.
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    whatever exec_sql() returns, or False if the frame does not exist
    '''
    if frame_name in list_tables(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        return drop_table(frame_name, conn, schema=schema, restrict=restrict, nb_trials=nb_trials, logger=logger)
    if frame_name in list_views(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        return drop_view(frame_name, conn, schema=schema, restrict=restrict, nb_trials=nb_trials, logger=logger)
    if frame_name in list_matviews(conn, schema=schema, nb_trials=nb_trials, logger=logger):
        return drop_matview(frame_name, conn, schema=schema, restrict=restrict, nb_trials=nb_trials, logger=logger)
    return False


def list_columns_ext(table_name, conn, schema=None, nb_trials=3, logger=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
    table_name : str
        a valid table name returned from `list_tables()`
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : pandas.DataFrame
        a table of details of the columns
    '''
    if not frame_exists(table_name, conn, schema=schema, nb_trials=nb_trials, logger=logger):
        if schema is None:
            s = "Table or view with name '{}' does not exists.".format(
                table_name)
        else:
            s = "Table or view with name '{}' from schema '{}' does not exists.".format(
                table_name, schema)
        raise _ps.ProgrammingError(s)

    if schema is None:
        query_str = "select * from information_schema.columns where table_name='{}';".format(
            table_name)
    else:
        query_str = "select * from information_schema.columns where table_schema='{}' and table_name='{}';".format(
            schema, table_name)

    return read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)


def list_columns(table_name, conn, schema=None, nb_trials=3, logger=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
    table_name : str
        a valid table name returned from `list_tables()`
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    out : list of all column names
    '''
    return list_columns_ext(table_name, conn, schema=schema, nb_trials=nb_trials, logger=logger)['column_name'].tolist()


def list_primary_columns_ext(frame_name, conn, schema=None, nb_trials=3, logger=None):
    '''Lists all primary columns of a given frame of a given schema.

    Parameters
    ----------
    frame_name : str
        a valid table/view/matview name returned from `list_frames()`
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    pandas.DataFrame
        dataframe containing primary column names and data types
    '''
    frame_sql_str = frame_sql(frame_name, schema=schema)
    query_str = """
        SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type
        FROM   pg_index i
        JOIN   pg_attribute a ON a.attrelid = i.indrelid
                             AND a.attnum = ANY(i.indkey)
        WHERE  i.indrelid = '{}'::regclass
        AND    i.indisprimary;
        """.format(frame_sql_str)
    return read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)


def list_primary_columns(frame_name, conn, schema=None, nb_trials=3, logger=None):
    '''Lists all primary columns of a given frame of a given schema.

    Parameters
    ----------
    frame_name : str
        a valid table/view/matview name returned from `list_frames()`
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        a valid schema name returned from `list_schemas()`
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    list
        list of primary column names
    '''
    return list_primary_columns_ext(frame_name, conn, schema=schema, nb_trials=nb_trials, logger=logger)['attname'].tolist()


def rename_column(table_name, old_column_name, new_column_name, conn, schema=None, nb_trials=3, logger=None):
    '''Renames a column of a table.

    Parameters
    ----------
    table_name : str
        table name
    old_column_name : str
        old column name
    new_column_name : str
        new column name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        schema name
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    '''
    old_column_name = old_column_name.replace('%', '%%')
    if schema is None:
        query_str = 'ALTER TABLE "{}" RENAME COLUMN "{}" TO "{}";'.format(
            table_name, old_column_name, new_column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" RENAME COLUMN "{}" TO "{}";'.format(
            schema, table_name, old_column_name, new_column_name)
    exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


def drop_column(table_name, column_name, conn, schema=None, nb_trials=3, logger=None):
    '''Drops a column of a table.

    Parameters
    ----------
    table_name : str
        table name
    column_name : str
        column name
    conn : sqlalchemy.engine.base.Engine
        an sqlalchemy connection engine created by function `create_engine()`
    schema : str or None
        schema name
    nb_trials: int
        number of query trials
    logger: logging.Logger or None
        logger for debugging
    '''
    column_name = column_name.replace('%', '%%')
    if schema is None:
        query_str = 'ALTER TABLE "{}" DROP COLUMN "{}";'.format(
            table_name, column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" DROP COLUMN "{}";'.format(
            schema, table_name, column_name)
    exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


# ----- functions to synchronise between a local table and a remote table -----


def comparesync_table(cnx, csv_filepath, table_name, id_name, set_index_after=False, columns=['*'], schema=None, cond=None, reading_mode=True, nb_trials=3, logger=None):
    '''Compares a local CSV table with a remote PostgreSQL to find out which rows are the same or different.

    Parameters
    ----------
    cnx : sqlalchemy connectible
        connection to the PostgreSQL database
    csv_filepath : path
        path to the local CSV file
    table_name : str
        table name
    id_name : str
        index column name. Assumption is only one column for indexing for now.
    set_index_after : bool
        whether to set index specified by index_col via the pandas.read_sql() function or after the function has been invoked
    columns : list
        list of column names the function will read from, ignoring the remaining columns
    schema : str
        schema name, None means using the default one
    cond : str
        additional condition in selecting rows from the PostgreSQL table
    reading_mode : bool
        whether comparing is for reading or for writing
    nb_trials: int
        number of read_sql() trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    local_df : pandas.DataFrame(index=id_name, columns=[..., 'hash']) or None
        local dataframe loaded to memory, if it exists
    remote_md5_df : pandas.DataFrame(index=id_name, columns=['hash'])
        remote dataframe containing only the hash values
    same_keys : list
        list of keys identifying rows which appear in both tables and are the same
    diff_keys : list
        list of keys identifying rows which appear in both tables but are different
    local_only_keys : list
        list of keys containing rows which appear in the local table only
    remote_only_keys : list
        list of keys identifying rows which appear in the remote table only

    Note
    ----
    The 'hash' column of each table will be used to store and compare the hash values. If it does not exist, it will be generated automatically.
    The id_name field must uniquely identify each record in both tables. Duplicated keys in either table will be treated as diff_keys, so that hopefully next sync will fix them.
    '''
    frame_sql_str = frame_sql(table_name, schema=schema)

    with logger.scoped_debug("Comparing table: local '{}' <-> remote '{}'".format(csv_filepath, frame_sql_str), curly=False) if logger else dummy_scope:
        # make sure the folder containing the CSV file exists
        data_dir = _p.dirname(csv_filepath)
        _p.make_dirs(data_dir)

        # local_df
        if _p.exists(csv_filepath):
            try:
                local_df = _mc.read_csv(csv_filepath, index_col=id_name)
                local_dup_keys = local_df[local_df.index.duplicated(
                )].index.drop_duplicates().tolist()
                if len(local_df) == 0:
                    local_df = None
                elif 'hash' not in local_df.columns:
                    local_df['hash'] = _pu.hash_pandas_object(
                        local_df, index=False, hash_key='emerus_pham').astype(_np.int64)
            except ValueError:
                local_df = None
        else:
            local_df = None
            local_dup_keys = []

        # local_md5_df
        if local_df is not None:
            if logger:
                logger.debug(
                    "The local table has {} records.".format(len(local_df)))
            local_md5_df = local_df[['hash']]
        else:
            if logger:
                logger.debug("The local table is empty.")
            local_md5_df = _pd.DataFrame(index=_pd.Index(
                [], name=id_name), columns=['hash'])

        # remote_md5_df
        try:
            column_list = ','.join((table_name+'.'+x for x in columns))
            if columns == ['*']:
                text = 'textin(record_out('+column_list+'))'
            else:
                text = 'textin(record_out(('+column_list+')))'

            if 'hash' in list_columns(table_name, cnx, schema=schema, nb_trials=nb_trials, logger=logger):
                query_str = "select {}, hash from {}".format(
                    id_name, frame_sql_str)
            else:
                query_str = "select {}, md5({}) as hash from {}".format(
                    id_name, text, frame_sql_str)

            if cond is not None:
                query_str += " where " + cond
            # if logger:
                #logger.debug("Probing the remote table using hash query '{}'...".format(query_str))
            remote_md5_df = read_sql(query_str, cnx, index_col=id_name,
                                     set_index_after=set_index_after, nb_trials=nb_trials, logger=logger)
            remote_dup_keys = remote_md5_df[remote_md5_df.index.duplicated(
            )].index.drop_duplicates().tolist()
            if logger:
                logger.debug("The remote table has {} records.".format(
                    len(remote_md5_df)))
        # table does not exist or does not have the columns we wanted
        except (_se.ProgrammingError, _ps.ProgrammingError):
            if reading_mode:
                raise
            if logger:
                logger.warn("Ignoring the following exception.")
                logger.warn_last_exception()
            remote_md5_df = _pd.DataFrame(
                index=_pd.Index([], name=id_name), columns=['hash'])
            remote_dup_keys = []
            if logger:
                logger.debug("The remote table is empty.")

        # compare
        df = local_md5_df.join(remote_md5_df, how='outer',
                               lsuffix='_local', rsuffix='_remote')
        diff_keys = local_dup_keys + remote_dup_keys
        # remove all cases with duplicated keys
        df = df[~df.index.isin(diff_keys)]
        local_only_keys = df[df['hash_remote'].isnull()].index.tolist()
        df = df[df['hash_remote'].notnull()]
        remote_only_keys = df[df['hash_local'].isnull()].index.tolist()
        df = df[df['hash_local'].notnull()]
        # no need to drop_duplicates() as each key identifies maximum 1 row in each table
        same_keys = df[df['hash_local'] == df['hash_remote']].index.tolist()
        # no need to drop_duplicates() as each key identifies maximum 1 row in each table
        diff_keys += df[df['hash_local'] != df['hash_remote']].index.tolist()

        return local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys


def writesync_table(cnx, csv_filepath, table_name, id_name, schema=None, max_records_per_query=None, nb_trials=3, logger=None):
    '''Writes and updates a remote PostgreSQL table from a local CSV table by updating only rows which have been changed.

    Parameters
    ----------
    cnx : sqlalchemy connectible
        connection to the PostgreSQL database
    csv_filepath : path
        path to the local CSV file
    table_name : str
        table name
    id_name : str
        index column name. Assumption is only one column for indexing for now.
    schema : str
        schema name, None means using the default one
    bg_write_csv : bool
        whether to write the updated CSV file in a background thread
    max_records_per_query : int or None
        maximum number of records to be updated in each SQL query. If None, this will be dynamic to make sure each query runs about 5 minute.
    nb_trials: int
        number of read_sql() trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    df : pandas.DataFrame
        the data frame representing the local table

    Note
    ----
    The id_name column is written as the primary key of the remote table.
    See the comparesync_table() function for additional assumptions.
    '''
    frame_sql_str = frame_sql(table_name, schema=schema)
    with logger.scoped_debug("Writing table: local '{}' -> remote '{}'".format(csv_filepath, frame_sql_str), curly=False) if logger else dummy_scope:
        local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys = comparesync_table(
            cnx, csv_filepath, table_name, id_name, columns=['*'], schema=schema, cond=None, reading_mode=False, nb_trials=nb_trials, logger=None)

        # nothing changed, really!
        if len(diff_keys) == 0 and len(local_only_keys) == 0 and len(remote_only_keys) == 0:
            if logger:
                logger.debug(
                    "Both tables are the same and of length {}.".format(len(same_keys)))
            return local_df

        if logger:
            logger.debug("Keys: {} to retain, {} to delete, {} to update, {} to write as new.".format(
                len(same_keys), len(remote_only_keys), len(diff_keys), len(local_only_keys)))

        if local_df is None:  # delete remote table if there is no local table
            if logger:
                logger.debug(
                    "Deleting remote table {} if it exists because local table is empty...".format(frame_sql_str))
            query_str = "DROP TABLE IF EXISTS {};".format(frame_sql_str)
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)
            return local_df

        if len(local_df) < 128:  # a small dataset
            to_sql(local_df, cnx, table_name, schema=schema, if_exists='replace',
                   index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
            return local_df

        if len(same_keys) == 0:  # no record in the remote table
            if logger:
                logger.debug(
                    "Deleting table {} if it exists since there is no reusable remote record...".format(frame_sql_str))
            query_str = "DROP TABLE IF EXISTS {};".format(
                frame_sql_str)  # delete the remote table
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)

        record_cap = 128 if max_records_per_query is None else max_records_per_query

        # write those records as new
        if len(local_only_keys) > 0:
            df = local_df[local_df.index.isin(local_only_keys)]

            while len(df) > record_cap:
                df2 = df[:record_cap]
                df = df[record_cap:]
                if logger:
                    logger.debug(
                        "Inserting {} records, {} remaining...".format(len(df2), len(df)))

                start_time = _pd.Timestamp.utcnow()
                to_sql(df2, cnx, table_name, schema=schema, if_exists='append',
                       index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
                # elapsed time is in seconds
                elapsed_time = (_pd.Timestamp.utcnow() -
                                start_time).total_seconds()

                if max_records_per_query is None:
                    if elapsed_time > 300:  # too slow
                        record_cap = max(1, record_cap//2)
                    else:  # too fast
                        record_cap *= 2

            if logger:
                logger.debug("Inserting {} records.".format(len(df)))
            to_sql(df, cnx, table_name, schema=schema, if_exists='append',
                   index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)

        # remove redundant remote records
        id_list = diff_keys + remote_only_keys
        if len(id_list) > 0:
            id_list = ",".join(str(x) for x in id_list)
            query_str = "IF EXISTS({}) DELETE FROM {} WHERE {} IN ({}) END IF;".format(
                frame_sql_str, frame_sql_str, id_name, id_list)
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)

        # insert records that need modification
        if len(diff_keys) > 0:
            df = local_df[local_df.index.isin(diff_keys)]

            while len(df) > record_cap:
                df2 = df[:record_cap]
                df = df[record_cap:]
                if logger:
                    logger.debug(
                        "Modifying {} records, {} remaining...".format(len(df2), len(df)))

                start_time = _pd.Timestamp.utcnow()
                to_sql(df2, cnx, table_name, schema=schema, if_exists='append',
                       index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
                # elapsed time is in seconds
                elapsed_time = (_pd.Timestamp.utcnow() -
                                start_time).total_seconds()

                if max_records_per_query is None:
                    if elapsed_time > 300:  # too slow
                        record_cap = max(1, record_cap//2)
                    else:  # too fast
                        record_cap *= 2
            if logger:
                logger.debug("Modifying {} records.".format(len(df)))
            to_sql(df, cnx, table_name, schema=schema, if_exists='append',
                   index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)

    return local_df


def readsync_table(cnx, csv_filepath, table_name, id_name, set_index_after=False, columns=['*'], schema=None, cond=None, bg_write_csv=False, max_records_per_query=10240, nb_trials=3, logger=None):
    '''Reads and updates a local CSV table from a PostgreSQL table by updating only rows which have been changed.

    Parameters
    ----------
    cnx : sqlalchemy connectible
        connection to the PostgreSQL database
    csv_filepath : path
        path to the local CSV file
    table_name : str
        table name
    id_name : str
        index column name. Assumption is only one column for indexing for now.
    set_index_after : bool
        whether to set index specified by index_col via the pandas.read_sql() function or after the function has been invoked
    columns : list
        list of column names the function will read from, ignoring the remaining columns
    schema : str
        schema name, None means using the default one
    cond : str
        additional condition in selecting rows from the PostgreSQL table
    bg_write_csv : bool
        whether to write the updated CSV file in a background thread
    max_records_per_query : int or None
        maximum number of records to be updated in each SQL query. If None, this will be dynamic to make sure each query runs about 5 minute.
    nb_trials: int
        number of read_sql() trials
    logger: logging.Logger or None
        logger for debugging

    Returns
    -------
    df : pandas.DataFrame
        the data frame representing the read and updated table
    bg : BgInvoke or None, optional
        If bg_write_csv is True, this represents the background thread for writing the updated CSV file. If no background thread is needed, None is returned.

    Note
    ----
    See the comparesync_table() function for additional assumptions.
    '''
    frame_sql_str = frame_sql(table_name, schema=schema)
    with logger.scoped_debug("Reading table: local '{}' <- remote '{}'".format(csv_filepath, frame_sql_str), curly=False) if logger else dummy_scope:
        local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys = comparesync_table(
            cnx, csv_filepath, table_name, id_name, columns=columns, schema=schema, cond=cond, nb_trials=nb_trials, logger=None)

        # nothing changed, really!
        if len(diff_keys) == 0 and len(local_only_keys) == 0 and len(remote_only_keys) == 0:
            if logger:
                logger.debug(
                    "Both tables are the same and of length {}.".format(len(same_keys)))
            return local_df, None if bg_write_csv else local_df

        if logger:
            logger.debug("Keys: {} to retain, {} to delete, {} to update, {} to read as new.".format(
                len(same_keys), len(local_only_keys), len(diff_keys), len(remote_only_keys)))

        # read remote records
        id_list = diff_keys + remote_only_keys
        if len(id_list) > 0:
            column_list = ','.join((table_name+'.'+x for x in columns))

            new_md5_df = remote_md5_df[remote_md5_df.index.isin(id_list)]

            record_cap = 128 if max_records_per_query is None else max_records_per_query

            new_dfs = []
            while len(id_list) > 0:
                if len(id_list) > record_cap:
                    id_list2 = id_list[:record_cap]
                    id_list = id_list[record_cap:]
                else:
                    id_list2 = id_list
                    id_list = []
                if logger:
                    logger.debug("Fetching {} records with remaining {} records...".format(
                        len(id_list2), len(id_list)))
                query_str = "("+",".join((str(id) for id in id_list2))+")"
                query_str = "select {} from {} where {} in {}".format(
                    column_list, frame_sql_str, id_name, query_str)
                if cond is not None:
                    query_str += " and " + cond
                # if logger:
                    #logger.debug("  using query '{}',".format(query_str))

                start_time = _pd.Timestamp.utcnow()
                new_dfs.append(read_sql(query_str, cnx, index_col=id_name,
                                        set_index_after=set_index_after, nb_trials=nb_trials, logger=logger))
                # elapsed time is in seconds
                elapsed_time = (_pd.Timestamp.utcnow() -
                                start_time).total_seconds()

                if max_records_per_query is None:
                    if elapsed_time > 300:  # too slow
                        record_cap = max(1, record_cap//2)
                    else:  # too fast
                        record_cap *= 2

            new_df = _pd.concat(new_dfs)
            if not 'hash' in new_df.columns:
                new_df = new_df.join(new_md5_df)

            if len(new_md5_df) != len(new_df):
                if logger:
                    logger.debug("New dataframe:\n{}".format(str(new_df)))
                    logger.debug("Hash dataframe:\n{}".format(str(new_md5_df)))
                raise RuntimeError("Something must have gone wrong. Number of hashes {} != number of records {}.".format(
                    len(new_md5_df), len(new_df)))
        else:
            new_df = None  # nothing new

        # final df
        if len(same_keys) == 0:
            # former: empty dataframe
            df = local_df[0:0] if new_df is None else new_df
        else:
            local2_df = local_df[local_df.index.isin(same_keys)]
            df = local2_df if new_df is None else _pd.concat(
                [local2_df, new_df], sort=True)
        df.index = df.index.astype(new_md5_df.index.dtype)
        df = df.sort_index()

        # write back
        if logger:
            logger.debug("Saving all {} records to file...".format(len(df)))
        if bg_write_csv is True:
            bg = BgInvoke(_mc.to_csv, df, csv_filepath, index=True)
            return df, bg
        else:
            _mc.to_csv(df, csv_filepath, index=True)
            return df
