import unittest

import numpy as np
import pandas as pd

import pylandstats as pls


class TestPyLandStats(unittest.TestCase):
    def setUp(self):
        ls_arr = np.load('tests/input_data/ls.npy')
        self.ls = pls.Landscape(ls_arr, res=(250, 250))

    def test_io(self):
        ls = pls.read_geotiff('tests/input_data/ls.tif')
        self.assertEqual(ls.cell_width, 250)
        self.assertEqual(ls.cell_height, 250)
        self.assertEqual(ls.cell_area, 250 * 250)

    def test_metrics_parameters(self):
        ls = self.ls

        for patch_metric in pls.Landscape.PATCH_METRICS:
            method = getattr(ls, patch_metric)
            self.assertIsInstance(method(), pd.DataFrame)
            self.assertIsInstance(method(class_val=ls.classes[0]), pd.Series)

        for class_metric in pls.Landscape.CLASS_METRICS:
            self.assertTrue(
                np.isreal(getattr(ls, class_metric)(class_val=ls.classes[0])))

        for landscape_metric in pls.Landscape.LANDSCAPE_METRICS:
            self.assertTrue(np.isreal(getattr(ls, landscape_metric)()))

    def test_metric_dataframes(self):
        ls = self.ls
        patch_df = ls.patch_metrics_df()
        self.assertTrue(
            np.all(
                patch_df.columns.drop('class_val') ==
                pls.Landscape.PATCH_METRICS))
        self.assertEqual(patch_df.index.name, 'patch_id')
        self.assertRaises(ValueError, ls.patch_metrics_df, ['foo'])

        class_df = ls.class_metrics_df()
        self.assertEqual(
            len(class_df.columns.difference(pls.Landscape.CLASS_METRICS)), 0)
        self.assertEqual(class_df.index.name, 'class_val')
        self.assertRaises(ValueError, ls.class_metrics_df, ['foo'])

        landscape_df = ls.landscape_metrics_df()
        self.assertEqual(
            len(
                landscape_df.columns.difference(
                    pls.Landscape.LANDSCAPE_METRICS)), 0)
        self.assertEqual(len(landscape_df.index), 1)
        self.assertRaises(ValueError, ls.landscape_metrics_df, ['foo'])

    def test_landscape_metrics_value_ranges(self):
        ls = self.ls

        # basic tests of the `Landscape` class' attributes
        self.assertNotIn(ls.nodata, ls.classes)
        self.assertGreater(ls.landscape_area, 0)

        class_val = ls.classes[0]
        # label_arr = ls._get_label_arr(class_val)

        # patch-level metrics
        assert (ls.area()['area'] > 0).all()
        assert (ls.perimeter()['perimeter'] > 0).all()
        assert (ls.perimeter_area_ratio()['perimeter_area_ratio'] > 0).all()
        assert (ls.shape_index()['shape_index'] >= 1).all()
        _fractal_dimension_ser = ls.fractal_dimension()['fractal_dimension']
        assert (_fractal_dimension_ser >= 1).all() and (_fractal_dimension_ser
                                                        <= 2).all()
        # TODO: assert 0 <= ls.contiguity_index(patch_arr) <= 1
        # TODO: assert 0 <= ls.euclidean_nearest_neighbor(patch_arr) <= 1
        # TODO: assert 0 <= ls.proximity(patch_arr) <= 1

        # class-level metrics
        assert ls.total_area(class_val) > 0
        assert 0 < ls.proportion_of_landscape(class_val) < 100
        assert ls.patch_density(class_val) > 0
        assert 0 < ls.largest_patch_index(class_val) < 100
        assert ls.total_edge(class_val) >= 0
        assert ls.edge_density(class_val) >= 0

        # the value ranges of mean, area-weighted mean and median aggregations
        # are going to be the same as their respective original metrics
        mean_suffixes = ['_mn', '_am', '_md']
        # the value ranges of the range, standard deviation and coefficient of
        # variation  will always be nonnegative as long as the means are
        # nonnegative as well (which is the case of all of the metrics
        # implemented so far)
        var_suffixes = ['_ra', '_sd', '_cv']

        for mean_suffix in mean_suffixes:
            assert getattr(ls, 'area' + mean_suffix)(class_val) > 0
            assert getattr(ls,
                           'perimeter_area_ratio' + mean_suffix)(class_val) > 0
            assert getattr(ls, 'shape_index' + mean_suffix)(class_val) >= 1
            assert 1 <= getattr(
                ls, 'fractal_dimension' + mean_suffix)(class_val) <= 2
            # assert 0 <= getattr(
            #     ls, 'contiguity_index' + mean_suffix)(class_val) <= 1
            # assert getattr(ls, 'proximity' + mean_suffix)(class_val) >= 0
            # assert getattr(
            #     ls, 'euclidean_nearest_neighbor' + mean_suffix)(class_val) >

        for var_suffix in var_suffixes:
            assert getattr(ls, 'area' + mean_suffix)(class_val) >= 0
            assert getattr(ls,
                           'perimeter_area_ratio' + var_suffix)(class_val) >= 0
            assert getattr(ls, 'shape_index' + var_suffix)(class_val) >= 0
            assert getattr(ls,
                           'fractal_dimension' + var_suffix)(class_val) >= 0
            # assert getattr(
            #    ls, 'contiguity_index' + var_suffix)(class_val) >= 0
            # assert getattr(ls, 'proximity' + var_suffix)(class_val) >= 0
            # assert getattr(
            #     ls, 'euclidean_nearest_neighbor' + var_suffix)(
            #         class_val) >= 0

        # TODO: assert 0 < ls.interspersion_juxtaposition_index(
        #           class_val) <= 100
        assert ls.landscape_shape_index(class_val) >= 1

        # landscape-level metrics
        assert ls.total_area() > 0
        assert ls.patch_density() > 0
        assert 0 < ls.largest_patch_index() < 100
        assert ls.total_edge() >= 0
        assert ls.edge_density() >= 0
        assert 0 < ls.largest_patch_index() <= 100
        assert ls.total_edge() >= 0
        assert ls.edge_density() >= 0

        # for class_val in ls.classes:
        #     print('num_patches', class_val, ls._get_num_patches(class_val))
        #     print('patch_areas', len(ls._get_patch_areas(class_val)))

        # raise ValueError

        for mean_suffix in mean_suffixes:
            assert getattr(ls, 'area' + mean_suffix)() > 0
            assert getattr(ls, 'perimeter_area_ratio' + mean_suffix)() > 0
            assert getattr(ls, 'shape_index' + mean_suffix)() >= 1
            assert 1 <= getattr(ls, 'fractal_dimension' + mean_suffix)() <= 2
            # assert 0 <= getattr(ls, 'contiguity_index' + mean_suffix)() <= 1
            # assert getattr(ls, 'proximity' + mean_suffix)() >= 0
            # assert getattr(ls,
            #                'euclidean_nearest_neighbor' + mean_suffix)() > 0
        for var_suffix in var_suffixes:
            assert getattr(ls, 'area' + var_suffix)() > 0
            assert getattr(ls, 'perimeter_area_ratio' + var_suffix)() >= 0
            assert getattr(ls, 'shape_index' + var_suffix)() >= 0
            assert getattr(ls, 'fractal_dimension' + var_suffix)() >= 0
            # assert getattr(ls, 'contiguity_index' + var_suffix)() >= 0
            # assert getattr(ls, 'proximity' + var_suffix)() >= 0
            # assert getattr(ls,
            #                'euclidean_nearest_neighbor' + var_suffix)() >= 0

        # TODO: assert 0 < ls.contagion() <= 100
        # TODO: assert 0 < ls.interspersion_juxtaposition_index() <= 100
        # TODO: assert ls.shannon_diversity_index() >= 0

    def test_spatiotemporalanalysis(self):
        res = (250, 250)

        landscapes = [
            pls.Landscape(np.load(fp), res=res) for fp in
            ['tests/input_data/ls.npy', 'tests/input_data/ls_future.npy']
        ]

        sta = pls.SpatioTemporalAnalysis(landscapes, dates=[2012, 2018])

        # TODO: test legend and figsize

        ax = sta.plot_metric('patch_density', class_val=None)
        assert len(ax.lines) == 1
        ax = sta.plot_metric('patch_density', class_val=54, ax=ax)
        assert len(ax.lines) == 2

        fig, axes = sta.plot_metrics(['edge_density', 'patch_density'],
                                     class_val=54)
        assert len(axes) == 2
