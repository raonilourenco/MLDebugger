from future import standard_library
standard_library.install_aliases()
from builtins import zip
from builtins import next
from past.builtins import basestring
from builtins import object
import vistrails.core.db.action


from vistrails.core.modules.module_registry import get_module_registry
from vistrails.core.vistrail.pipeline import Pipeline as _Pipeline
from vistrails.core.system import get_vistrails_basic_pkg_id
from vistrails.core.vistrail.module_function import ModuleFunction
from vistrails.core.vistrail.module_param import ModuleParam
from vistrails.core.interpreter.default import get_default_interpreter

__all__ = ['Vistrail', 'Pipeline', 'Module', 'Package',
           'ExecutionResults', 'ExecutionErrors', 'Function',
           'ipython_mode', 'load_vistrail', 'load_pipeline', 'load_package',
           'output_mode', 'run_vistrail',
           'NoSuchVersion', 'NoSuchPackage']


class Pipeline(object):
    """This class represents a single Pipeline.

    It now does have a controller.
    """
    vistrail = None
    version = None
    _inputs = None
    _outputs = None
    _html = None
    controller = None
    locator = None

    def __init__(self, controller=None, vistrail=None):
        self.controller = controller
        self.locator = controller.locator
        pipeline = controller.current_pipeline
        if pipeline is None:
            self.pipeline = _Pipeline()
        elif isinstance(pipeline, _Pipeline):
            self.pipeline = pipeline
        elif isinstance(pipeline, basestring):
            raise TypeError("Pipeline was constructed from %r.\n"
                            "Use load_pipeline() to get a Pipeline from a "
                            "file." % type(pipeline).__name__)
        else:
            raise TypeError("Pipeline was constructed from unexpected "
                            "argument type %r" % type(pipeline).__name__)
        if vistrail is not None:
            if (isinstance(vistrail, tuple) and len(vistrail) == 2 and
                    isinstance(vistrail[0], Vistrail)):
                self.vistrail, self.version = vistrail
            else:
                raise TypeError("Pipeline got unknown type %r as 'vistrail' "
                                "argument" % type(vistrail).__name__)

    @property
    def modules(self):
        for module in self.pipeline.module_list:
            yield Module(descriptor=module.module_descriptor,
                         module_id=module.id,
                         pipeline=self)

    def execute(self, *args, **kwargs):
        """Execute the pipeline.

        Positional arguments are either input values (created from
        ``module == value``, where `module` is a Module from the pipeline and
        `value` is some value or Function instance) for the pipeline's
        InputPorts, or Module instances (to select sink modules).

        Keyword arguments are also used to set InputPort by looking up inputs
        by name.

        Example::

           input_bound = pipeline.get_input('higher_bound')
           input_url = pipeline.get_input('url')
           sinkmodule = pipeline.get_module(32)
           pipeline.execute(sinkmodule,
                            input_bound == vt.Function(Integer, 10),
                            input_url == 'http://www.vistrails.org/',
                            resolution=15)  # kwarg: only one equal sign
        """
        pipeline = self.pipeline
        sinks = set()
        inputs = {}

        reg = get_module_registry()
        InputPort_desc = reg.get_descriptor_by_name(
            get_vistrails_basic_pkg_id(),
            'InputPort')

        # Read args
        for arg in args:
            if isinstance(arg, ModuleValuePair):
                if arg.module.id in inputs:
                    raise ValueError(
                        "Multiple values set for InputPort %r" %
                        get_inputoutput_name(arg.module))
                if not reg.is_descriptor_subclass(arg.module.module_descriptor,
                                                  InputPort_desc):
                    raise ValueError("Module %d is not an InputPort" %
                                     arg.module.id)
                inputs[arg.module.id] = arg.value
            elif isinstance(arg, Module):
                sinks.add(arg.module_id)

        # Read kwargs
        for key, value in kwargs.items():
            name = key
            key = self.get_python_parameter(key)  # Might raise KeyError
            if name in inputs:
                raise ValueError("Multiple values set for input %r" %
                                 name)
            inputs[name] = [key.module_id, value]

        reason = "API pipeline execution"
        sinks = sinks or None

        # Use controller only if no inputs were passed in
        if (not inputs and self.vistrail is not None and
                self.vistrail.current_version == self.version):
            controller = self.vistrail.controller
            results, changed = controller.execute_workflow_list([[
                controller.locator,  # locator
                self.version,  # version
                self.pipeline,  # pipeline
                DummyView(),  # view
                None,  # custom_aliases
                None,  # custom_params
                reason,  # reason
                sinks,  # sinks
                None,  # extra_info
            ]])
            result, = results
        else:
            # pipeline = self.pipeline
            if inputs:
                # id_scope = IdScope(1)
                # pipeline = pipeline.do_copy(False, id_scope)

                # A hach to get ids from id_scope that we know won't collide:
                # make them negative
                # id_scope.getNewId = lambda t, g=id_scope.getNewId: -g(t)

                # create_module = \
                #       VistrailController.create_module_from_descriptor_static
                # create_function = VistrailController.create_function_static
                # create_connection = VistrailController.create_connection_static
                # Fills in the ExternalPipe ports

                for name, input_list in inputs.items():
                    module_id, values = input_list
                    module = pipeline.modules[module_id]
                    if not isinstance(values, (list, tuple)):
                        values = [values]
                    '''
                    # Guess the type of the InputPort
                    _, sigstrings, _, _, _ = get_port_spec_info(pipeline, module)
                    sigstrings = parse_port_spec_string(sigstrings)

                    # Convert whatever we got to a list of strings, for the
                    # pipeline
                    values = [reg.convert_port_val(val, sigstring, None)
                              for val, sigstring in izip(values, sigstrings)]

                    if len(values) == 1:
                        # Create the constant module
                        constant_desc = reg.get_descriptor_by_name(
                                *sigstrings[0])
                        #print('Setting desription: ',str(constant_desc),str(sigstrings[0]))
                        constant_mod = create_module(id_scope, constant_desc)
                        func = create_function(id_scope, constant_mod,
                                               'value', values)
                        constant_mod.add_function(func)
                        pipeline.add_module(constant_mod)

                        # Connect it to the ExternalPipe port
                        conn = create_connection(id_scope,
                                                 constant_mod, 'value',
                                                 module, 'ExternalPipe')
                        pipeline.db_add_connection(conn)
                    else:
                        raise RuntimeError("TODO : create tuple")

                    '''
                    port_spec = reg.get_input_port_spec(module, name)
                    added_functions = {}
                    tmp_f_id = -1
                    tmp_p_id = -1
                    function = [f for f in module.functions
                                if f.name == port_spec.name]
                    if function:
                        function = function[0]
                    else:
                        try:
                            function = added_functions[(module.id, port_spec.name)]
                        except KeyError:
                            # add to function list
                            params = []
                            for psi in port_spec.port_spec_items:
                                parameter = ModuleParam(id=tmp_p_id,
                                                        pos=psi.pos,
                                                        name='<no description>',
                                                        val=psi.default,
                                                        type=psi.descriptor.sigstring)
                                params.append(parameter)
                                tmp_p_id -= 1
                            function = ModuleFunction(id=tmp_f_id,
                                                      pos=module.getNumFunctions(),
                                                      name=port_spec.name,
                                                      parameters=params)
                            tmp_f_id -= 1
                            added_functions[(module.id, port_spec.name)] = function
                            action = vistrails.core.db.action.create_action([('add',
                                                                              function,
                                                                              module.vtType,
                                                                              module.id)])
                            # function_actions.append(action)
                    parameter = function.params[0]
                    # find old parameter
                    old_param = parameter
                    actions = []

                    for v in values:
                        desc = reg.get_descriptor_by_name('org.vistrails.vistrails.basic', 'String', None)
                        if not isinstance(v, str):
                            str_value = desc.module.translate_to_string(v)
                        else:
                            str_value = v
                        new_param = ModuleParam(id=tmp_p_id,
                                                pos=old_param.pos,
                                                name=old_param.name,
                                                alias=old_param.alias,
                                                val=str_value,
                                                type=old_param.type)
                        tmp_p_id -= 1
                        action_spec = ('change', old_param, new_param,
                                       function.vtType, function.real_id)
                        action = vistrails.core.db.action.create_action([action_spec])
                        actions.append(action)
                        # controller = self.vistrail.controller
                        self.controller.perform_action(action)
            #########################################################################

            interpreter = get_default_interpreter()
            result = interpreter.execute(pipeline, locator=self.locator,
                                         reason=reason,
                                         sinks=sinks, actions=actions)

        if result.errors:
            raise ExecutionErrors(self, result)
        else:
            return ExecutionResults(self, result)

    def get_module(self, module_id):
        if isinstance(module_id, int):  # module id
            module = self.pipeline.modules[module_id]
        elif isinstance(module_id, basestring):  # module name
            def desc(mod):
                if '__desc__' in mod.db_annotations_key_index:
                    return mod.get_annotation_by_key('__desc__').value
                else:
                    return None

            modules = [mod
                       for mod in self.pipeline.modules.values()
                       if desc(mod) == module_id]
            if not modules:
                raise KeyError("No module with description %r" % module_id)
            elif len(modules) > 1:
                raise ValueError("Multiple modules with description %r" %
                                 module_id)
            else:
                module, = modules

        else:
            raise TypeError("get_module() expects a string or integer, not "
                            "%r" % type(module_id).__name__)
        return Module(descriptor=module.module_descriptor,
                      module_id=module.id,
                      pipeline=self)

    def _get_inputs_or_outputs(self, module_name):
        reg = get_module_registry()
        desc = reg.get_descriptor_by_name(
            'org.vistrails.vistrails.basic',
            module_name)
        modules = {}
        for module in self.pipeline.modules.values():
            if module.module_descriptor is desc:
                name = get_inputoutput_name(module)
                if name is not None:
                    modules[name] = module
        return modules

    def get_python_parameter(self, parameter_name):
        try:
            reg = get_module_registry()
            desc = reg.get_descriptor_by_name(
                'org.vistrails.vistrails.basic',
                'PythonSource')
            for module in self.pipeline.modules.values():
                if module.module_descriptor is desc:
                    for function in module.input_port_specs:
                        if function.name == parameter_name:
                            return Module(descriptor=module.module_descriptor,
                                          module_id=module.id,
                                          pipeline=self)
        except KeyError:
            raise KeyError("No PythonSource  module with name %r" % name)

    def get_input(self, name):
        try:
            module = self._get_inputs_or_outputs('InputPort')[name]
        except KeyError:
            raise KeyError("No InputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    def get_output(self, name):
        try:
            module = self._get_inputs_or_outputs('OutputPort')[name]
        except KeyError:
            raise KeyError("No OutputPort module with name %r" % name)
        else:
            return Module(descriptor=module.module_descriptor,
                          module_id=module.id,
                          pipeline=self)

    @property
    def inputs(self):
        if self._inputs is None:
            self._inputs = list(self._get_inputs_or_outputs('InputPort').keys())
        return self._inputs

    @property
    def outputs(self):
        if self._outputs is None:
            self._outputs = list(self._get_inputs_or_outputs('OutputPort').keys())
        return self._outputs

    def __repr__(self):
        desc = "<%s: %d modules, %d connections" % (
            self.__class__.__name__,
            len(self.pipeline.modules),
            len(self.pipeline.connections))
        inputs = self.inputs
        if inputs:
            desc += "; inputs: %s" % ", ".join(inputs)
        outputs = self.outputs
        if outputs:
            desc += "; outputs: %s" % ", ".join(outputs)
        return desc + ">"

    def _repr_html_(self):
        if self._html is None:
            import cgi
            try:
                from io import StringIO
            except ImportError:
                from io import StringIO

            self._html = ''

            # http://www.graphviz.org/doc/info/shapes.html
            dot = ['digraph {\n    node [shape=plaintext];']

            # {moduleId: (input_ports, output_ports)}
            modules = dict((mod.id, (set(), set()))
                           for mod in self.pipeline.module_list)
            for conn in self.pipeline.connection_list:
                src, dst = conn.source, conn.destination
                modules[src.moduleId][1].add(src.name)
                modules[dst.moduleId][0].add(dst.name)

            # {moduleId: ({input_port_name: input_num},
            #             {output_port_name: output_num})
            # where input_num and output_num are just some sequences of numbers
            modules = dict((mod_id,
                            (dict((n, i) for i, n in enumerate(mod_ports[0])),
                             dict((n, i) for i, n in enumerate(mod_ports[1]))))
                           for mod_id, mod_ports in modules.items())

            # Write out the modules
            for mod, port_lists in modules.items():
                labels = []
                for port_type, ports in zip(('in', 'out'), port_lists):
                    label = ('<td port="%s%s">%s</td>' % (port_type, port_num, cgi.escape(port_name))
                             for port_name, port_num in ports.items())
                    labels.append(''.join(label))

                label = ['<table border="0" cellborder="0" cellspacing="0">']
                if labels[0]:
                    label += ['<tr><td><table border="0" cellborder="1" cellspacing="0"><tr>', labels[0],
                              '</tr></table></td></tr>']
                mod_obj = self.pipeline.modules[mod]
                if '__desc__' in mod_obj.db_annotations_key_index:
                    name = (mod_obj.get_annotation_by_key('__desc__')
                            .value.strip())
                else:
                    name = mod_obj.label
                label += ['<tr><td border="1" bgcolor="grey"><b>', cgi.escape(name), '</b></td></tr>']
                if labels[1]:
                    label += ['<tr><td><table border="0" cellborder="1" cellspacing="0"><tr>', labels[1],
                              '</tr></table></td></tr>']
                label += ['</table>']
                dot.append('    module%d [label=<%s>];' % (mod, '\n'.join(label)))
            dot.append('')

            # Write out the connections
            for conn in self.pipeline.connection_list:
                src, dst = conn.source, conn.destination
                dot.append('    module%d:out%d -> module%d:in%d;' % (
                    src.moduleId,
                    modules[src.moduleId][1][src.name],
                    dst.moduleId,
                    modules[dst.moduleId][0][dst.name]))

            dot.append('}')
            try:
                proc = subprocess.Popen(['dot', '-Tsvg'],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                svg, _ = proc.communicate('\n'.join(dot))
                if proc.wait() == 0:
                    self._html += svg
            except OSError:
                pass
            self._html += '<pre>' + cgi.escape(repr(self)) + '</pre>'
        return self._html


def get_inputoutput_name(module):
    for function in module.functions:
        if function.name == 'name':
            if len(function.params) == 1:
                return function.params[0].strValue
    return None


class ExecutionErrors(Exception):
    """Errors raised during a pipeline execution.
    """

    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._errors = resultobj.errors

    def __str__(self):
        return "Pipeline execution failed: %d error%s:\n%s" % (
            len(self._errors),
            's' if len(self._errors) >= 2 else '',
            '\n'.join('%d: %s' % p for p in self._errors.items()))


class ExecutionResults(object):
    """Contains the results of a pipeline execution.
    """

    def __init__(self, pipeline, resultobj):
        self.pipeline = pipeline
        self._objects = resultobj.objects

    def output_port(self, output):
        """Gets the value passed to an OutputPort module with that name.
        """
        if isinstance(output, basestring):
            outputs = self.pipeline._get_inputs_or_outputs('OutputPort')
            module_id = outputs[output].id
        else:
            raise TypeError("output_port() expects a string, not %r" %
                            type(output).__name__)
        return self._objects[module_id].get_output('ExternalPipe')

    def module_output(self, module):
        """Gets all the output ports of a specified module.
        """
        if not isinstance(module, Module):
            module = self.pipeline.get_module(module)
        return self._objects[module.module_id].outputPorts

    def __repr__(self):
        return "<ExecutionResult: %d modules>" % len(self._objects)


class Module(object):
    """Wrapper for a module, which can be in a Pipeline or not yet.
    """
    module_id = None
    pipeline = None

    def __init__(self, descriptor, **kwargs):
        self.descriptor = descriptor
        if 'module_id' and 'pipeline' in kwargs:
            self.module_id = kwargs.pop('module_id')
            self.pipeline = kwargs.pop('pipeline')
            if not (isinstance(self.module_id, int) and
                    isinstance(self.pipeline, Pipeline)):
                raise TypeError
        elif 'module_id' in kwargs or 'pipeline' in kwargs:
            raise TypeError("Module was given an id but no pipeline")

        if kwargs:
            raise TypeError("Module was given unexpected argument: %r" %
                            next(iter(kwargs)))

    @property
    def module(self):
        if self.module_id is None:
            raise ValueError("This module is not part of a pipeline")
        return self.pipeline.pipeline.modules[self.module_id]

    @property
    def module_class(self):
        return ModuleClass(self.descriptor)

    @property
    def name(self):
        if self.module_id is None:
            raise ValueError("This module is not part of a pipeline")
        mod = self.pipeline.pipeline.modules[self.module_id]
        if '__desc__' in mod.db_annotations_key_index:
            return mod.get_annotation_by_key('__desc__').value
        else:
            return None

    def __repr__(self):
        desc = "<Module %r from %s" % (self.descriptor.name,
                                       self.descriptor.identifier)
        if self.module_id is not None:
            desc += ", id %d" % self.module_id
            if self.pipeline is not None:
                mod = self.pipeline.pipeline.modules[self.module_id]
                if '__desc__' in mod.db_annotations_key_index:
                    desc += (", name \"%s\"" %
                             mod.get_annotation_by_key('__desc__').value)
        return desc + ">"

    def __eq__(self, other):
        if isinstance(other, Module):
            if self.module_id is None:
                return other.module_id is None
            else:
                if other.module_id is None:
                    return False
                return (self.module_id == other.module_id and
                        self.pipeline == other.pipeline)
        else:
            return ModuleValuePair(self.module, other)
