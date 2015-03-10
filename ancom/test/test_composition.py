
import numpy as np
import scipy.stats as ss
from ancom.linalg.composition import (perturb, perturb_inv, power, clr, ilr, ilr_inv,
                                      centralize, variation_matrix, total_variation,
                                      multiplicative_replacement, _closure)

import unittest
import numpy.testing as npt

class CompositionTests(unittest.TestCase):

    def setUp(self):
        self.data1 = np.array([[2, 2, 6],
                               [4, 4, 2]])
        self.data2 = np.array([2, 2, 6])

        self.data3 = np.array([[1, 2, 3, 0, 5],
                               [1, 0, 0, 4, 5],
                               [1, 2, 3, 4, 5]])
        self.data4 = np.array([1, 2, 3, 0, 5])
        self.data5 = np.array([[[1, 2, 3, 0, 5]]])
        self.data6 = [[2, 2, 6], [4, 4, 2]]
        self.data7 = [[1, 2, 3, 0, 5],
                      [1, 0, 0, 4, 5],
                      [1, 2, 3, 4, 5]]

    def test_closure(self):
        npt.assert_allclose(_closure(self.data1),
                            np.array([[.2, .2, .6],
                                      [.4, .4, .2]]))
        npt.assert_allclose(_closure(self.data2),
                            np.array([.2, .2, .6]))
        npt.assert_allclose(_closure(self.data6),
                            np.array([[.2, .2, .6],
                                      [.4, .4, .2]]))
        with self.assertRaises(ValueError):
            _closure(self.data5)

    def test_perturb(self):
        pmat = perturb(_closure(self.data1), np.array([1, 1, 1]))
        npt.assert_allclose(pmat,
                            np.array([[.2, .2, .6],
                                      [.4, .4, .2]]))

        pmat = perturb(_closure(self.data1), np.array([10, 10, 20]))
        npt.assert_allclose(pmat,
                            np.array([[.125, .125, .75],
                                      [1./3, 1./3, 1./3]]))

        pmat = perturb(_closure(self.data1), np.array([10, 10, 20]))
        npt.assert_allclose(pmat,
                            np.array([[.125, .125, .75],
                                      [1./3, 1./3, 1./3]]))

        pmat = perturb(_closure(self.data2), np.array([1, 2, 1]))
        npt.assert_allclose(pmat, np.array([1./6, 2./6, 3./6]))

        pmat = perturb(_closure(self.data6), np.array([1, 1, 1]))
        npt.assert_allclose(pmat,
                            np.array([[.2, .2, .6],
                                      [.4, .4, .2]]))

    def test_power(self):
        pmat = power(_closure(self.data1), 2)
        npt.assert_allclose(pmat,
                            np.array([[.04/.44, .04/.44, .36/.44],
                                      [.16/.36, .16/.36, .04/.36]]))

        pmat = power(_closure(self.data2), 2)
        npt.assert_allclose(pmat, np.array([.04, .04, .36])/.44)

        pmat = power(_closure(self.data6), 2)
        npt.assert_allclose(pmat,
                            np.array([[.04/.44, .04/.44, .36/.44],
                                      [.16/.36, .16/.36, .04/.36]]))

    def test_perturb_inv(self):
        pmat = perturb_inv(_closure(self.data1), np.array([.1, .1, .1]))
        imat = perturb(_closure(self.data1), np.array([10, 10, 10]))
        npt.assert_allclose(pmat, imat)
        pmat = perturb_inv(_closure(self.data1), np.array([1, 1, 1]))
        npt.assert_allclose(pmat,
                            np.array([[.2, .2, .6],
                                      [.4, .4, .2]]))
        pmat = perturb_inv(_closure(self.data6), np.array([.1, .1, .1]))
        imat = perturb(_closure(self.data1), np.array([10, 10, 10]))
        npt.assert_allclose(pmat, imat)

    def test_multiplicative_replacement(self):
        np.set_printoptions(precision=10)
        amat = multiplicative_replacement(self.data3)
        npt.assert_allclose(amat,
                            np.array([[0.09056604, 0.18113208,
                                       0.27169811, 0.00377358,
                                       0.45283019],
                                      [0.09913793, 0.00431034,
                                       0.00431034, 0.39655172,
                                       0.49568966],
                                      [0.06666667, 0.13333333,
                                       0.2, 0.26666667,
                                       0.33333333]]), rtol=1e-5, atol=1e-5)

        amat = multiplicative_replacement(self.data4)
        npt.assert_allclose(amat, np.array([0.09056604, 0.18113208,
                                            0.27169811, 0.00377358,
                                            0.45283019]),
                            rtol=1e-5, atol=1e-5)

        amat = multiplicative_replacement(self.data7)
        npt.assert_allclose(amat,
                            np.array([[0.09056604, 0.18113208,
                                       0.27169811, 0.00377358,
                                       0.45283019],
                                      [0.09913793, 0.00431034,
                                       0.00431034, 0.39655172,
                                       0.49568966],
                                      [0.06666667, 0.13333333,
                                       0.2, 0.26666667,
                                       0.33333333]]), rtol=1e-5, atol=1e-5)

        with self.assertRaises(ValueError):
            multiplicative_replacement(self.data5)

    def test_clr(self):
        cmat = clr(_closure(self.data1))
        A = np.array([.2, .2, .6])
        B = np.array([.4, .4, .2])

        npt.assert_allclose(cmat,
                            [np.log(A / np.exp(np.log(A).mean())),
                             np.log(B / np.exp(np.log(B).mean()))])
        cmat = clr(_closure(self.data2))
        A = np.array([.2, .2, .6])
        npt.assert_allclose(cmat,
                            np.log(A / np.exp(np.log(A).mean())))

        cmat = clr(_closure(self.data6))
        A = np.array([.2, .2, .6])
        B = np.array([.4, .4, .2])

        npt.assert_allclose(cmat,
                            [np.log(A / np.exp(np.log(A).mean())),
                             np.log(B / np.exp(np.log(B).mean()))])

        with self.assertRaises(ValueError):
            clr(self.data5)

    def test_centralize(self):
        cmat = centralize(_closure(self.data1))
        npt.assert_allclose(cmat,
                            np.array([[0.22474487, 0.22474487,
                                       0.55051026],
                                      [0.41523958, 0.41523958,
                                       0.16952085]]))
        cmat = centralize(_closure(self.data6))
        npt.assert_allclose(cmat,
                            np.array([[0.22474487, 0.22474487,
                                       0.55051026],
                                      [0.41523958, 0.41523958,
                                       0.16952085]]))

        with self.assertRaises(ValueError):
            centralize(self.data2)
        with self.assertRaises(ValueError):
            centralize(self.data5)

    def test_ilr(self):
        mat = _closure(np.array([[np.exp(1), 1, 1]]))
        npt.assert_array_almost_equal(ilr(mat),
                                          np.array([[ 0.70710678,  0.40824829]]))
    def test_ilr_inv(self):
        mat = _closure(np.array([[np.exp(1), 1, 1]]))
        npt.assert_array_almost_equal(ilr_inv(ilr(mat)),mat)

if __name__=="__main__":
    unittest.main()
