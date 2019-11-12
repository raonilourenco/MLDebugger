from builtins import str
from builtins import range
from builtins import object
import os
import pytest
import zmq
import mldebugger.tree as _tree

from mldebugger.autodebug_trees import AutoDebug
from mldebugger.quine_mccluskey import reduce_terms
from mldebugger.run import find_all_paths, from_paths_to_binary

@pytest.mark.incremental
class TestBudget(object):

    def kill(self):
        context = zmq.Context()
        sender = context.socket(zmq.PUSH)
        sender.bind("tcp://{0}:{1}".format("*", '5557'))
        receiver = context.socket(zmq.PULL)
        receiver.bind("tcp://{0}:{1}".format("*", '5558'))
        poller = zmq.Poller()
        poller.register(receiver, zmq.POLLIN)

        sender.send_string('kill')

        poller.unregister(receiver)
        receiver.close()
        sender.close()
        context.term()

    def test_diagnosis_false(self):
        os.system("python_worker & disown")
        space = {'p0':['a','b','c','d','e','f'],'p1':[0,1,2],'p2':['a','b','c','d','e','f']}
        filename = 'test/test_diagnosis.vt'
        outputs = ['result']

        believedecisive, t, total = AutoDebug().run(filename, space, outputs)
        if _tree.get_depth(t) > 0:
            keys = list(space.keys())
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
                assert ('p1','>=','1') in result
            else:
                assert False
        else:
            assert False

        self.kill()

        assert True



