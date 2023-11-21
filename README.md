# PolicePatrolOptmization
3012 proj
This repository is a supplement to our research paper for our combinatorics class.



main_driver: this is where you can run all functions. You can convert a geojson file, as found online on many government platforms, into a graphml file that can be used to find euler circuits, and then convert back into a geojson file. You can visualize the new geojson file using aoftware such as QGIS. When visualizing modified geojsons, make sure to configure labeling so that order labels are displayed, allowing you to see direction in circuits. This label is found as a column in the geo data frame of the output geojson file. 

a graphml file is an XML file that is essentially structured like a graph, containing nodes and edges. THe nodes represent intersections between different roads, and the edges represent small segments of roads thesmelves. The nodes are labeled by their coordinates, which are needed when converting back into geojson. Each edge also stores data contianing the name of the road, and in the future additional properties (speed limits, distance, etc) found on many geojson files for each road segment can be added to the graphml file.

the find_euler_path.modify_graph() function is used to convert a graphml file into one that represnts an euler circuit. The function has three keyword arguments: graphml_input for the input graphml path. 

The third parameter is the method used to eulerize the graph and has 3 options:
  - "base" (default): uses networkx's builtin eulerize function, which connects vertices of odd degree together with no consideration of weight or distance between odd degreed nodes. In the case the graph is already euler, you can leave this parameter at "base"
