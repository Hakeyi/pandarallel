import pytest

from pandarallel import pandarallel

import pandas as pd
import numpy as np
import math

def func_for_dataframe_apply_axis_0(x):
    return max(x) - min(x)

def func_for_dataframe_apply_axis_1(x):
    return math.sin(x.a**2) + math.sin(x.b**2)

def func_for_dataframe_applymap(x):
    return math.sin(x**2) - math.cos(x**2)

def func_for_series_map(x):
    return math.log10(math.sqrt(math.exp(x**2)))

def func_for_series_apply(x, power, bias=0):
    return math.log10(math.sqrt(math.exp(x**power))) + bias

def func_for_series_rolling_apply(x):
    return x.iloc[0] + x.iloc[1] ** 2 + x.iloc[2] ** 3 + x.iloc[3] ** 4

def func_for_dataframe_groupby_apply(df):
    dum = 0
    for item in df.b:
        dum += math.log10(math.sqrt(math.exp(item**2)))

    return dum / len(df.b)

def func_for_dataframe_groupby_rolling_apply(x):
    return x.iloc[0] + x.iloc[1] ** 2 + x.iloc[2] ** 3 + x.iloc[3] ** 4

@pytest.fixture(scope="session")
def plasma_client():
    pandarallel.initialize()

def test_dataframe_apply_axis_0(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.randint(1, 8, df_size),
                        b=np.random.rand(df_size)))

    res = df.apply(func_for_dataframe_apply_axis_0)
    res_parallel = df.parallel_apply(func_for_dataframe_apply_axis_0)
    assert res.equals(res_parallel)

def test_dataframe_apply_axis_1(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.randint(1, 8, df_size),
                        b=np.random.rand(df_size)))

    res = df.apply(func_for_dataframe_apply_axis_1, axis=1)
    res_parallel = df.parallel_apply(func_for_dataframe_apply_axis_1, axis=1)
    assert res.equals(res_parallel)

def test_dataframe_applymap(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.randint(1, 8, df_size),
                            b=np.random.rand(df_size)))

    res = df.applymap(func_for_dataframe_applymap)
    res_parallel = df.parallel_applymap(func_for_dataframe_applymap)
    assert res.equals(res_parallel)

def test_series_map(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.rand(df_size) + 1))

    res = df.a.map(func_for_series_map)
    res_parallel = df.a.parallel_map(func_for_series_map)
    assert res.equals(res_parallel)

def test_series_apply(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.rand(df_size) + 1))

    res = df.a.apply(func_for_series_apply, args=(2,), bias=3)
    res_parallel = df.a.parallel_apply(func_for_series_apply, args=(2,),
                                       bias=3)
    assert res.equals(res_parallel)

def test_series_rolling_apply(plasma_client):
    df_size = int(1e2)
    df = pd.DataFrame(dict(a=np.random.randint(1, 8, df_size),
                      b=list(range(df_size))))

    res = df.b.rolling(4).apply(func_for_series_rolling_apply, raw=False)
    res_parallel = df.b.rolling(4).parallel_apply(func_for_series_rolling_apply,
                                                  raw=False)

    assert res.equals(res_parallel)

def test_dataframe_groupby_apply(plasma_client):
    df_size = int(1e1)
    df = pd.DataFrame(dict(a=np.random.randint(1, 8, df_size),
                           b=np.random.rand(df_size),
                           c=np.random.rand(df_size)))

    res = df.groupby("a").apply(func_for_dataframe_groupby_apply)
    res_parallel = (df.groupby("a")
                      .parallel_apply(func_for_dataframe_groupby_apply))
    res.equals(res_parallel)

    res = df.groupby(["a"]).apply(func_for_dataframe_groupby_apply)
    res_parallel = (df.groupby(["a"])
                      .parallel_apply(func_for_dataframe_groupby_apply))
    res.equals(res_parallel)

    res = df.groupby(["a", "b"]).apply(func_for_dataframe_groupby_apply)
    res_parallel = (df.groupby(["a", "b"])
                      .parallel_apply(func_for_dataframe_groupby_apply))
    res.equals(res_parallel)

def test_dataframe_groupby_rolling_apply(plasma_client):
    df_size = int(1e2)
    df = pd.DataFrame(dict(a=np.random.randint(1, 3, df_size),
                            b=np.random.rand(df_size)))

    res = (df.groupby('a').b.rolling(4)
             .apply(func_for_dataframe_groupby_rolling_apply, raw=False))
    res_parallel = (df.groupby('a')
                     .b.rolling(4)
                     .parallel_apply(func_for_dataframe_groupby_rolling_apply,
                                     raw=False)
                   )
    res.equals(res_parallel)
