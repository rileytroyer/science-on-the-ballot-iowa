"""Script to take the shape files for the political boundaries and add identifiers to the json files.

@author Riley Troyer
scipol@rileytroyer.com
"""

# Import libraries
import geopandas as gpd
import json
import pandas as pd

# Define directories
map_dir = 'data/raw/map-files/'
interim_map_dir = 'data/interim/map-files/'
processed_map_dir = 'data/processed/map-files/'

# Read in spatial file
state_rep_gdf = gpd.read_file(map_dir + 'Plan2_House.shp')
state_sen_gdf = gpd.read_file(map_dir + 'Plan2_Senate.shp')
us_rep_gdf = gpd.read_file(map_dir + 'Plan2_Congress.shp')
us_sen_gdf = gpd.read_file(map_dir + 'iowa_border.shp')
gov_gdf = gpd.read_file(map_dir + 'iowa_border.shp')
sec_ag_gdf = gpd.read_file(map_dir + 'iowa_border.shp')
sec_state_gdf = gpd.read_file(map_dir + 'iowa_border.shp')

# Convert to latitude longitude for iowa border files
us_sen_gdf = us_sen_gdf.to_crs('epsg:4326')
gov_gdf = gov_gdf.to_crs('epsg:4326')
sec_ag_gdf = sec_ag_gdf.to_crs('epsg:4326')
sec_state_gdf = sec_state_gdf.to_crs('epsg:4326')

# Write to json files
state_rep_gdf.to_file(interim_map_dir + 'house.json', driver='GeoJSON')
state_sen_gdf.to_file(interim_map_dir + 'senate.json', driver='GeoJSON')
us_rep_gdf.to_file(interim_map_dir + 'congress.json', driver='GeoJSON')
us_sen_gdf.to_file(interim_map_dir + 'us-senate.json', driver='GeoJSON')
gov_gdf.to_file(interim_map_dir + 'gov.json', driver='GeoJSON')
sec_ag_gdf.to_file(interim_map_dir + 'sec-ag.json', driver='GeoJSON')
sec_state_gdf.to_file(interim_map_dir + 'sec-state.json', driver='GeoJSON')

# Read in json file for house senate and congress, these have identifiable names
for filename in ['house.json', 'senate.json', 'congress.json']:
    
    with open(interim_map_dir + filename) as geofile:
        j_file = json.load(geofile)
        
    # Create an id field
    for feature in j_file['features']:
        feature['id'] = feature['properties']['NAME']

    # Write to new json file
    with open(processed_map_dir + filename, 'w') as f:
        json.dump(j_file, f)

# US senate, gov, sec of ag, and sec of state need ID to be set manually
filename = 'us-senate.json'
with open(interim_map_dir + filename) as geofile:
    j_file = json.load(geofile)

# Create an id field
for feature in j_file['features']:
    feature['id'] = 'United States Senator'

# Write to new json file
with open(processed_map_dir + filename, 'w') as f:
    json.dump(j_file, f)
    
# Governor
filename = 'gov.json'
with open(interim_map_dir + filename) as geofile:
    j_file = json.load(geofile)

# Create an id field
for feature in j_file['features']:
    feature['id'] = 'Governor'

# Write to new json file
with open(processed_map_dir + filename, 'w') as f:
    json.dump(j_file, f)    
    

# Sec of Ag
filename = 'sec-ag.json'
with open(interim_map_dir + filename) as geofile:
    j_file = json.load(geofile)

# Create an id field
for feature in j_file['features']:
    feature['id'] = 'Secretary of Agriculture and Land Stewardship'

# Write to new json file
with open(processed_map_dir + filename, 'w') as f:
    json.dump(j_file, f)
    
    
# Sec of State
filename = 'sec-state.json'
with open(interim_map_dir + filename) as geofile:
    j_file = json.load(geofile)

# Create an id field
for feature in j_file['features']:
    feature['id'] = 'Secretary of State'

# Write to new json file
with open(processed_map_dir + filename, 'w') as f:
    json.dump(j_file, f)