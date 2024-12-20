import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import openrouteservice

client = openrouteservice.Client(key="5b3ce3597851110001cf624860a05a1e58ba4ea2987933a00876a5d1")


# Load CSV
def load_csv():
    return pd.read_csv("tagaytayplaces.csv")


# Function to save user preferences to a CSV
def save_user_preferences(user_id, cuisine_type, price_range):
# Load existing CSV file
    try:
        df = pd.read_csv('user_preferences.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['user_id', 'cuisine_type', 'price_range'])

# Add the new user's preferences
    new_user = pd.DataFrame([[user_id, cuisine_type, price_range]], columns=['user_id', 'cuisine_type', 'price_range'])

# Append to the CSV and save it
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv('user_preferences.csv', index=False)


# Function for Recommendation Page
def recommendation_page(food_map):
# Title and description
    st.title("TagaytayBite: A food place recommendation app")
    st.write("Here are food places in Tagaytay based on the cuisine type and price range.")

# Load the CSV
    data = load_csv()

# Check if the necessary columns exist in the CSV
    if 'lat' in data.columns and 'lon' in data.columns and 'cuisine' in data.columns and 'price' in data.columns \
            and 'address' in data.columns and 'contact' in data.columns:

# User input for user_id
        user_id = st.text_input("Enter your User ID:")

# Cuisine filter input
        cuisine_type = st.text_input("Enter cuisine type to filter ", "")

# Price range filter input
        price_range = st.selectbox("Select price range", ["All", "Low", "Medium", "High"])

# Save preferences to session state
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.cuisine_type = cuisine_type
            st.session_state.price_range = price_range
            # Save preferences to CSV file
            save_user_preferences(user_id, cuisine_type, price_range)

 # Filter the data based on the cuisine type entered
        if cuisine_type:
            filtered_data = data[data['cuisine'].str.contains(cuisine_type, case=False, na=False)]
            st.write(f"There are {len(filtered_data)} food places that match the cuisine type '{cuisine_type}'")
        else:
            filtered_data = data
            st.write("Showing all food places.")

# Filter based on price range
        if price_range != "All":
            filtered_data = filtered_data[filtered_data['price'].str.contains(price_range, case=False, na=False)]
            st.write(f"There are {len(filtered_data)} food places that match the price range '{price_range}'")

 # Shuffle data between button presses
        if 'shuffled_data' not in st.session_state:
            st.session_state.shuffled_data = filtered_data.sample(frac=1).reset_index(drop=True)

# Button to generate a new set of recommendations
        if st.button("Show Another Set of Recommendations"):
            # Shuffle the filtered data again
            st.session_state.shuffled_data = filtered_data.sample(frac=1).reset_index(drop=True)

# Get top 5 restaurants from the shuffled data
        top_5_restaurants = st.session_state.shuffled_data.head(5)

        foodplace = [food for food in top_5_restaurants["name"]]
        options_map = {row[6]: row[1:] for row in top_5_restaurants.to_numpy()}


        selection = st.segmented_control(
            "Restaurants",
            options=list(options_map.keys()),
            format_func=lambda option: f"{option}",
            selection_mode="single",
        )

        if selection is None:
            selection = foodplace[0]
            placeName = foodplace[0]
            placeCoords = [options_map[foodplace[0]][7], options_map[foodplace[0]][8]]
        else:
            placeName = selection
            placeCoords = [options_map[selection][7], options_map[selection][8]]

# Loop through the selected data
        for index, row in top_5_restaurants.iterrows():
            name = row.get('name', 'Unnamed Food Place')
            restaurant_lat = row['lat']
            restaurant_lon = row['lon']
            cuisine = row.get('cuisine', 'Unknown Cuisine')
            price = row.get('price', 'Unknown Price')
            address = row.get('address', 'Unknown Address')
            contact = row.get('contact', 'Unknown Contact')

# Create a popup with restaurant details
            popup_text = f"{name}<br>Cuisine: {cuisine}<br>Price Range: {price}<br>Address: {address}<br>Contact: {contact}<br>Location: ({restaurant_lat}, {restaurant_lon})"

# Add a marker for each restaurant
            folium.Marker([restaurant_lat, restaurant_lon], popup=popup_text).add_to(food_map)

        selpopup_text =  f"{options_map[selection][5]}<br>Cuisine: {options_map[selection][12]}<br>Price Range: {options_map[selection][13]}<br>Address: {options_map[selection][11]}<br>Contact: {options_map[selection][14]}<br>Location: ({placeCoords[0]}, {placeCoords[1]})"
#default start
        plot(food_map, [14.1153, 120.9620], [options_map[selection][8], options_map[selection][7]], selpopup_text)

        
    else:
        st.error("Preferences Unavailable.")

def plot(food_map, start_coords, end_coords, popup_text):
    route = client.directions(
        coordinates=[list(reversed(start_coords)), list(reversed(end_coords))],
        profile='driving-car', #attribute for cars, can change ..
        format='geojson'
    )
    folium.PolyLine(
        locations=[list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']],
        color='green',
        weight=5,
        opacity=0.8
    ).add_to(food_map)

    folium.Marker(
        location=start_coords,
        popup="Start: Tagaytay",
        icon=folium.Icon(color="green", icon='white', prefix='fa')
    ).add_to(food_map)

    folium.Marker(
        location=end_coords,
        popup=popup_text,
        icon=folium.Icon(color="red", icon='white', prefix='fa')
    ).add_to(food_map)

def merge_sort(data, key):
# Base case: A list with one or zero elements is already sorted
    if len(data) <= 1:
        return data

# Divide the data into two halves
    mid = len(data) // 2
    left_half = merge_sort(data[:mid], key)
    right_half = merge_sort(data[mid:], key)

# Combine: Merge the sorted halves
    return merge(left_half, right_half, key)

def merge(left, right, key):
    sorted_list = []
    i, j = 0, 0

# Merge the two halves in sorted order
    while i < len(left) and j < len(right):
        if left[i][key].lower() <= right[j][key].lower():
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    # Append any remaining elements
    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])

    return sorted_list


# Updated content-based filtering page
def content_based_filtering_page():
    st.title("Content-Based Food Place Recommendation")
    st.write("Here are some food place suggestions based on your preferences:")

    # Load the CSV data
    data = load_csv()

# Check if preferences exist in session state
    if 'cuisine_type' in st.session_state and 'price_range' in st.session_state:
        cuisine_type = st.session_state.cuisine_type
        price_range = st.session_state.price_range

        st.write(f"Your preferences: Cuisine - {cuisine_type}, Price Range - {price_range}")

# Filter the data based on user's previous preferences
        filtered_data = data
        if cuisine_type:
            filtered_data = filtered_data[filtered_data['cuisine'].str.contains(cuisine_type, case=False, na=False)]
        if price_range != "All":
            filtered_data = filtered_data[filtered_data['price'].str.contains(price_range, case=False, na=False)]

# Check if there are any matching food places
        if len(filtered_data) > 0:
            # Convert filtered data to a list of dictionaries
            filtered_list = filtered_data.to_dict('records')

# Sort the filtered data alphabetically by 'name' using Merge Sort
            sorted_data = merge_sort(filtered_list, key='name')

# Show the sorted recommendations
            st.write("Here are the food places matching your preferences (sorted alphabetically):")

            for row in sorted_data:
                st.write(f"- **{row['name']}**")
                st.write(f"  - Cuisine: {row['cuisine']}")
                st.write(f"  - Price Range: {row['price']}")
                st.write(f"  - Location: ({row['lat']}, {row['lon']})")

 # Display the map with the restaurant's location
                food_map = folium.Map(location=[row['lat'], row['lon']], zoom_start=14)
                folium.Marker([row['lat'], row['lon']], popup=row['name']).add_to(food_map)
                st_folium(food_map, width=700, height=500)

        else:
            st.write("No food places match your preferences. Try broadening your search.")
    else:
        st.write("No preferences saved. Please visit the first page to set your preferences.")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page", ["Recommendation Page", "Content-Based Filtering Page"])

# Create a map to pass to the plot function
    lat = 14.109088  # Tagaytay latitude
    lon = 120.955384  # Tagaytay longitude
    food_map = folium.Map(
        location=[lat, lon],
        zoom_start=13
        )

    if page == "Recommendation Page":
        recommendation_page(food_map)
    elif page == "Content-Based Filtering Page":
        content_based_filtering_page()


# Display the map
    st.write("Route Map:")
    st_folium(food_map, width=700, height=500)


if __name__ == "__main__":
    main()

