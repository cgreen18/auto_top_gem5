
import sys



# def twod_paths(next_routers):



#     return twod_paths

nrl_file = sys.argv[1]
vn_file = sys.argv[2]

n_routers = int(sys.argv[3])

nrl = []
with open(nrl_file,'r') as inf:

    cur = 0
    i = 0
    nrl.append([])

    for line in inf:
        
        if '_' in line:
            continue

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


twod_paths = [[[] for __ in range(n_routers)] for _ in range(n_routers)]

for osrc in range(n_routers):
    for odest in range(n_routers):
        print(f'constructing path for {osrc}->...->{odest}')

        cur = osrc

        twod_paths[osrc][odest].append(cur)

        while cur != odest:
            nex = nrl[cur][osrc][odest]
            twod_paths[osrc][odest].append(nex)
            cur = nex


# print(f'paths ({len(twod_paths)})=...')
# for i in range(20):
#     print(f'\t{i} :')
#     for j in range(20):
#         print(f'\t\t{j} : {twod_paths[i][j]}')
# quit()

# print(f'nrl ({len(nrl)})=...')
# for i in range(20):
#     print(f'\t{i} :')
#     for j in range(20):
#         print(f'\t\t{j} : {nrl[i][j]}')
# quit()
        

vn_map = []

with open(vn_file,'r') as inf:
    for line in inf:
        line.strip('\n')
        line_split = line.split(' ')
        line_split = [l for l in line_split if '\n' not in l]

        vn_map.append([])
        for e in line_split:
            vn_map[-1].append(int(e))



print(f'vn_map ({len(vn_map)})=...')
for i in range(20):
    print(f'\t{i} : {vn_map[i]}')


done = False

src = int(input('src:'))
dest = int(input('dest:'))
cur = int(input('cur:'))

print(f'{src} -> {dest} : {twod_paths[src][dest]}')
print(f'\tvn={vn_map[src][dest]}')
print(f'\tnext={nrl[cur][src][dest]}')

while not done:

    src = int(input('src:'))
    dest = int(input('dest:'))
    cur = int(input('cur:'))

    


    if cur == -1:
        done = True
        continue


    print(f'{src} -> {dest} : {twod_paths[src][dest]}')
    print(f'\tvn={vn_map[src][dest]}')
    print(f'\tnext={nrl[cur][src][dest]}')





