import sqlalchemy as _sa
import sqlalchemy.exc as _se

def frame_sql(frame_name, schema=None):
    return frame_name if schema is None else '{}.{}'.format(schema, frame_name)


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
        except _se.ProgrammingError as e:
            raise
        except (_se.DatabaseError, _se.OperationalError) as e:
            if logger:
                with logger.scoped_warn("Ignored an exception raised by failed attempt {}/{} to execute `{}.{}()`".format(x+1, nb_trials, func.__module__, func.__name__)):
                    logger.warn_last_exception()
    raise RuntimeError("Attempted {} times to execute `{}.{}()` but failed.".format(nb_trials, func.__module__, func.__name__))


def list_schemas(conn, nb_trials=3, logger=None):
    '''Lists all schemas.

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
        out : list
            list of all schema names
    '''
    return run_func(_sa.inspect, conn, nb_trials=nb_trials, logger=logger).get_schemas()


def list_tables(conn, schema=None, nb_trials=3, logger=None):
    '''Lists all tables of a given schema.

    Parameters
    ----------
        conn : sqlalchemy.engine.base.Engine
            an sqlalchemy connection engine created by function `create_engine()`
        schema : str or None
            a valid schema name returned from `list_schemas()`. Default to sqlalchemy
        nb_trials: int
            number of query trials
        logger: logging.Logger or None
            logger for debugging

    Returns
    -------
        out : list
            list of all table names
    '''
    return run_func(conn.table_names, schema=schema, nb_trials=nb_trials, logger=logger)


