#!/usr/bin/env python

"""
This program will extract an edge list from the songs.csv file for viewing
in a graph utility like Cytoscape or Gephi.

    ./edge_list.py Artist Producer

will write a file:

    artist-producer.csv

"""



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
        if not n2 or n1 == n2:
            continue
        g.add_node(n1, {type: 'artist'})
        g.add_node(n2, {type: 'producer'})
        g.add_edge(n1, n2)
        e = g[n1][n2]
        e['weight'] = e.get('weight', 0) + 1

output = open(("%s-%s.csv" % (col1, col2)).lower(), "w")
writer = csv.DictWriter(output, fieldnames=[col1, col2, 'weight'])
writer.writeheader()

for n1, n2 in g.edges():
    writer.writerow({
        col1: n1,
        col2: n2, 
        "weight": g[n1][n2]['weight']
    }) 
