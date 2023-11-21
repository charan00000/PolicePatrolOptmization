import conversions
import find_euler_path

conversions.convert_to_graph_road_edges('forsyth_major_bottom_left_roads.geojson', dest = 'forsyth_major_bottom_left_roads.graphml')
find_euler_path.builtin_method(graphml_input = 'forsyth_major_bottom_left_roads.graphml', dest = 'euler_path_output.graphml')
conversions.convert_to_geojson('euler_path_output.graphml')