
from sys import int_info
from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from topologies.BaseTopology import SimpleTopology

import math

class Simple_Misaligned(SimpleTopology):
    description='Simple_Misaligned'

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes


        n_cpus = options.num_cpus
        n_dirs = options.num_dirs

        # N_CPUS = 64
        # assert(n_cpus == N_CPUS)
        # for now equal dirs to cpus
        assert(n_dirs == n_cpus)

        # no dma controllers
        assert('DMA_Controller' not in [n.type for n in nodes])

        caches = [n for n in nodes if n.type != 'Directory_Controller']
        dirs = [n for n in nodes if n.type == 'Directory_Controller']

        print(f'caches({len(caches)})={caches}')
        print(f'dirs({len(dirs)})={dirs}')

        assert(n_cpus == len(caches))
        assert(n_dirs == len(dirs))

        # nothing else (dma)
        assert(n_cpus + n_dirs == len(nodes))

        # obligatory required sets
        link_latency = options.link_latency
        router_latency = options.router_latency

        # Will be part of self later
        # TODO make cla?
        n_routers = 20
        per_row = 5
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(n_routers)]

        print(f'routers({len(routers)})={routers}')

        int_links = []
        ext_links = []

        cpu_dir_to_router_map = []

        
        # ext links
        # l1s/dirs -> routers
        link_count = 0
        n_set = 0

        for idx, router in enumerate(routers):
            row = idx // per_row
            col = idx % per_row

            # default interior with 4 cpus per router
            cpus_per_router = 4

            # edge if col == 0 or col == per_row-1
            if col == 0 or col == per_row - 1:
                cpus_per_router = 2

            for i in range(cpus_per_router):
                src = n_set
                dest = idx
                print(f'Adding external link: l1 cache node {src} <-> router {dest} ')
                ext_links.append(ExtLink(link_id=link_count,
                                        ext_node= caches[src],
                                        int_node= router,
                                        latency=link_latency))
                link_count += 1
                print(f'Adding external link: dir node {src} <-> router {dest}')
                ext_links.append(ExtLink(link_id=link_count,
                                        ext_node= dirs[src],
                                        int_node= router,
                                        latency=link_latency))
                link_count += 1
                n_set += 1


        # int links
        # routers -> routers
        # based on topology .sol file
        map_file = options.router_map_file
        r_map = self.ingest(map_file)

        for src_r in range(n_routers):
            for dest_r, is_connected in enumerate(r_map[src_r]):
                assert(src_r < n_routers)
                assert(dest_r < n_routers)
                if(src_r == dest_r):
                        continue

                if(is_connected == 1):
                        print(f'Adding internal link {src_r}->{dest_r}')
                        s_name = f'r{src_r}_lc{link_count}'
                        d_name = f'r{dest_r}_lc{link_count}'
                        # add link
                        int_links.append(IntLink(link_id=link_count,
                                            src_node=routers[src_r],
                                            dst_node=routers[dest_r],
                                            src_outport=s_name,
                                            dst_inport=d_name,
                                            latency = link_latency,
                                            weight=1))
                        link_count += 1

        # Required to be set
        network.int_links = int_links
        network.ext_links = ext_links
        network.routers = routers

    # # Register nodes with filesystem
    # def registerTopology(self, options):
        
    #     # closest_power_of_two = int(math.log(options.num_cpus,2))**2
    #     # # if():
    #     # print(f'closest_power_of_two={closest_power_of_two}')
    #     # per_cpu = MemorySize(options.mem_size) // closest_power_of_two
    #     # for i in range(closest_power_of_two):
    #     #     FileSystemConfig.register_node([i],
    #     #             per_cpu, i)

    #     # n_cpus = 16
    #     # per_cpu = MemorySize(options.mem_size) // 16
    #     # for i in range(n_cpus):
    #     #     FileSystemConfig.register_node([i],
    #     #             per_cpu, i)


    #     n_cpus = options.num_cpus
    #     per_cpu = MemorySize(options.mem_size) // n_cpus
    #     print(f'per_cpu={per_cpu}')
    #     for i in range(n_cpus):
    #         FileSystemConfig.register_node([i],
    #                 per_cpu, i)

    # read from file a 2d matrix of router to router map and return matrix
    def ingest(self, file_name):
        r_map = []

        with open(file_name, 'r') as in_file:
            n_routers = in_file.readline()
            n_ports = in_file.readline()

            n_routers = int(n_routers)
            n_ports = int(n_ports)

            for r in range(0,n_routers):
                row = in_file.readline()
                r_conns = row.split(" ")

                # for e in r_conns:
                #     print(e)
                #     print(type(e))

                try:
                    r_conns = [int(elem) for elem in r_conns]
                except:
                    r_conns = [int(float(elem)) for elem in r_conns]
                r_map.append(r_conns)

        for i in range(n_routers):
            r_map[i][i] = 0

        return r_map