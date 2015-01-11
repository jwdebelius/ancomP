
import pyviennacl as pv
import pyopencl as cl
import numpy as np
import scipy.sparse as sp
import pandas as pd
from time import time
import copy

import unittest
import numpy.testing as np_test

from ancom.stats.permutation import (_init_device,
                                     _init_reciprocal_perms,
                                     _init_categorical_perms,
                                     _np_two_sample_mean_statistic,
                                     _cl_two_sample_mean_statistic,
                                     _naive_mean_permutation_test,
                                     _np_mean_permutation_test,
                                     _cl_mean_permutation_test,
                                     _naive_t_permutation_test,
                                     _np_t_permutation_test,
                                     _np_two_sample_t_statistic
                                     )

class TestPermutation(unittest.TestCase):

    def test_init_perms(self):
        cats = np.array([0, 1, 2, 0, 0, 2, 1])
        perms = _init_categorical_perms(cats, permutations=0)
        np_test.assert_array_equal(perms,
                          np.array([[1, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1],
                                    [1, 0, 0],
                                    [1, 0, 0],
                                    [0, 0, 1],
                                    [0, 1, 0]]))
        
    def test_basic_mean1(self):
        ## Basic quick test
        D = 5
        M = 6
        mat = np.array([range(10)]*M,dtype=np.float32)
        cats = np.array([0]*D+[1]*D,dtype=np.float32)

        nv_stats, nv_p = _naive_mean_permutation_test(mat,cats,1000)
        np_stats, np_p = _np_mean_permutation_test(mat,cats,1000)
        cl_stats, cl_p = _cl_mean_permutation_test(mat,cats,1000)

        nv_stats = np.matrix(nv_stats).transpose()
        nv_p = np.matrix(nv_p).transpose()
        self.assertEquals(sum(abs(nv_stats-np_stats) > 0.1), 0)
        self.assertEquals(sum(abs(nv_stats-cl_stats) > 0.1), 0)
        #Check test statistics
        self.assertAlmostEquals(sum(nv_stats-5),0,4)
        self.assertAlmostEquals(sum(np_stats-5),0,4)
        self.assertAlmostEquals(sum(cl_stats-5),0,4)
        #Check for small pvalues
        self.assertEquals(sum(nv_p>0.05),0)
        self.assertEquals(sum(np_p>0.05),0)
        self.assertEquals(sum(cl_p>0.05),0)

        np_test.assert_array_almost_equal(nv_stats, np_stats)
        np_test.assert_array_almost_equal(np_stats, cl_stats)


    def test_basic_mean2(self):
        ## Basic quick test
        D = 5
        M = 6
        mat = np.array([[0]*D+[10]*D]*M,dtype=np.float32)
        cats = np.array([0]*D+[1]*D,dtype=np.float32)

        nv_stats, nv_p = _naive_mean_permutation_test(mat,cats,1000)
        np_stats, np_p = _np_mean_permutation_test(mat,cats,1000)
        cl_stats, cl_p = _cl_mean_permutation_test(mat,cats,1000)

        nv_stats = np.matrix(nv_stats).transpose()
        nv_p = np.matrix(nv_p).transpose()
        self.assertEquals(sum(abs(nv_stats-np_stats) > 0.1), 0)
        self.assertEquals(sum(abs(nv_stats-cl_stats) > 0.1), 0)
        #Check test statistics
        self.assertAlmostEquals(sum(nv_stats-10),0,0.01)
        self.assertAlmostEquals(sum(np_stats-10),0,0.01)
        self.assertAlmostEquals(sum(cl_stats-10),0,0.01)
        #Check for small pvalues
        self.assertEquals(sum(nv_p>0.05),0)
        self.assertEquals(sum(np_p>0.05),0)
        self.assertEquals(sum(cl_p>0.05),0)

        np_test.assert_array_almost_equal(nv_stats, np_stats)
        np_test.assert_array_almost_equal(np_stats, cl_stats)

    def test_large(self):
        ## Large test
        N = 10
        mat = np.array(
            np.matrix(np.vstack((
                np.array([0]*(N/2)+[1]*(N/2)),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.random.random(N))),dtype=np.float32))
        cats = np.array([0]*(N/2)+[1]*(N/2),dtype=np.float32)
        np_stats, np_p = _np_mean_permutation_test(mat,cats,1000)
        cl_stats, cl_p = _cl_mean_permutation_test(mat,cats,1000)
        self.assertEquals(sum(abs(np_stats-cl_stats) > 0.1), 0)

        np_test.assert_array_almost_equal(np_stats, cl_stats)

    def test_random(self):
        ## Randomized test
        N = 50
        mat = np.array(
            np.matrix(np.vstack((
                np.array([0]*(N/2)+[100]*(N/2)),
                np.random.random(N),
                np.random.random(N),
                np.random.random(N),
                np.random.random(N),
                np.random.random(N),
                np.random.random(N))),dtype=np.float32))
        cats = np.array([0]*(N/2)+[1]*(N/2),dtype=np.float32)
        nv_stats, nv_p = _naive_mean_permutation_test(mat,cats,1000)
        np_stats, np_p = _np_mean_permutation_test(mat,cats,1000)
        cl_stats, cl_p = _cl_mean_permutation_test(mat,cats,1000)
        nv_stats = np.matrix(nv_stats).transpose()
        
        self.assertAlmostEquals(nv_stats[0],100.,4)
        self.assertAlmostEquals(np_stats[0],100.,4)
        self.assertAlmostEquals(cl_stats[0],100.,4)
        self.assertLess(nv_p[0],0.05)
        self.assertLess(np_p[0],0.05)
        self.assertLess(cl_p[0],0.05)

        #Check test statistics
        self.assertEquals(sum(nv_stats[1:]>nv_stats[0]), 0)
        self.assertEquals(sum(np_stats[1:]>np_stats[0]), 0)
        self.assertEquals(sum(cl_stats[1:]>cl_stats[0]), 0)
        
        self.assertEquals(sum(abs(np_stats-cl_stats) > 0.1), 0)
        self.assertEquals(sum(abs(nv_stats-cl_stats) > 0.1), 0)

        np_test.assert_array_almost_equal(np_stats, nv_stats)
        np_test.assert_array_almost_equal(np_stats, cl_stats)
        
    def test_mean_stat(self):
        N = 20
        mat = np.array(
            np.matrix(np.vstack((
                np.array([0]*(N/4)+[1]*(3*N/4)),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.random.random(N))),dtype=np.float32))
        cats = np.array([0]*(N/4)+[1]*(3*N/4), dtype=np.float32)
        d_mat, d_perms = _init_device(mat,cats)
        mean_stats, pvalues = _cl_two_sample_mean_statistic(d_mat, d_perms)
        self.assertEquals(mean_stats.argmax(), 0)
        self.assertEquals(mean_stats.max(), 1)
        self.assertLess(pvalues.min(), 0.05)
        perms = _init_reciprocal_perms(cats)
        mat, perms = np.matrix(mat), np.matrix(perms)
        mean_stats, pvalues = _np_two_sample_mean_statistic(mat, perms)
        self.assertEquals(mean_stats.argmax(), 0)
        self.assertEquals(mean_stats.max(), 1)
        self.assertLess(pvalues.min(), 0.05)
        
    def test_t_test_basic1(self):
        np.set_printoptions(precision=3)
        N = 20
        mat = np.array(
            np.matrix(np.vstack((
                np.hstack((np.arange((3*N)/4), np.arange(N/4)+100)),
                np.random.random(N))),dtype=np.float32))
        cats = np.array([0]*((3*N)/4)+[1]*(N/4), dtype=np.float32)      
        nv_t_stats, pvalues = _naive_t_permutation_test(mat, cats)
        perms = _init_categorical_perms(cats)
        mat, perms = np.matrix(mat), np.matrix(perms)
        np_t_stats, pvalues = _np_two_sample_t_statistic(mat, perms)


    def test_init_device(self):
        N = 10
        mat = np.array(
            np.matrix(np.vstack((
                np.array([0]*(N/2)+[1]*(N/2)),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.array([0]*N),
                np.random.random(N))),dtype=np.float32))
        cats = np.array([0]*(N/2)+[1]*(N/2), dtype=np.float32)
        d_mat, d_perms = _init_device(mat,cats)
        self.assertEquals(type(d_mat), pv.pycore.Matrix)
        self.assertEquals(type(d_perms), pv.pycore.Matrix)

        self.assertEquals(d_mat.shape, (7, 10) )
        self.assertEquals(d_perms.shape, (10, 2002) )
        
        
    def test_times(self):
        ## Compare timings between numpy and pyviennacl
        N = 60
        M = 60
        mat = np.array([range(M)]*N,dtype=np.float32)
        cats = np.array([0]*(M/2)+[1]*(M/2),dtype=np.float32)
        perms = _init_reciprocal_perms(cats,1000)
        t1 = time()
        counts = 3
        for _ in range(counts):
            nv_stats, nv_p = _naive_mean_permutation_test(mat,cats,1000)
        nv_time = (time()-t1)/counts
        t1 = time()
        for _ in range(counts):
            np_stats, np_p = _np_mean_permutation_test(mat,cats,1000)
        np_time = (time()-t1)/counts
        t1 = time()
        smat = sp.csr_matrix(mat)
        for _ in range(counts):
            sp_stats, sp_p = _np_mean_permutation_test(mat,cats,1000)
        sp_time = (time()-t1)/counts
        t1 = time()
        for _ in range(counts):
            cl_stats, cl_p = _cl_mean_permutation_test(mat,cats,1000)
        cl_time = (time()-t1)/counts

        print "Naive time [s]:", nv_time
        print "Numpy time [s]:", np_time
        print "Scipy time [s]:", sp_time
        print "GPU compute [s]:", cl_time

        _mat = np.matrix(mat)
        _perms = np.matrix(_init_reciprocal_perms(cats))
        t1 = time()
        for _ in range(counts):
            np_stats, np_p = _np_two_sample_mean_statistic(_mat,_perms)
        np_time = (time()-t1)/counts
        _mat = pv.Matrix(mat)
        _perms = pv.Matrix(_init_reciprocal_perms(cats))
        t1 = time()
        for _ in range(counts):
            cl_stats, cl_p = _cl_two_sample_mean_statistic(_mat,_perms)
        cl_time = (time()-t1)/counts
        print "Numpy time (w/o transfer)[s]:", np_time
        print "GPU compute (w/o transfer)[s]:", cl_time
        
unittest.main()