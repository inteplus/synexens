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
import dataframemt.csv as _mc

from dataframemt.sql import *


# ----- functions dealing with sql queries to overcome OperationalError -----


def run_func(func, *args, nb_trials=3, logger=None, **kwargs):
    '''Attempt to run a function a number of times to overcome OperationalError exceptions.

    :Parameters:
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
        except (_se.DatabaseError, _se.OperationalError, _ps.OperationalError) as e:
            if logger:
                with logger.scoped_warn("Ignored an exception raised by failed attempt {}/{} to execute `{}.{}()`".format(x+1, nb_trials, func.__module__, func.__name__)):
                    logger.warn_last_exception()
    raise RuntimeError("Attempted {} times to execute `{}.{}()` but failed.".format(nb_trials, func.__module__, func.__name__))


def read_sql(sql, conn, nb_trials=3, logger=None, **kwargs):
    """Read an SQL query with a number of trials to overcome OperationalError.

    :Aditional Parameters:
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    pandas.read_sql:

    """ + _pd.read_sql.__doc__
    return run_func(_pd.read_sql, sql, conn, nb_trials=nb_trials, logger=logger, **kwargs)


def read_sql_query(sql, conn, nb_trials=3, logger=None, **kwargs):
    """Read an SQL query with a number of trials to overcome OperationalError.

    :Aditional Parameters:
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    pandas.read_sql_query:

    """ + _pd.read_sql_query.__doc__
    return run_func(_pd.read_sql_query, sql, conn, nb_trials=nb_trials, logger=logger, **kwargs)


def read_sql_table(table_name, conn, nb_trials=3, logger=None, **kwargs):
    """Read an SQL table with a number of trials to overcome OperationalError.

    :Aditional Parameters:
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    pandas.read_sql_table:

    """ + _pd.read_sql_table.__doc__
    return run_func(_pd.read_sql_table, table_name, conn, nb_trials=nb_trials, logger=logger, **kwargs)


def to_sql(df, conn, name, nb_trials=3, logger=None, **kwargs):
    """Writes records stored in a DataFrame to an SQL database, with a number of trials to overcome OperationalError.

    :Aditional Parameters:
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    pandas.DataFrame.to_sql:

    """ + _pd.DataFrame.to_sql.__doc__
    return run_func(df.to_sql, name, conn, nb_trials=nb_trials, logger=logger, **kwargs)


def exec_sql(sql, conn, *args, nb_trials=3, logger=None, **kwargs):
    """Execute an SQL query with a number of trials to overcome OperationalError. See sqlalchemy.Engine.execute() for more details.

    :Aditional Parameters:
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    """
    return run_func(conn.execute, sql, *args, nb_trials=nb_trials, logger=logger, **kwargs)


# ----- simple functions -----


def rename_schema(old_schema_name, new_schema_name, conn, nb_trials=3, logger=None):
    '''Renames a schema.

    Parameters
    ----------
        old_schema_name : str
            old schema name
        new_schema_name : str
            new schema name
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging
    '''
    exec_sql('ALTER SCHEMA "{}" RENAME TO "{}";'.format(old_schema_name, new_schema_name), conn, nb_trials=nb_trials, logger=logger)


def list_views(conn, schema_name=None, nb_trials=3, logger=None):
    '''Lists all views of a given schema.

    Parameters
    ----------
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
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
    if schema_name is None:
        query_str = "select distinct viewname from pg_views;"
    else:
        query_str = "select distinct viewname from pg_views where schemaname='{}';".format(schema_name)
    df = read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)
    return df['viewname'].tolist()


def rename_table(schema_name, old_table_name, new_table_name, conn, nb_trials=3, logger=None):
    '''Renames a table of a schema.

    Parameters
    ----------
        schema_name : str
            schema name
        old_table_name : str
            old table name
        new_table_name : str
            new table name
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging
    '''
    exec_sql('ALTER TABLE "{}"."{}" RENAME TO "{}";'.format(schema_name, old_table_name, new_table_name), conn, nb_trials=nb_trials, logger=logger)


def list_columns_ext(table_name, conn, schema_name=None, nb_trials=3, logger=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
        table_name : str
            a valid table name returned from `list_tables()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
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
    if schema_name is None:
        query_str = "select * from information_schema.columns where table_name='{}';".format(table_name)
    else:
        query_str = "select * from information_schema.columns where table_schema='{}' and table_name='{}';".format(schema_name, table_name)
    return read_sql_query(query_str, conn, nb_trials=nb_trials, logger=logger)


def list_columns(table_name, conn, schema_name=None, nb_trials=3, logger=None):
    '''Lists all columns of a given table of a given schema.

    Parameters
    ----------
        table_name : str
            a valid table name returned from `list_tables()`
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema_name : str or None
            a valid schema name returned from `list_schemas()`
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    Returns
    -------
        out : list of all column names
    '''
    return list_columns_ext(table_name, conn, schema_name=schema_name, nb_trials=nb_trials, logger=logger)['column_name'].tolist()


def rename_column(table_name, old_column_name, new_column_name, conn, schema_name=None, nb_trials=3, logger=None):
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
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging
    '''
    old_column_name = old_column_name.replace('%', '%%')
    if schema_name is None:
        query_str = 'ALTER TABLE "{}" RENAME COLUMN "{}" TO "{}";'.format(table_name, old_column_name, new_column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" RENAME COLUMN "{}" TO "{}";'.format(schema_name, table_name, old_column_name, new_column_name)
    exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


def drop_column(table_name, column_name, conn, schema_name=None, nb_trials=3, logger=None):
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
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging
    '''
    column_name = column_name.replace('%', '%%')
    if schema_name is None:
        query_str = 'ALTER TABLE "{}" DROP COLUMN "{}";'.format(table_name, column_name)
    else:
        query_str = 'ALTER TABLE "{}"."{}" DROP COLUMN "{}";'.format(schema_name, table_name, column_name)
    exec_sql(query_str, conn, nb_trials=nb_trials, logger=logger)


# ----- functions to synchronise between a local table and a remote table -----


def comparesync_table(cnx, csv_filepath, table_name, id_name, columns=['*'], schema_name=None, cond=None, reading_mode=True, nb_trials=3, logger=None):
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
        columns : list
            list of column names the function will read from, ignoring the remaining columns
        schema_name : str
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
    table_sql_str = table_sql(table_name, schema_name=schema_name)

    with logger.scoped_debug("Comparing table: local '{}' <-> remote '{}'".format(csv_filepath, table_sql_str), curly=False) if logger else dummy_scope:
        # make sure the folder containing the CSV file exists
        data_dir = _p.dirname(csv_filepath)
        _p.make_dirs(data_dir)

        # local_df
        if _p.exists(csv_filepath):
            try:
                local_df = _mc.read_csv(csv_filepath, index_col=id_name)
                local_dup_keys = local_df[local_df.index.duplicated()].index.drop_duplicates().tolist()
                if len(local_df) == 0:
                    local_df = None
                elif 'hash' not in local_df.columns:
                    local_df['hash'] = _pu.hash_pandas_object(local_df, index=False, hash_key='emerus_pham').astype(_np.int64)
            except ValueError:
                local_df = None
        else:
            local_df = None
            local_dup_keys = []

        # local_md5_df
        if local_df is not None:
            if logger:
                logger.debug("The local table has {} records.".format(len(local_df)))
            local_md5_df = local_df[['hash']]
        else:
            if logger:
                logger.debug("The local table is empty.")
            local_md5_df = _pd.DataFrame(index=_pd.Index([], name=id_name), columns=['hash'])

        # remote_md5_df
        try:
            column_list = ','.join((table_name+'.'+x for x in columns))
            if columns == ['*']:
                text = 'textin(record_out('+column_list+'))'
            else:
                text = 'textin(record_out(('+column_list+')))'

            if 'hash' in list_columns(table_name, cnx, schema_name=schema_name, nb_trials=nb_trials, logger=logger):
                query_str = "select {}, hash from {}".format(id_name, table_sql_str)
            else:
                query_str = "select {}, md5({}) as hash from {}".format(id_name, text, table_sql_str)

            if cond is not None:
                query_str += " where " + cond
            #if logger:
                #logger.debug("Probing the remote table using hash query '{}'...".format(query_str))
            remote_md5_df = read_sql(query_str, cnx, index_col=id_name, nb_trials=nb_trials, logger=logger)
            remote_dup_keys = remote_md5_df[remote_md5_df.index.duplicated()].index.drop_duplicates().tolist()
            if logger:
                logger.debug("The remote table has {} records.".format(len(remote_md5_df)))
        except (_se.ProgrammingError, _ps.ProgrammingError): # table does not exist or does not have the columns we wanted
            if logger:
                logger.warn("Ignoring the following exception.")
                logger.warn_last_exception()
            remote_md5_df = _pd.DataFrame(index=_pd.Index([], name=id_name), columns=['hash'])
            remote_dup_keys = []
            if logger:
                logger.debug("The remote table is empty.")

        # compare
        df = local_md5_df.join(remote_md5_df, how='outer', lsuffix='_local', rsuffix='_remote')
        diff_keys = local_dup_keys + remote_dup_keys
        df = df[~df.index.isin(diff_keys)] # remove all cases with duplicated keys
        local_only_keys = df[df['hash_remote'].isnull()].index.tolist()
        df = df[df['hash_remote'].notnull()]
        remote_only_keys = df[df['hash_local'].isnull()].index.tolist()
        df = df[df['hash_local'].notnull()]
        same_keys = df[df['hash_local'] == df['hash_remote']].index.tolist() # no need to drop_duplicates() as each key identifies maximum 1 row in each table
        diff_keys += df[df['hash_local'] != df['hash_remote']].index.tolist() # no need to drop_duplicates() as each key identifies maximum 1 row in each table

        return local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys


def writesync_table(cnx, csv_filepath, table_name, id_name, schema_name=None, max_records_per_query=None, nb_trials=3, logger=None):
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
        schema_name : str
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
    table_sql_str = table_sql(table_name, schema_name=schema_name)
    with logger.scoped_debug("Writing table: local '{}' -> remote '{}'".format(csv_filepath, table_sql_str), curly=False) if logger else dummy_scope:
        local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys = comparesync_table(cnx, csv_filepath, table_name, id_name, columns=['*'], schema_name=schema_name, cond=None, reading_mode=False, nb_trials=nb_trials, logger=None)

        if len(diff_keys) == 0 and len(local_only_keys) == 0 and len(remote_only_keys) == 0: # nothing changed, really!
            if logger:
                logger.debug("Both tables are the same and of length {}.".format(len(same_keys)))
            return local_df

        if logger:
            logger.debug("Keys: {} to retain, {} to delete, {} to update, {} to write as new.".format(len(same_keys), len(remote_only_keys), len(diff_keys), len(local_only_keys)))

        if local_df is None: # delete remote table if there is no local table
            if logger:
                logger.debug("Deleting remote table {} if it exists because local table is empty...".format(table_sql_str))
            query_str = "DROP TABLE IF EXISTS {};".format(table_sql_str)
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)
            return local_df

        if len(local_df) < 128: # a small dataset
            to_sql(local_df, cnx, table_name, schema=schema_name, if_exists='replace', index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
            return local_df

        if len(same_keys) == 0: # no record in the remote table
            if logger:
                logger.debug("Deleting table {} if it exists since there is no reusable remote record...".format(table_sql_str))
            query_str = "DROP TABLE IF EXISTS {};".format(table_sql_str) # delete the remote table
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)

        record_cap = 128 if max_records_per_query is None else max_records_per_query

        # write those records as new
        if len(local_only_keys) > 0:
            df = local_df[local_df.index.isin(local_only_keys)]

            while len(df) > record_cap:
                df2 = df[:record_cap]
                df = df[record_cap:]
                if logger:
                    logger.debug("Inserting {} records, {} remaining...".format(len(df2), len(df)))

                start_time = _pd.Timestamp.utcnow()
                to_sql(df2, cnx, table_name, schema=schema_name, if_exists='append', index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
                elapsed_time = (_pd.Timestamp.utcnow() - start_time).total_seconds() # elapsed time is in seconds

                if max_records_per_query is None:
                    if elapsed_time > 300: # too slow
                        record_cap = max(1, record_cap//2)
                    else: # too fast
                        record_cap *= 2

            if logger:
                logger.debug("Inserting {} records.".format(len(df)))
            to_sql(df, cnx, table_name, schema=schema_name, if_exists='append', index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)

        # remove redundant remote records
        id_list = diff_keys + remote_only_keys
        if len(id_list) > 0:
            id_list = ",".join(str(x) for x in id_list)
            query_str = "DELETE FROM {} WHERE {} IN ({});".format(table_sql_str, id_name, id_list)
            exec_sql(query_str, cnx, nb_trials=nb_trials, logger=logger)

        # insert records that need modification
        if len(diff_keys) > 0:
            df = local_df[local_df.index.isin(diff_keys)]

            while len(df) > record_cap:
                df2 = df[:record_cap]
                df = df[record_cap:]
                if logger:
                    logger.debug("Modifying {} records, {} remaining...".format(len(df2), len(df)))

                start_time = _pd.Timestamp.utcnow()
                to_sql(df2, cnx, table_name, schema=schema_name, if_exists='append', index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)
                elapsed_time = (_pd.Timestamp.utcnow() - start_time).total_seconds() # elapsed time is in seconds

                if max_records_per_query is None:
                    if elapsed_time > 300: # too slow
                        record_cap = max(1, record_cap//2)
                    else: # too fast
                        record_cap *= 2
            if logger:
                logger.debug("Modifying {} records.".format(len(df)))
            to_sql(df, cnx, table_name, schema=schema_name, if_exists='append', index=True, index_label=id_name, nb_trials=nb_trials, logger=logger)

    return local_df


def readsync_table(cnx, csv_filepath, table_name, id_name, columns=['*'], schema_name=None, cond=None, bg_write_csv=False, max_records_per_query=10240, nb_trials=3, logger=None):
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
    table_sql_str = table_sql(table_name, schema_name=schema_name)
    with logger.scoped_debug("Reading table: local '{}' <- remote '{}'".format(csv_filepath, table_sql_str), curly=False) if logger else dummy_scope:
        local_df, remote_md5_df, same_keys, diff_keys, local_only_keys, remote_only_keys = comparesync_table(cnx, csv_filepath, table_name, id_name, columns=columns, schema_name=schema_name, cond=cond, nb_trials=nb_trials, logger=None)

        if len(diff_keys) == 0 and len(local_only_keys) == 0 and len(remote_only_keys) == 0: # nothing changed, really!
            if logger:
                logger.debug("Both tables are the same and of length {}.".format(len(same_keys)))
            return local_df, None if bg_write_csv else local_df

        if logger:
            logger.debug("Keys: {} to retain, {} to delete, {} to update, {} to read as new.".format(len(same_keys), len(local_only_keys), len(diff_keys), len(remote_only_keys)))

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
                    logger.debug("Fetching {} records with remaining {} records...".format(len(id_list2), len(id_list)))
                query_str = "("+",".join((str(id) for id in id_list2))+")"
                query_str = "select {} from {} where {} in {}".format(column_list, table_sql_str, id_name, query_str)
                if cond is not None:
                    query_str += " and " + cond
                #if logger:
                    #logger.debug("  using query '{}',".format(query_str))

                start_time = _pd.Timestamp.utcnow()
                new_dfs.append(read_sql(query_str, cnx, index_col=id_name, nb_trials=nb_trials, logger=logger))
                elapsed_time = (_pd.Timestamp.utcnow() - start_time).total_seconds() # elapsed time is in seconds

                if max_records_per_query is None:
                    if elapsed_time > 300: # too slow
                        record_cap = max(1, record_cap//2)
                    else: # too fast
                        record_cap *= 2

            new_df = _pd.concat(new_dfs)
            if not 'hash' in new_df.columns:
                new_df = new_df.join(new_md5_df)

            if len(new_md5_df) != len(new_df):
                if logger:
                    logger.debug("New dataframe:\n{}".format(str(new_df)))
                    logger.debug("Hash dataframe:\n{}".format(str(new_md5_df)))
                raise RuntimeError("Something must have gone wrong. Number of hashes {} != number of records {}.".format(len(new_md5_df), len(new_df)))
        else:
            new_df = None # nothing new

        # final df
        if len(same_keys) == 0:
            df = local_df[0:0] if new_df is None else new_df # former: empty dataframe
        else:
            local2_df = local_df[local_df.index.isin(same_keys)]
            df = local2_df if new_df is None else _pd.concat([local2_df, new_df], sort=True)
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


def readsync_table2(cnx, csv_filepath, table_name, id_name, columns=['*'], schema_name=None, cond=None, bg_write_csv=False, max_records_per_query=10240, nb_trials=3, logger=None):
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
        nb_trials: int
            number of read_sql() trials
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
    new_md5_df = read_sql(query_str, cnx, index_col=id_name, nb_trials=nb_trials, logger=logger)
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
        new_df = read_sql(query_str, cnx, index_col=id_name, nb_trials=nb_trials, logger=logger)
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
            new_dfs.append(read_sql(query_str, cnx, index_col=id_name, nb_trials=nb_trials, logger=logger))
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

