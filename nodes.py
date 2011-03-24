# node list spec 

racks = 2
nodes_per_rack = 11

whole_cluster =[ 'node-%02d%02d' % (rack, node)  for rack in range(1, racks +1) for node in range(1, nodes_per_rack + 1)]

rack1 = filter(lambda node: node.startswith('node-01'), whole_cluster) 
rack2 = filter(lambda node: node.startswith('node-02'), whole_cluster) 

