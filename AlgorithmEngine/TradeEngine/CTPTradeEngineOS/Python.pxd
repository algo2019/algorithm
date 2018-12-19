# -*- coding: utf-8 -*-

cdef extern from "Python.h":
    ctypedef enum PyGILState_STATE:
        pass
    PyGILState_STATE PyGILState_Ensure()
    void PyGILState_Release(PyGILState_STATE)
    void PyEval_InitThreads()
