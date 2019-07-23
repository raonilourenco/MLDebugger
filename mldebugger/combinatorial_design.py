###############################################################################
##
## Copyright (C) 2018-2020, New York University.
## All rights reserved.
## Contact: raoni@nyu.edu
##
## This file is part of MLDebugger.
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice,
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright
##    notice, this list of conditions and the following disclaimer in the
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the New York University nor the names of its
##    contributors may be used to endorse or promote products derived from
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

import itertools
import random

"""
"""

def create_rows(num_params, num_values, keys):
    """
    :param num_params:
    :param num_values:
    :param keys:
    :return:
    """
    rows = []
    for i in range(num_params * num_values):
        rows.append(dict.fromkeys(keys))
    return rows


def fit(v_0, v_1, pair, rows, keys):
    """
    :param v_0:
    :param v_1:
    :param pair:
    :param rows:
    :param keys:
    :return:
    """
    if any((data[pair[0]] == v_0 and data[pair[1]] == v_1) for data in rows):
        return
    for data in rows:
        if data[pair[0]] == v_0 and data[pair[1]] is None:
            data[pair[1]] = v_1
            return
        if data[pair[0]] is None and data[pair[1]] is v_1:
            data[pair[0]] = v_0
            return
        if data[pair[0]] is None and data[pair[1]] is None:
            data[pair[0]] = v_0
            data[pair[1]] = v_1
            return
    rows.append(dict.fromkeys(keys))
    rows[-1][pair[0]] = v_0
    rows[-1][pair[1]] = v_1


def all_disjoint_pairs(lst):
    """
    :param lst:
    :return:
    """
    if len(lst) < 2:
        yield lst
        return
    a_member = lst[0]
    for i in range(1, len(lst)):
        pair = (a_member, lst[i])
        for rest in all_disjoint_pairs(lst[1:i] + lst[i + 1:]):
            yield [pair] + rest


def get_disjoint_pairs_with_max(keys, max_0, max_1):
    """
    :param keys:
    :param max_0:
    :param max_1:
    :return:
    """
    for disjoint_pairs in all_disjoint_pairs(keys):
        if ((max_0, max_1) in disjoint_pairs) or ((max_1, max_0) in disjoint_pairs):
            return disjoint_pairs


def generate_tuples(parameters):
    """
    :param parameters:
    :return:
    """
    if len(parameters.keys()) % 2 != 0:
        parameters['dummy'] = []
    keys = parameters.keys()
    max_0 = keys[0]
    max_1 = keys[1]
    for key in keys[1:]:
        if len(parameters[key]) >= len(parameters[max_0]):
            max_1 = max_0
            max_0 = key
        elif len(parameters[key]) > len(parameters[max_1]):
            max_1 = key

    handled_pairs = get_disjoint_pairs_with_max(keys, max_0, max_1)
    rows = create_rows(len(parameters[max_0]), len(parameters[max_1]), keys)
    for pair in handled_pairs:
        row_index = 0
        for v_0 in parameters[pair[0]]:
            for v_1 in parameters[pair[1]]:
                rows[row_index][pair[0]] = v_0
                rows[row_index][pair[1]] = v_1
                row_index += 1

    pairs = list(itertools.combinations(keys, 2))
    for pair in pairs:
        if pair not in handled_pairs:
            for v_0 in parameters[pair[0]]:
                for v_1 in parameters[pair[1]]:
                    fit(v_0, v_1, pair, rows, keys)
            handled_pairs.append(pair)
    parameters.pop('dummy', None)
    for row in rows:
        row.pop('dummy', None)
        for key in parameters.keys():
            if row[key] is None:
                row[key] = random.choice(list(parameters[key]))
    return rows
