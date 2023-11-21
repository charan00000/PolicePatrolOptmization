import conversions
import contextily as ctx
import find_euler_path
import geopandas as gpd
import matplotlib.pyplot as plt


def plot(geojson_file, time_delay = 0, arrow_spacing = 15):
    # Load the GeoJSON file
    gdf = gpd.read_file(geojson_file)

    # Create a new plot
    fig, ax = plt.subplots()

    # Iterate over the GeoDataFrame
    for i, row in gdf.iterrows():
        # Get the line's start and end points
        if row['geometry'].geom_type == 'MultiLineString' or row['geometry'].geom_type == 'MultiPolygon':
            start = row['geometry'][0].coords[0][:2]
            end = row['geometry'][-1].coords[-1][:2]
        else:
            start = row['geometry'].coords[0][:2]
            end = row['geometry'].coords[-1][:2]

        # Plot the line
        ax.plot(*row['geometry'].xy, color='blue')

        # Add an arrow at the end of the line to represent the direction
        if i % arrow_spacing == 0:
            ax.annotate('', xy=end, xytext=start, arrowprops=dict(facecolor='red', edgecolor='red'))

        #fig.canvas.draw()

        # Add a delay
        if time_delay > 0:
            plt.pause(time_delay)
    
    # Show the plot
    #ctx.add_basemap(ax)
    plt.show()


# these lines are the important ones

conversions.convert_to_graph_road_edges('forsyth_major_bottom_left_roads.geojson',
                                        dest = 'forsyth_major_bottom_left_roads.graphml',
                                        has_properties = True)

total_distance = find_euler_path.modify_graph(graphml_input = 'forsyth_major_bottom_left_roads.graphml',
                                              dest = 'euler_path_output.graphml',
                                              method = "min_weights",
                                              length_unit = "miles")

conversions.convert_to_geojson('euler_path_output.graphml')
print(total_distance)
plot('output_geojson.geojson', time_delay=0)