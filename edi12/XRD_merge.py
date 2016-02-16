# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:40:07 2015

@author: casim
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from edi12.XRD_tools import XRD_tools
from edi12.merge_tools import find_limits, mask_generator, masked_merge

class XRD_merge(XRD_tools):
    """
    Tool to merge mutliple XRD data sets - inherits tools for XRD_tools.
    """
    def __init__(self, data, name, order = 'slit', padding = 0.1):
        """
        Merge data, specifying mering method/order
        
        # data:       Tuple or list containing data objects analysed with the 
                      XRD_analysis tool.
        # name:       Experiment name/ID.
        # order:      Merging method/order. Specify 'simple' merge (keeps all 
                      data) or by 'slit' size (default)/ user defined order.
                      Slit/user defined order allows for the supression/removal
                      of overlapping data. User defined should be a list of
                      the same length as the data tuple.
        """
        self.data = np.array(data)
        self.q0 = self.data[0].q0
        self.peak_windows = self.data[0].peak_windows
        
        for i in self.data:
            error = 'Trying to merge incompatible data (e.g. 2D with 3D)'
            assert self.data[0].dims == i.dims, error
        self.dims = self.data[0].dims
        
        if order == 'slit':
            priority = [data.slit_size for data in self.data]
        elif order == 'simple':
            priority = [0 for data in self.data]
        else:
            priority = order

        priority_set, inds = np.unique(priority, return_inverse=True)    
        data_mask = [self.data[inds == 0],  [None] * len(self.data[inds == 0])]
        
        for idx, _ in enumerate(priority_set[1:]):
            mask_gen = self.data[inds < idx + 1]
            mask_data = self.data[inds == idx + 1]
            limits = []
            for dim in mask_gen[0].dims:
                limits.append(find_limits([i.co_ords[dim] for i in mask_gen]))

            data_mask[0] = np.append(data_mask[0], mask_data)
            data_mask[1] += [mask_generator(data, limits, padding) 
                             for data in mask_data]

        merged_data = masked_merge(data_mask[0], data_mask[1])
        self.strain, self.strain_err, self.strain_param, self.peaks, \
        self.peaks_err, self.ss2_x, self.ss2_y, self.ss2_z = merged_data
        self.co_ords = {b'ss2_x': self.ss2_x, b'ss2_y': self.ss2_y, 
                        b'ss2_z': self.ss2_z} 
        self.slit_size = None


    def __exit__(self, exc_type, exc_value, traceback):
        pass
 