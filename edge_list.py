#!/usr/bin/env python

import sys
import csv
import networkx

col1 = sys.argv[1]
col2 = sys.argv[2]

g = networkx.DiGraph()

input_data = csv.DictReader(open("songs.csv"))

for row in input_data:
    n1 = row[col1]
    for n2 in row[col2].split(","):
        if not col2:
            continue
        g.add_node(n1)
        g.add_node(n2)
        g.add_edge(n1, n2)
        e = g[n1][n2]
        e['weight'] = e.get('weight', 0) + 1

writer = csv.DictWriter(
    open("%s-%s.csv" % (col1, col2), "w"),
    fieldnames=[col1, col2, 'weight']
)
writer.writeheader()

for n1, n2 in g.edges():
    writer.writerow({
        col1: n1,
        col2: n2, 
        "weight": g[n1][n2]['weight']
    }) 
