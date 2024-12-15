#
# Job: This file holds all the prompts for each different type of call we have to the AI APIs
#
def create_must_see_attractions_prompt(destination):
    """
    Generate an OpenAI prompt to create 5 must-see attractions for the given destination.

    :param destination: The destination for which must-see attractions are generated.
    :return: A string OpenAI prompt to generate the attractions.
    """

    prompt = f"""
    You are a travel expert. Generate a list of 5 must-see attractions for travelers visiting {destination}.
    Each attraction should have:
    1. The name of the attraction (place_name).
    2. A brief description (description) of why it's iconic or famous.
    3. A highlight of its most notable features (features).
    Format the output as follows:
    
    ('Place Name 1', 'Brief description of the attraction', 'Key features or highlights of the place'),
    ('Place Name 2', 'Brief description of the attraction', 'Key features or highlights of the place'),
        ...
    
    Ensure that the output follows Python syntax strictly, with all strings enclosed in double quotes (`"`), and no special characters (e.g., single quotes, backslashes) causing invalid syntax. And no next-line character after the last tuple. 
    """
    return prompt


def create_image_prompts(mustSeeAttractions, fromDate, toDate):
    """
    Generate image prompts for a list of must-see attractions during the given travel dates.

    :param mustSeeAttractions: List of tuples containing (place_name, description, features).
    :param fromDate: Start date of the trip (YYYY-MM-DD).
    :param toDate: End date of the trip (YYYY-MM-DD).
    :return: List of image prompts as strings.
    """

    prompts = []
    for attraction in mustSeeAttractions:
        attraction_name, description, features = attraction
        prompt = (
            f"An ultra-realistic photograph of {attraction_name}, taken during a trip from {fromDate} to {toDate}. "
            f"The scene highlights {description}, surrounded by its natural or urban environment. "
            f"The lighting is balanced and natural, showcasing intricate details of {features}. "
            f"The perspective is carefully chosen to emphasize the grandeur and charm of the location, "
            f"captured with a high-quality, true-to-life photographic style."
        )
        prompts.append(prompt)
    
    return prompts


def create_weather_and_packing_list_prompt(destination, description, from_date, to_date):
    """
    Generate an OpenAI prompt to create a list of must-see attractions for the given destination,
    and also provide expected weather conditions, average temperatures for those dates, and a recommended packing list.

    :param destination: Location of travel.
    :param description: Description related to the trip.
    :param fromDate: Start date of the trip (YYYY-MM-DD).
    :param toDate: End date of the trip (YYYY-MM-DD).
    """

    prompt = f"""
    You are a travel expert. For travelers visiting {destination} from {from_date} to {to_date} wanting to have a trip with the following description: {description}, 
    do the following:

    1. Based on historical weather data for {destination} during this time of year, 
    provide an expected weather outlook. Describe the general weather conditions 
    (e.g., mostly sunny, occasional rain), and include approximate average high and low temperatures 
    in Celsius.

    2. Based on the expected weather, generate a comprehensive packing list that would be suitable 
    for someone visiting during this period. Include items that are both weather-appropriate and 
    generally useful for exploring the attractions.


    The expected format is:
    ('conditions', 'Sunny with clear skies'),('average_high', '25C'),('average_low', '15C'),('Item 1', 'Heavy Coat'),('Item 2', 'Boots'),('Item 3', 'Sunglasses'),('Item 4', 'Sunscreen'),('Item 5', 'Hat'),('Item 6', 'Reusable Water Bottle')

    Ensure that the output follows Python syntax strictly, with all strings enclosed in double quotes (`"`), and no special characters (e.g., single quotes, backslashes) causing invalid syntax. And no next-line character after each tuple. 
    """

    return prompt


def create_itinerary_pdf_prompt(selected_attractions, weather_info, packing_list, travel_dates):
    """
    Generate a detailed OpenAI prompt for creating a PDF-friendly plain-text full itinerary.
    """

    # Format selected attractions into a readable list
    attractions_str = "\n".join([
        f"- {attr['title']}: {attr['description']}"
        for attr in selected_attractions
    ])

    # Format weather information
    weather_str = (
        f"Weather during your trip:\n"
        f"- Condition: {weather_info.get('condition', 'Unknown')}\n"
        f"- Average High: {weather_info.get('average_high', 'N/A')}°C\n"
        f"- Average Low: {weather_info.get('average_low', 'N/A')}°C\n"
    )

    # Format packing list
    packing_str = "\n".join([f"- {item}" for item in packing_list])

    # Build the prompt
    prompt = f"""
    You are a travel planner. Using the details provided below, create a well-structured, plain-text travel itinerary.

    Travel Dates: {travel_dates}

    Selected Attractions:
    {attractions_str}

    {weather_str}

    Packing List:
    {packing_str}

    The output should:
    1. Provide a daily itinerary, allocating attractions to specific days.
    2. Suggest the best times to visit attractions (e.g., morning, afternoon, evening).
    3. Include practical advice for travelers, such as weather considerations and packing tips.
    4. End with a section titled "Travel Tips" that summarizes key recommendations.

    Format the response in plain text with clear headings (e.g., "Day 1", "Weather Summary") and readable structure, but do not use Markdown, HTML, or any special formatting. Keep it simple and professional.
    """
    return prompt
