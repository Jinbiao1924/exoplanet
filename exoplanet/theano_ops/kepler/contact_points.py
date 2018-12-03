# -*- coding: utf-8 -*-

from __future__ import division, print_function

__all__ = ["ContactPointsOp"]

import pkg_resources

import numpy as np

import theano
from theano import gof
import theano.tensor as tt


class ContactPointsOp(gof.COp):
    params_type = gof.ParamsType(
        maxiter=theano.scalar.int64,
        tol=theano.scalar.float64,
    )
    __props__ = ("tol", "maxiter")
    func_file = "./contact_points.cc"
    func_name = "APPLY_SPECIFIC(contact_points)"

    def __init__(self, tol=1e-12, maxiter=1000, **kwargs):
        self.tol = float(tol)
        self.maxiter = int(maxiter)
        super(ContactPointsOp, self).__init__(self.func_file, self.func_name)

    # def c_code_cache_version(self):
    #     return (0, 0, 1)

    def c_headers(self, compiler):
        return ["theano_helpers.h", "contact_points.h"]

    def c_header_dirs(self, compiler):
        return [
            pkg_resources.resource_filename(__name__, "include"),
        ]

    def make_node(self, *args):
        if len(args) != 6:
            raise ValueError("expected {0} inputs".format(self.num_input))
        dtype = theano.config.floatX
        in_args = []
        for a in args:
            try:
                a = tt.as_tensor_variable(a)
            except tt.AsTensorError:
                pass
            else:
                dtype = theano.scalar.upcast(dtype, a.dtype)
            in_args.append(a)
        out_args = [in_args[0].type() for i in range(4)]
        return gof.Apply(self, in_args, out_args)

    def infer_shape(self, node, shapes):
        return shapes[0], shapes[0], shapes[0], shapes[0]

    # def grad(self, inputs, gradients):
    #     M, e = inputs
    #     E, f = self(M, e)

    #     bM = tt.zeros_like(M)
    #     be = tt.zeros_like(M)
    #     ecosE = e * tt.cos(E)

    #     if not isinstance(gradients[0].type, theano.gradient.DisconnectedType):
    #         # Backpropagate E_bar
    #         bM = gradients[0] / (1 - ecosE)
    #         be = tt.sin(E) * bM

    #     if not isinstance(gradients[1].type, theano.gradient.DisconnectedType):
    #         # Backpropagate f_bar
    #         sinf2 = tt.sin(0.5*f)
    #         cosf2 = tt.cos(0.5*f)
    #         tanf2 = sinf2 / cosf2
    #         e2 = e**2
    #         ome2 = 1 - e2
    #         ome = 1 - e
    #         ope = 1 + e
    #         cosf22 = cosf2**2
    #         twoecosf22 = 2 * e * cosf22
    #         factor = tt.sqrt(ope/ome)
    #         inner = (twoecosf22+ome) * tt.as_tensor_variable(gradients[1])

    #         bM += factor*(ome*tanf2**2+ope)*inner*cosf22/(ope*ome2)
    #         be += -2*cosf22*tanf2/ome2**2*inner*(ecosE-2+e2)

    #     return [bM, be]

    # def R_op(self, inputs, eval_points):
    #     if eval_points[0] is None:
    #         return eval_points
    #     return self.grad(inputs, eval_points)