import abc

import numpy as np
import h5py

import miapy.data.indexexpression as expr


class Writer(metaclass=abc.ABCMeta):

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    @abc.abstractmethod
    def close(self):
        pass

    @abc.abstractmethod
    def open(self):
        pass

    @abc.abstractmethod
    def reserve(self, entry: str, shape: tuple, dtype=None):
        pass

    @abc.abstractmethod
    def fill(self, entry: str, data, index: expr.IndexExpression=None):
        pass

    @abc.abstractmethod
    def write(self, entry: str, data, dtype=None):
        pass


class Hdf5Writer(Writer):
    str_type = h5py.special_dtype(vlen=str)

    def __init__(self, file_name: str) -> None:
        self.h5 = None  # type: h5py.File
        self.file_name = file_name

    def close(self):
        if self.h5 is not None:
            self.h5.close()
            self.h5 = None

    def open(self):
        self.h5 = h5py.File(self.file_name)

    def reserve(self, entry: str, shape: tuple, dtype=None):
        # special string handling (in order not to use length limited strings)
        if dtype is str or dtype == 'str' or (isinstance(dtype, np.dtype) and dtype.type == np.str_):
            dtype = self.str_type
        self.h5.create_dataset(entry, shape, dtype=dtype)

    def fill(self, entry: str, data, index: expr.IndexExpression=None):
        # special string handling (in order not to use length limited strings)
        if self.h5[entry].dtype is self.str_type:
            data = np.asarray(data, dtype=object)

        if index is None:
            index = expr.IndexExpression()

        self.h5[entry][index.expression] = data

    def write(self, entry: str, data, dtype=None):
        # special string handling (in order not to use length limited strings)
        if dtype is str or dtype == 'str' or (isinstance(dtype, np.dtype) and dtype.type == np.str_):
            dtype = self.str_type
            data = np.asarray(data, dtype=object)
        if entry in self.h5:
            del self.h5[entry]
        self.h5.create_dataset(entry, dtype=dtype, data=data)
