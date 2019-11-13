from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
import argparse
import ast
import itertools
import queue
import mldebugger.tree as _tree
from mldebugger.quine_mccluskey import reduce_terms
from mldebugger.autodebug_trees import AutoDebug


def find_all_paths(node, keys):
    """
    :param node:
    :param keys:
    :return:
    """
    q = queue.Queue()
    q.put((node, []))
    puregoodpaths = []
    purebadpaths = []
    input_dict = {}

    while (not q.empty()):
        current = q.get()
        if current[0].results is None:
            key = current[0].col
            value = current[0].value
            if key in input_dict:
                if value not in input_dict[key]:
                    input_dict[key].append(value)
            else:
                input_dict[key] = [value]

            q.put((current[0].fb, current[1] + [(key, value, False)]))
            q.put((current[0].tb, current[1] + [(key, value, True)]))
        elif (len(list(current[0].results.items())) > 1):
            continue
        elif (list(current[0].results.items())[0][0]):
            puregoodpaths.append(current[1])
        elif (not list(current[0].results.items())[0][0]):
            purebadpaths.append(current[1])
    return [puregoodpaths, purebadpaths, input_dict]


def from_paths_to_binary(paths, input_dict):
    """
    :param paths:
    :param input_dict:
    :return:
    """
    minterms = []
    flatten = []
    for path in paths:
        bits_dict = {}
        for triple in path:
            bits_dict[(triple[0], triple[1])] = triple[2]
        path_possibilities = []
        for param in list(input_dict.keys()):
            for value in input_dict[param]:
                if (param, value) not in flatten:
                    flatten.append((param, value))
                if (param, value) in bits_dict:
                    path_possibilities.append([str(int(bits_dict[(param, value)]))])
                else:
                    path_possibilities.append(['0', '1'])
        minterms += list(itertools.product(*path_possibilities))
    return [[int(''.join(term), 2) for term in minterms], flatten]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="pipeline entry point")
    parser.add_argument("params", help="parameters and values to be investigated")
    parser.add_argument("--server", type=str, help="host responsible for execution requests")
    parser.add_argument("--receive", type=str, help="port to receive messages on")
    parser.add_argument("--send", type=str, help="port to send messages to")
    parser.add_argument("--budget", type=int, help="maximum number of instances to be tested")
    parser.add_argument("-o", "--one", help="Look for one minimal definitive root cause", action="store_true")
    parser.add_argument("-k", "--k", type=int,
                        help="Number of configurations used to check candidate diagnoses (top k)")

    args = parser.parse_args()
    kw_args = {}
    if args.server:
        kw_args['host'] = args.server
    if args.receive:
        kw_args['receive'] = args.receive
    if args.send:
        kw_args['send'] = args.send
    if args.k:
        kw_args['k'] = args.k
    if args.budget:
        kw_args['max_iter'] = args.budget
    kw_args['first_solution'] = args.one

    filename = args.file
    json_file = open(args.params, "r")
    json_str = json_file.read()
    json_file.close()
    input_dict = ast.literal_eval(json_str)

    autodebug = AutoDebug(**kw_args)
    believedecisive, t, total = autodebug.run(filename, input_dict, ['result'])
    if _tree.get_depth(t) > 0:
        keys = list(input_dict.keys())
        goodpaths, badpaths, input_dict = find_all_paths(t, keys)
        minterms, flatten = from_paths_to_binary(badpaths, input_dict)
        if 0 < len(flatten) < 10:
            s = reduce_terms(len(flatten), minterms)
            results = []
            for prime in s:
                result = []
                for i in range(len(prime)):
                    if prime[i] == '1':
                        comparator = '==' if (
                                    isinstance(flatten[i][1], str) or isinstance(flatten[i][1], str)) else '>='
                        result.append((keys[flatten[i][0]], comparator, str(flatten[i][1])))
                    elif prime[i] == '0':
                        comparator = '!=' if (
                                    isinstance(flatten[i][1], str) or isinstance(flatten[i][1], str)) else '<'
                        result.append((keys[flatten[i][0]], comparator, str(flatten[i][1])))
                results.append(result)
            believedecisive = '\nRoot causes:\n\n %s' % (' \n OR: '.join([' AND '.join([triple[0] +triple[1]+triple[2] for triple in result]) for result in results]))
            print(believedecisive)
        else:
            print(str(believedecisive))
    else:
        print(str(believedecisive))
    return believedecisive