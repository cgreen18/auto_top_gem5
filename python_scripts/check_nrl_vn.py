import sys
import networkx as nx

verbose = False

def networkx_get_cycle(cdg):

    cycle = []

    G = nx.DiGraph()

    for src, depens in enumerate(cdg):
        for dest in depens:
            G.add_edge(src, dest)

    try:
        cycle = list(nx.find_cycle(G))

        if verbose:
            print(f'networkx found cycle: {cycle}')
        return cycle

    except:
        return []

def translate_cycle(cycle,node_to_channel_map):
    for a,b in cycle:
        print(f'{node_to_channel_map[a].split(":")[0]}->',end='')
    print('')

# IMPORTANT: path_list is flat.
#           determine src/dest by indexing w/ [0]/[-1]
def create_a_cdg_from_paths( path_list, n_links):

    channel_to_node_map = {}
    node_to_channel_map = {}

    channel_number = 0
    cnum1 = 0
    cnum2 = 0

    cdg_adj_list = [[] for _ in range(n_links)]

    for path in path_list:

        # 1/2 node paths cannot have turns
        # theres only one edge

        for i in range(len(path) - 2):
            # print(f'====================\npath={path}')
            src = path[i]
            mid = path[i+1]
            dest = path[i+2]

            channel_name1 = str(src)+":"+str(mid)
            if channel_name1 in channel_to_node_map:
                cnum1 = channel_to_node_map[channel_name1]
            else:
                cnum1 = channel_number
                channel_to_node_map[channel_name1] = cnum1
                node_to_channel_map[cnum1] = channel_name1
                channel_number += 1
            # print (channel_name1 + "--->" + str(cnum1))
                # edge_name_dict[src].update({mid:cnum1})

            channel_name2 = str(mid)+":"+str(dest)
            if channel_name2 in channel_to_node_map:
                cnum2 = channel_to_node_map[channel_name2]
            else:
                cnum2 = channel_number
                channel_to_node_map[channel_name2] = cnum2
                node_to_channel_map[cnum2] = channel_name2
                channel_number += 1
            # print (channel_name2 + "--->" + str(cnum2))
                # edge_name_dict[mid].update({dest:cnum2})

            if cnum2 in cdg_adj_list[cnum1]:
                pass                                 # turn already exists in CDG; ignore
            else:
                cdg_adj_list[cnum1].append(cnum2)    # add turn to CDG

    if verbose:
        print(f'completed creation of cdg from path set')
        print_cdg_list([cdg_adj_list])

    # quit()

    return cdg_adj_list.copy(), node_to_channel_map, channel_to_node_map

def ingest_vn_local(vn_path):
    vn_map = []

    with open(vn_path,'r') as inf:
        for line in inf:
            line.strip('\n')
            line_split = line.split(' ')
            line_split = [l for l in line_split if '\n' not in l]

            vn_map.append([])
            for e in line_split:
                vn_map[-1].append(int(e))
    return vn_map

def ingest_nrl_local( nrl_name, n_routers):
    if True:#self.verbose:
        print(f'Ingesting nrl {nrl_name}')
    
    nrl = []
    with open(nrl_name,'r') as inf:

        cur = 0
        i = 0
        nrl.append([])

        for line in inf:
            
            if '_' in line:
                continue

            # nrl.append([])

            line = line.strip('\n')
            line = line.replace('[','')
            line = line.replace(']','')
            # print(f'line = {line}')
            line_split = line.split(' ')
            line_split = [l for l in line_split if '\n' not in l]

            # print(f'nrl={nrl}')

            nrl[cur].append([])
            
            for e in line_split:
                e = e.strip(',')
                nrl[cur][-1].append(int(e))

            # print(f'i={i}')

            i += 1
            if i == n_routers:
                i = 0
                cur += 1
                nrl.append([])

    # for r in nrl:
    #     print(f'+ {r}')

    # print(f'nrl len={len(nrl)}')

    return nrl

def flatten_pathlist(twod_pl):
    oned_pl = []
    for src, row in enumerate(twod_pl):
        for dest, path in enumerate(row):
            oned_pl.append(path)
    return oned_pl

def prune_pathlist(oned_pl, vn_map, vn_interest):
    new_pl = []
    for p in oned_pl:
        s = p[0]
        d = p[-1]

        if vn_map[s][d] == vn_interest:
            new_pl.append(p)
    return new_pl

# only local vars
def verify_nrl_vn_files( nrl_path, vn_path):

    vm = ingest_vn_local(vn_path)
    n_routers = len(vm)
    nrl = ingest_nrl_local(nrl_path, n_routers)

    checksum = 0
    for row in vm:
        for e in row:
            checksum += hash(e)

    print(f'checksum={checksum}')
    checksum = 0
    for src_r in nrl:
        for row in src_r:
            for e in row:
                checksum += hash(e)

    print(f'checksum={checksum}')
    # quit()

    twod_paths = [[[] for __ in range(n_routers)] for _ in range(n_routers)]

    for osrc in range(n_routers):
        for odest in range(n_routers):
            # print(f'constructing path for {osrc}->...->{odest}')

            cur = osrc

            twod_paths[osrc][odest].append(cur)

            while cur != odest:
                nex = nrl[cur][osrc][odest]
                twod_paths[osrc][odest].append(nex)
                cur = nex

    checksum = 0
    for src in twod_paths:
        for path in src:
            for e in path:
                checksum += hash(e)
    print(f'checksum={checksum}')
    # quit()

    flat_pl = flatten_pathlist(twod_paths)

    checksum = 0
    for path in flat_pl:
        for e in path:
            checksum += hash(e)
    print(f'checksum={checksum}')
    # quit()

    n_vns = 1
    for row in vm:
        # print(f'vm row={row}')
        n_vns = max(n_vns, max(row))

    n_links = n_routers*10
    
    for vn in range(n_vns + 1):

        vnet_pl = prune_pathlist(flat_pl, vm, vn)

        checksum = 0
        for path in vnet_pl:
            for e in path:
                checksum += hash(e)
        print(f'checksum={checksum}')
        # quit()


        my_cdg, ntc_map, ctn_map = create_a_cdg_from_paths(vnet_pl, n_links)

        checksum = 0
        for row in my_cdg:
            for e in row:
                checksum += hash(e)
        print(f'checksum={checksum}')
        # quit()
        # my_cdg = create_a_cdg_from_paths(vnet_pl, n_links)


        cycle = networkx_get_cycle(my_cdg)

        print(f'printing cycle for vn {vn}')
        translate_cycle(cycle, ntc_map)

        assert(len(cycle) == 0)

if __name__ == '__main__':


    # nrl_path = sys.argv[1]
    # vn_path = sys.argv[2]

    # print(f'nrl {nrl_path}')
    # print(f'vn {vn_path}')

    # verify_nrl_vn_files( nrl_path, vn_path)

    # for topo in topos:

    topo = sys.argv[1]

    nrl_path = f'configs/topologies/nr_list3/{topo}_naive.nrl'
    vn_path = f'configs/topologies/vn_maps3/{topo}_naive_hops_3vns.vn'

    print(f'nrl {nrl_path}')
    print(f'vn {vn_path}')

    verify_nrl_vn_files( nrl_path, vn_path)