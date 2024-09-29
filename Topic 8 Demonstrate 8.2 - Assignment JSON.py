import folium
import json

# Load the schools geojson data
with open('schools.geojson') as f_schools:
    schools_data = json.load(f_schools)

# Load the universities json data
with open('univ.json') as f_universities:
    universities_data = json.load(f_universities)

# Filter Big 12 schools based on NCAA code 108
big_12_schools = [school for school in universities_data if school.get('NCAA', {}).get('NAIA conference number football (IC2020)') == 108]

# Create a mapping for faster access to geojson data by university name
geojson_school_mapping = {school['properties']['NAME']: school for school in schools_data['features']}

# Initialize a map centered over Texas
texas_map = folium.Map(location=[31.9686, -99.9018], zoom_start=6)

# Iterate through the filtered Big 12 schools
for school in big_12_schools:
    school_name = school['instnm']
    total_enrollment = school.get('Total  enrollment (DRVEF2020)', 0)
    
    # Ensure the percentage fields exist and fetch male and female enrollment percentages
    male_percentage = school.get('Percent of total enrollment that are men (DRVGR2020)', None)
    female_percentage = school.get('Percent of total enrollment that are women (DRVGR2020)', None)
    
    # Check if the percentages are valid (None or 0 means missing or invalid data)
    if male_percentage is not None and female_percentage is not None:
        # Convert percentages to actual counts based on total enrollment
        male_enrollment = int(male_percentage * total_enrollment / 100)
        female_enrollment = int(female_percentage * total_enrollment / 100)
    else:
        male_enrollment = female_enrollment = 0  # Handle missing data by setting counts to 0

    # Use geojson data to get latitude and longitude
    geojson_school = geojson_school_mapping.get(school_name)
    
    if geojson_school:
        latitude = geojson_school['properties']['LAT']
        longitude = geojson_school['properties']['LON']
        
        # Adjust the circle radius based on total enrollment
        radius = total_enrollment / 1000  # Scale radius to fit the map

        # Add a circle marker for each university with popup info
        folium.CircleMarker(
            location=[latitude, longitude],
            radius=radius,
            color='blue' if 'University of Texas' in school_name else 'green',  # Highlight specific schools
            fill=True,
            fill_opacity=0.6,
            popup=(
                f"<b>{school_name}</b><br>"
                f"Total enrollment: {total_enrollment:,}<br>"  # Add commas to large numbers
                f"Male: {male_enrollment:,}<br>"  # Male enrollment with commas
                f"Female: {female_enrollment:,}"  # Female enrollment with commas
            )
        ).add_to(texas_map)

# Save the map to an HTML file
texas_map.save('texas_big_12_enrollment_map.html')

print("Map with enrollment circles created successfully! Check 'texas_big_12_enrollment_map.html'.")
