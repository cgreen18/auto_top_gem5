# Copyright (c) 2016 Georgia Institute of Technology
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

import ast

class OneToOneGarnet(SimpleTopology):
    description='OneToOneGarnet'

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        # Create one router in Garnet. Internally models a crossbar and
        # the associated allocator.
        # For simple network, use Crossbar.py

        verbose = True
        verbose = False

        if verbose:
            print(f'self.nodes ({len(self.nodes)}) = {[(d,d._name) for d in self.nodes]}')
        # quit(-1)

        n_routers = len(self.nodes)

        flat_nr_map_path = options.flat_nr_map_file

        # this is 3d (20x20x20)
        (flat_nr_maps, routing_alg) = self.ingest_flat_map_list(flat_nr_map_path, n_routers)



        routers = [Router(router_id=i,flat_next_router_map=flat_nr_maps[i]) for i in range(n_routers)]

        network.routers = routers

        lid = 0

        # ext_links = [ExtLink(link_id=i, ext_node=n, int_node=routers[i]) for (i, n) in enumerate(self.nodes)]
        ext_links = []
        for i in range(n_routers):
            ext_links.append(ExtLink(link_id=lid, ext_node=self.nodes[i], int_node=routers[i]))
            lid += 1
            if verbose:
                print(f'added ext link #{lid} for r {i} -> node {i}')

        network.ext_links = ext_links

        int_links = []
        # start where ext IDs ended
        # lid = n_routers
        for i in range(n_routers):
            for j in range(n_routers):
                if i==j:
                    continue
                s_name = f'src{i}_dest{j}'
                d_name = f'dest{j}_src{i}'
                int_links.append( IntLink(link_id=lid,
                                        src_outport=s_name,
                                        dst_inport=d_name,
                                        src_node=routers[i],
                                        dst_node=routers[j]) )
                lid += 1
                if verbose:
                    print(f'added int link #{lid} for r {i} -> r {j}')

        network.int_links = int_links

        # important, set network stuff
        ############################################################################################################################3

        flat_vn_map_path = options.flat_vn_map_file

        # its 2d
        flat_vn_map = self.ingest_flat_map(flat_vn_map_path, n_routers)


        network.flat_src_dest_to_evn = flat_vn_map
        network.use_escape_vns = options.use_escape_vns
        network.n_deadlock_free = options.evn_n_deadlock_free
        network.evn_deadlock_partition = options.evn_deadlock_partition
        network.min_n_deadlock_free = options.evn_min_n_deadlock_free

        # should be false
        network.synth_traffic = options.synth_traffic

    def ingest_flat_map(self, path_name, n_routers):
        print(f'ingesting {path_name}')

        r_map = []

        with open(path_name, 'r') as in_file:

            # for _router in range(0,n_routers):
            #     row = in_file.readline()
            for row in in_file:

                row = row.replace('\n','')
                r_conns = row.split(" ")
                if '' in r_conns:
                    r_conns.remove('')
                # print(f'row={row}')
                # print(r_conns)
                # print(type(r_conns[0]))

                try:
                    r_conns = [int(elem) for elem in r_conns]
                except Exception as e:
                    print(f'e={e}')
                    r_conns = [int(float(elem)) for elem in r_conns]

                # r_map.append(r_conns)
                r_map += r_conns

        #input('cont?')

        # assert(len(r_map) == n_routers)b

        return r_map

    def ingest_flat_map_list(self, path_name, n_routers):

        print(f'ingesting {path_name} w/ n_routers {n_routers}')
        # input('cont?')
        routing_alg = None
        flat_nr_map = []

        with open(path_name, 'r') as inf:
            routing_alg = inf.readline()

            # print(f'routing_alg={routing_alg}')

            ln = 0

            for i in range(n_routers):
                # flat_nr_map.append([])
                a_routers_map = []
                for j in range(n_routers):
                    thisline = inf.readline()

                    # print(f'this_line ({ln})={thisline}')


                    as_list = ast.literal_eval(thisline)
                    clean_as_list = [e for e in as_list]

                    # print(f'\trouting table for router {i} '+
                    #     f' row (src) {j} : {clean_as_list}')
                    # flat_nr_map.append(clean_as_list)
                    a_routers_map += clean_as_list
                    ln+=1

                flat_nr_map.append(a_routers_map)


        # print(f'flat_nr_map({len(flat_nr_map)}) = {flat_nr_map}')
        # for alist in flat_nr_map:
        #     for row in alist:
        #         print(f'{row}')
        # quit(-1)

        return (flat_nr_map, routing_alg)
