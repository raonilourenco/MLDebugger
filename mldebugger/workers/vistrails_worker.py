import argparse
import ast
import logging
import sys
import traceback
import zmq

import vistrails.core.db.io
from vistrails.core.db.locator import UntitledLocator, FileLocator
from vistrails.core.vistrail.controller import VistrailController
from mldebugger.utils import record_python_run

from mldebugger.pipeline import Pipeline

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

is_initialized = False
_application = None
is_not_sync = True


def initialize():
    """Initializes VisTrails.

    You don't have to call this directly. Initialization will happen when you
    start using the API.
    """
    global is_initialized
    global _application

    if is_initialized:
        return False

    # Creates a core application
    _application = vistrails.core.application.init(
        options_dict={
            'installBundles': False,
            'loadPackages': False,
            'enablePackagesSilently': True},
        args=[])

    is_initialized = True
    return True

initialize()


parser = argparse.ArgumentParser()
parser.add_argument("--server", type=str, help="host responsible for execution requests")
parser.add_argument("--receive", type=str, help="port to receive messages on")
parser.add_argument("--send", type=str, help="port to send messages to")
args = parser.parse_args()

if args.server:
    HOST = args.server
else:
    HOST = 'localhost'

if args.receive:
    RECEIVE = args.receive
else:
    RECEIVE = '5557'

if args.send:
    SEND = args.send
else:
    SEND = '5558'

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://{0}:{1}".format(HOST, RECEIVE))

# Socket to send messages to
sender = context.socket(zmq.PUSH)
sender.connect("tcp://{0}:{1}".format(HOST, SEND))

while True:
    # Receiving pipeline instance configuration
    data = receiver.recv()
    logging.debug('Receiving: ' + data)
    fields = data.split("|")
    filename = fields[0]
    parameter_list = ast.literal_eval(fields[1])
    inputs = ast.literal_eval(fields[2])
    outputs = ast.literal_eval(fields[3])

    locator = FileLocator(filename)
    loaded_objs = vistrails.core.db.io.load_vistrail(locator)
    controller = VistrailController(loaded_objs[0], locator,
                                    *loaded_objs[1:])
    controller.do_version_switch(
        controller.get_latest_version_in_graph())
    pipeline = Pipeline(controller)

    kwargs = {}
    for i in range(len(parameter_list)):
        kwargs[inputs[i]] = parameter_list[i]
    try:
        #Executing pipeline instance and retieving the result
        result = pipeline.execute(**kwargs)
        for output in outputs:
            parameter_list.append(str(result.output_port(output)))
    except:
        traceback.print_exc(file=sys.stdout)
        parameter_list.append(str(False))
        kwargs['result'] = parameter_list[-1]
        record_python_run(kwargs, filename)
    logging.debug('Pipeline result: ' + parameter_list[-1])
    #Sending the instance result back to the Algorithm
    sender.send_string(str(parameter_list))
