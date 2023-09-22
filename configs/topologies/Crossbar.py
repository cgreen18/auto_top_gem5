# Copyright (c) 2010 Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from m5.params import *
from m5.objects import *

from topologies.BaseTopology import SimpleTopology

import traceback

class Crossbar(SimpleTopology):
    description='Crossbar'

    def makeTopology(self, options, network, IntLink, ExtLink, Router):

        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet

        # Create an individual router for each controller plus one more for
        # the centralized crossbar.  The large numbers of routers are needed
        # because external links do not model outgoing bandwidth in the
        # simple network, but internal links do.
        # For garnet, one router suffices, use CrossbarGarnet.py

        routers = [Router(router_id=i) for i in range(len(self.nodes)+1)]
        xbar = routers[len(self.nodes)] # the crossbar router is the last router created
        network.routers = routers

        ext_links = [ExtLink(link_id=i, ext_node=n, int_node=routers[i],
                             latency = link_latency)
                        for (i, n) in enumerate(self.nodes)]
        network.ext_links = ext_links

        link_count = len(self.nodes)

        int_links = []
        for i in range(len(self.nodes)):
            int_links.append(IntLink(link_id=(link_count+i),
                                     src_node=routers[i],
                                     dst_node=xbar,
                                     latency = link_latency))

        link_count += len(self.nodes)

        for i in range(len(self.nodes)):
            int_links.append(IntLink(link_id=(link_count+i),
                                     src_node=xbar,
                                     dst_node=routers[i],
                                     latency = link_latency))

        network.int_links = int_links


        print(f'nodes({len(self.nodes)})={self.nodes}')
        for n in self.nodes:
            print(f'n {n} : attrs {n.__dict__}')
            print('-'*72)

        nodes = self.nodes

        l1_caches = [n for n in nodes if n.type == 'L1Cache_Controller']
        l2_caches = [n for n in nodes if n.type == 'L2Cache_Controller']
        dirs = [n for n in nodes if n.type == 'Directory_Controller']
        dmas = [n for n in nodes if n.type == 'DMA_Controller']
        others = [n for n in nodes if n not in l1_caches and n not in l2_caches and n not in dirs and n not in dmas]


        print(f'l1_caches({len(l1_caches)})={l1_caches}')
        print(f'l2_caches({len(l2_caches)})={l2_caches}')
        print(f'dirs({len(dirs)})={[(d,d._name) for d in dirs]}')
        print(f'dmas({len(dmas)})={[(d,d._name) for d in dmas]}')
        print(f'others({len(others)})={[(d,d._name) for d in others]}')

        # for line in traceback.format_stack():
        #     print(line.strip())


        # quit(-1)

        # important, set network stuff
        ############################################################################################################################3

        # network.flat_src_dest_to_evn = flat_vn_map
        network.use_escape_vns = options.use_escape_vns
        network.n_deadlock_free = options.evn_n_deadlock_free
        network.evn_deadlock_partition = options.evn_deadlock_partition
        network.min_n_deadlock_free = options.evn_min_n_deadlock_free

        # should be false
        network.synth_traffic = options.synth_traffic

