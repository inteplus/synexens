'''Useful modules for accessing PostgreSQL'''

import pandas as _pd
import re as _re
import base.path as _p
from basemt.bg_invoke import BgInvoke
import dataframemt.csv as _mc

from dataframemt.sql import *


# MT-TODO: any function below this line needs testing


def list_views(db_name, conn):
    '''Lists all views of a given database.

    Parameters
    ----------
        db_name : str
            a valid dtabase name returned from `show_databases()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`

    Returns
    -------
        out : list
            list of all view names
    '''
    df = _pd.read_sql_query("SHOW FULL TABLES IN '{}' WHERE TABLE_TYPE LIKE 'VIEW';".format(db_name), conn)
    return df['viewname'].tolist()


def rename_table(old_table_name, new_table_name, conn, schema_name=None):
    '''Renames a table of a schema.

    Parameters
    ----------
        old_table_name : str
            old table name
        new_table_name : str
            new table name
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
            schema name
    '''
    if schema_name is None:
        query_str = 'ALTER TABLE "{}" RENAME TO "{}";'.format(old_table_name, new_table_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" RENAME TO "{}";'.format(schema_name, old_table_name, new_table_name)
    conn.execute(query_str)


def list_columns_ext(table_name, conn, schema_name=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
        schema_name : str
            a valid schema name returned from `list_schemas()`
        table_name : str
            a valid table name returned from `list_tables()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
            schema name

    Returns
    -------
        out : pandas.DataFrame
            a table of details of the columns
    '''
    if schema_name is None:
        query_str = "select * from information_schema.columns where table_name='{}';".format(table_name)
    else:
        query_str = "select * from information_schema.columns where table_schema='{}' and table_name='{}';".format(schema_name, table_name)
    return _pd.read_sql_query(query_str, conn)


def list_columns(table_name, conn, schema_name=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
        table_name : str
            a valid table name returned from `list_tables()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
            schema name

    Returns
    -------
        out : list of all column names
    '''
    return list_columns_ext(table_name, conn, schema_name=schema_name)['column_name'].tolist()


def rename_column(table_name, old_column_name, new_column_name, conn, schema_name=None):
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
        schema_name : str or None
            schema name
    '''
    old_column_name = old_column_name.replace('%', '%%')
    if schema_name is None:
        query_str = 'ALTER TABLE "{}" RENAME COLUMN "{}" TO "{}";'.format(table_name, old_column_name, new_column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" RENAME COLUMN "{}" TO "{}";'.format(schema_name, table_name, old_column_name, new_column_name)
    conn.execute(query_str)


def drop_column(table_name, column_name, conn, schema_name=None):
    '''Drops a column of a table.

    Parameters
    ----------
        table_name : str
            table name
        column_name : str
            column name
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
            schema name
    '''
    column_name = column_name.replace('%', '%%')
    if schema_name is None:
        query_str = 'ALTER TABLE "{}" DROP COLUMN "{}";'.format(table_name, column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" DROP COLUMN "{}";'.format(schema_name, table_name, column_name)
    conn.execute(query_str)


def readsync_table(cnx, csv_filepath, table_name, id_name, columns=['*'], schema_name=None, cond=None, bg_write_csv=False, max_records_per_query=10240):
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
        columns : list
            list of column names the function will read from, ignoring the remaining columns
        schema_name : str
            schema name, None means using the default one
        cond : str
            additional condition in selecting rows from the PostgreSQL table
        bg_write_csv : bool
            whether to write the updated CSV file in a background thread
        max_records_per_query : int or None
            maximum number of records to be updated in each SQL query
        logger: logging.Logger or None
            logger for debugging

    Returns
    -------
        df : pandas.DataFrame
            the data frame representing the read and updated table
        bg : BgInvoke, optional
            If bg_write_csv is True, this represents the background thread for writing the updated CSV file

    Note
    ----
        The PSQL table must not contain a column named 'hash' as it will be used to store the hash values.
    '''
    if logger:
        logger.debug("Table {}".format(csv_filepath))

    # make sure the folder containing the CSV file exists
    data_dir = _p.dirname(csv_filepath)
    _p.make_dirs(data_dir)

    # old_df
    if _p.exists(csv_filepath):
        try:
            old_df = _mc.read_csv(csv_filepath, index_col=id_name)
            if 'hash' not in old_df.columns or len(old_df) == 0:
                old_df = None
        except ValueError:
            old_df = None
    else:
        old_df = None
    if old_df is not None:
        if logger:
            logger.debug("  has {} records previously,".format(len(old_df)))
    else:
        if logger:
            logger.debug("  is empty previously,")

    table_sql_str = table_sql(table_name, schema_name=schema_name)

    # new_md5_df and old_df
    column_list = ','.join((table_name+'.'+x for x in columns))
    if columns == ['*']:
        text = 'textin(record_out('+column_list+'))'
    else:
        text = 'textin(record_out(('+column_list+')))'
    query_str = "select {}, md5({}) as hash from {}".format(id_name, text, table_sql_str)
    if cond is not None:
        query_str += " where " + cond
    if logger:
        logger.debug("  using hash query '{}',".format(query_str))
    new_md5_df = _pd.read_sql(query_str, cnx, index_col=id_name)
    new_md5_df.columns = ['new_hash']
    if old_df is not None:
        old_md5_df = new_md5_df.join(old_df[['hash']], how='inner') # records with both old and new md5
        old_md5_df = old_md5_df[old_md5_df['hash'] == old_md5_df['new_hash']][['hash']] # keep those where the two md5s are the same
        old_df = old_md5_df.drop('hash', axis=1).join(old_df, how='left') # filter old_df
        new_md5_df = new_md5_df.join(old_md5_df, how='left') # preparation
        new_md5_df = new_md5_df[new_md5_df['hash'].isnull()][['new_hash']] # keep records in new_md5_df but not in old_df
    if len(new_md5_df) == 0:
        if logger:
            logger.debug("  retains all {} records.".format(0 if old_df is None else len(old_df)))
        return (old_df, None) if bg_write_csv else old_df
    new_md5_df.columns = ['hash']
    if old_df is not None:
        if logger:
            logger.debug("  retains {} records,".format(len(old_df)))

    # new_df
    id_list = new_md5_df.reset_index(drop=False)[id_name].drop_duplicates().tolist()
    if max_records_per_query is None or len(id_list) < max_records_per_query:
        if logger:
            logger.debug("  updates {} records,".format(len(id_list)))
        query_str = "("+",".join((str(id) for id in id_list))+")"
        query_str = "select {} from {} where {} in {}".format(column_list, table_sql_str, id_name, query_str)
        if cond is not None:
            query_str += " and " + cond
        if logger:
            logger.debug("    using query '{}',".format(query_str))
        new_df = _pd.read_sql(query_str, cnx, index_col=id_name)
        #if logger:
            #logger.debug(new_df)
            #logger.debug(new_md5_df)
    else:
        if logger:
            logger.debug("  will update {} records,".format(len(id_list)))
        new_dfs = []
        while len(id_list) > 0:
            if len(id_list) > max_records_per_query:
                id_list2 = id_list[:max_records_per_query]
                id_list = id_list[max_records_per_query:]
            else:
                id_list2 = id_list
                id_list = []
            if logger:
                logger.debug("  updates {} records with remaining {} records,".format(len(id_list2), len(id_list)))
            query_str = "("+",".join((str(id) for id in id_list2))+")"
            query_str = "select {} from {} where {} in {}".format(column_list, table_sql_str, id_name, query_str)
            if cond is not None:
                query_str += " and " + cond
            if logger:
                logger.debug("    using query '{}',".format(query_str))
            new_dfs.append(_pd.read_sql(query_str, cnx, index_col=id_name))
        new_df = _pd.concat(new_dfs)
    new_df = new_df.join(new_md5_df)

    # final df
    df = new_df if old_df is None else _pd.concat([old_df, new_df], sort=True).sort_index()
    df.index = df.index.astype(new_md5_df.index.dtype)

    # write back
    if logger:
        logger.debug("  writes {} records to file.".format(len(df)))
    if bg_write_csv is True:
        bg = BgInvoke(_mc.to_csv, df, csv_filepath, index=True)
        return df, bg
    else:
        _mc.to_csv(df, csv_filepath, index=True)
        return df

