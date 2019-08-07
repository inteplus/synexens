import dask.dataframe as _dd
import pandas as _pd
import numpy as _np
import csv as _csv
import basemt.path as _p
import json as _js
import time as _t


def metadata(df):
    '''Extracts the metadata of a dataframe.

    Parameters
    ----------
        df : pandas.DataFrame

    Returns
    -------
        meta : json-like
            metadata describing the dataframe
    '''
    meta = {}
    if list(df.index.names) != [None]: # has index
        index_names = list(df.index.names)
        df = df.reset_index(drop=False)
    else: # no index
        index_names = []

    meta = {}
    for x in df.dtypes.index:
        dtype = df.dtypes.loc[x]
        name = dtype.name
        if name != 'category':
            meta[x] = name
        else:
            meta[x] = ['category', df[x].cat.categories.tolist(), df[x].cat.ordered]
    meta = {'columns': meta, 'index_names': index_names}
    return meta


def metadata2dtypes(meta):
    '''Creates a dictionary of dtypes from the metadata returned by metadata() function.'''
    res = {}
    s = meta['columns']
    for x in s:
        y = s[x]
        if y == 'datetime64[ns]':
            y = 'object'
        elif isinstance(y, list) and y[0] == 'category':
            y = 'object'
        res[x] = np.dtype(y)
    return res
    # return {x:np.dtype(y) for (x,y) in s.items()}


def read_csv(path, **kwargs):
    # make sure we do not concurrently access the file
    with _p.lock(path, to_write=False):
        # If '.meta' file exists, assume our format and therefore use dask to read. Otherwise, assume general csv file and use pandas to read.
        path2 = path[:-4]+'.meta'
        if not _p.exists(path2): # no meta
            if _p.getsize(path) >= (1 << 25): # >= 32MB?
                try: # try to load in parallel using dask
                    return _dd.read_csv(path, quoting=_csv.QUOTE_NONNUMERIC, **kwargs)
                except:
                    pass
            return _pd.read_csv(path, quoting=_csv.QUOTE_NONNUMERIC, **kwargs)

        # extract 'index_col' and 'dtype' from kwargs
        index_col = kwargs.pop('index_col', None)
        dtype = kwargs.pop('dtype', None)

        # load the metadata
        meta = _js.load(open(path2, 'rt')) if _p.exists(path2) else None

        # From now on, meta takes priority over dtype. We will ignore dtype.
        kwargs['dtype'] = 'object'

        # update index_col if it does not exist and meta has it
        if index_col is None and len(meta['index_names']) > 0:
            index_col = meta['index_names']

        # Try dask. If it fails, try pandas.
        try:
            df = _dd.read_csv(path, quoting=_csv.QUOTE_NONNUMERIC, **kwargs).compute()
        except:
            df = _pd.read_csv(path, quoting=_csv.QUOTE_NONNUMERIC, **kwargs)

        # adjust the returning dataframe based on the given meta
        s = meta['columns']
        for x in s:
            y = s[x]
            if y == 'datetime64[ns]':
                df[x] = _pd.to_datetime(df[x])
            elif isinstance(y, list) and y[0] == 'category':
                df[x] = df[x].astype('category', categories=y[1], ordered=y[2])
            elif y == 'int64':
                df[x] = df[x].astype(_np.int64)
            elif y == 'uint8':
                df[x] = df[x].astype(_np.uint8)
            elif y == 'float64':
                df[x] = df[x].astype(_np.float64)
            elif y == 'bool':
                # dd is very strict at reading a csv. It may read True as 'True' and False as 'False'.
                df[x] = df[x].replace('True', True).replace('False', False).astype(_np.bool)
            elif y == 'object':
                pass
            else:
                raise OSError("Unknown dtype for conversion {}".format(y))

        # set the index_col if it exists
        if index_col is not None and len(index_col) > 0:
            df = df.set_index(index_col, drop=True)

        return df
read_csv.__doc__ = _dd.read_csv.__doc__

def to_csv(df, path, **kwargs):
    '''Write DataFrame to a comma-separated values (csv) file. Other than the first argument being the dataframe to be written to, the remaining arguments are passed directly to `DataFrame.to_csv()` function.\n''' + _pd.DataFrame.to_csv.__doc__
    # make sure we do not concurrenly access the file
    with _p.lock(path, to_write=True):
        # write the csv file
        path2 = path+'.tmp.csv'
        dirpath = _p.dirname(path)
        if dirpath:
            _p.make_dirs(dirpath)
        if not _p.exists(dirpath):
            _t.sleep(1)
        res = df.to_csv(path2, quoting=_csv.QUOTE_NONNUMERIC, **kwargs)
        _p.remove(path)
        if _p.exists(path) or not _p.exists(path2):
            _t.sleep(1)
        _p.rename(path2, path)

        # write the meta file
        path2 = path[:-4]+'.meta'
        _js.dump(metadata(df), open(path2, 'wt'))

        return res
