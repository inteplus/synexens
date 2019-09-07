'''Extra modules to augment pandas.'''


import pandas as _pd


def Series4json(obj):
    '''Converts a json-like object in to a pandas.Series.

    Parameters
    ==========
    obj : json_like
        a json-like object

    Returns
    =======
    pandas.Series
        output Series

    Notes
    =====
    A json-like object contains 2 array-likes, each has length K. The first array represents the index array. The second array represents the value array.
    '''
    return _pd.Series(index=obj[0], data=obj[1])


def json4Series(obj):
    '''Converts a pandas.Series into a json-like object.

    Parameters
    ==========
    obj : pandas.Series
        input Series

    Returns
    =======
    json_like
        a json-like object

    Notes
    =====
    A json-like object contains 2 array-likes, each has length K. The first array represents the index array. The second array represents the value array.
    '''
    return [obj.index.tolist(), obj.tolist()]
