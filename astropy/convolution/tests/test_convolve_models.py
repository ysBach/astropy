# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import math
import numpy as np
from ..convolve import convolve, convolve_models
from ...modeling import models, fitting
from ...tests.helper import pytest
from ...utils.misc import NumpyRNGContext
from numpy.testing import assert_allclose, assert_almost_equal

try:
    import scipy
except ImportError:
    HAS_SCIPY = False
else:
    HAS_SCIPY = True

class TestConvolve1DModels(object):
    @pytest.mark.skipif('not HAS_SCIPY')
    def test_against_scipy(self):
        from scipy.signal import fftconvolve

        kernel = models.Gaussian1D(1, 0, 1)
        model = models.Gaussian1D(1, 0, 1)
        model_conv = convolve_models(model, kernel, mode='convolve_fft')
        x = np.arange(-5, 6)
        ans = fftconvolve(kernel(x), model(x), mode='same')

        assert_allclose(ans, model_conv(x) * kernel(x).sum(), atol=1e-5)

    @pytest.mark.skipif('not HAS_SCIPY')
    def test_against_scipy_with_additional_keywords(self):
        from scipy.signal import fftconvolve

        kernel = models.Gaussian1D(1, 0, 1)
        model = models.Gaussian1D(1, 0, 1)
        model_conv = convolve_models(model, kernel, mode='convolve_fft',
                                     normalize_kernel=False)
        x = np.arange(-5, 6)
        ans = fftconvolve(kernel(x), model(x), mode='same')

        assert_allclose(ans, model_conv(x), atol=1e-5)

    def test_sum_of_gaussians(self):
        """
        Test that convolving N(a, b) with N(c, d) gives N(a + b, c + d),
        where N(., .) stands for Gaussian probability density function.
        """

        kernel = models.Gaussian1D(1, 1, 1)
        model = models.Gaussian1D(1, 3, 1)
        model_conv = convolve_models(model, kernel, mode='convolve_fft',
                                     normalize_kernel=False)
        ans = models.Gaussian1D(1, 4, np.sqrt(2))
        x = np.arange(-5, 6)

        assert_allclose(ans(x) / (2 * math.sqrt(math.pi)),
                        model_conv(x) / (2 * np.pi), atol=1e-3)

    @pytest.mark.skipif('not HAS_SCIPY')
    def test_fitting_convolve_models(self):
        """
        test that a convolve model can be fitted
        """
        b1 = models.Box1D()
        g1 = models.Gaussian1D()

        x = np.linspace(-5, 5, 100)
        fake_model = models.Gaussian1D(amplitude=10)
        with NumpyRNGContext(123):
            fake_data = fake_model(x) + np.random.normal(size=len(x))

        init_model = convolve_models(b1, g1, normalize_kernel=False)
        fitter = fitting.LevMarLSQFitter()
        fitted_model = fitter(init_model, x, fake_data)

        me = np.mean(fitted_model(x) - fake_data)
        assert_almost_equal(me, 0.0, decimal=2)
