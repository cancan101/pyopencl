from __future__ import division

from IPython.core.magic import (magics_class, Magics, cell_magic, line_magic)
from IPython.core.magics.code import (CodeMagics)


import pyopencl as cl


@magics_class
class PyOpenCLMagics(Magics):
    @cell_magic
    def cl_kernel(self, line, cell):
        try:
            ctx = self.shell.user_ns["cl_ctx"]
        except KeyError:
            ctx = None

        if not isinstance(ctx, cl.Context):
            ctx = None

        if ctx is None:
            try:
                ctx = self.shell.user_ns["ctx"]
            except KeyError:
                ctx = None

        if ctx is None or not isinstance(ctx, cl.Context):
            raise RuntimeError("unable to locate cl context, which must be "
                    "present in namespace as 'cl_ctx' or 'ctx'")

        prg = cl.Program(ctx, cell.encode("utf8")).build(options=line.encode("utf8").strip())

        for knl in prg.all_kernels():
            self.shell.user_ns[knl.function_name] = knl

@magics_class
class PyOpenCLCodeMagics(CodeMagics):
    @line_magic
    def cl_kernel_file(self, line):
        opts,args = self.parse_options(line,'o:f:')

        header = "%%cl_kernel"

        build_options = opts.get('o')

        if build_options:
            header = "%s %s" % (header, build_options)

        kernel = self.shell.find_user_code(opts.get('f') or args)

        content = "%s\n\n%s" % (header, kernel)

        self.shell.set_next_input(content)


def load_ipython_extension(ip):
    ip.register_magics(PyOpenCLMagics)
    ip.register_magics(PyOpenCLCodeMagics)

