'''
Code-based service that allows the user to specify the genre, the year, and the
number of top rated movies they want to receive and returns to them a list of
matching movies ordered by rating in descending order.
'''
from statistics import mean
import csv


def read_file(pathname: str, year: int=0):
    '''
    Reads data from a specified file and filters it by release year.

    :param pathname: str, The path to the file containing movie data.
    :param year: int, The minimum release year of movies to be included in the output. 
    Only movies released on or after this year are returned. Default is 0.
    :return: list of list, A list where each element is a list representing one movie.

    >>> read_file('films.csv', 2014)[:2]
    [['1', 'Guardians of the Galaxy', 'Action,Adventure,Sci-Fi', \
'A group of intergalactic criminals are forced to work together to stop \
a fanatical warrior from taking control of the universe.', 'James Gunn', \
'Chris Pratt, Vin Diesel, Bradley Cooper, Zoe Saldana', '2014', '121', \
'8.1', '757074', '333.13', '76.0'], \
['3', 'Split', 'Horror,Thriller', 'Three girls are kidnapped by a man with \
a diagnosed 23 distinct personalities. They must try to escape before the \
apparent emergence of a frightful new 24th.', 'M. Night Shyamalan', \
'James McAvoy, Anya Taylor-Joy, Haley Lu Richardson, Jessica Sula', '2016', '117', \
'7.3', '157606', '138.12', '62.0']]
    '''
    movies = []
    with open(pathname, mode='r', encoding='utf-8') as file:
        next(file)  # Skip the header row
        for line in file:
            row = line.strip().split(';')
            try:
                movie_year = int(row[6])  # Year is in column 7
                if movie_year >= year:
                    movies.append(row)
            except (ValueError, IndexError):
                # Skip lines with invalid year data or missing columns
                continue
    return movies


def top_n(data: list, genre: str = '', n: int = 0) -> list:
    """
    Selects and ranks the top movies based on a combined average of the movie's
    rating and actor rating.

    Args:
        data (list): A list of lists where each inner list represents a movie
        (output from `read_file`).
        genre (str): A comma-separated list of genres to filter movies by. Default
        is '' (any genre).
        n (int): The number of top movies to return. If 0, returns all movies that
        match the criteria.

    Returns:
        list of tuple: A list of tuples, each containing the movie title and averaged
        rating, sorted in descending order.

    Example:
    >>> top_n(read_file('films.csv', 2014), genre='Action', n=5)
    [('Dangal', 8.8), ('Bahubali: The Beginning', 8.3), ('Guardians of the Galaxy', 8.1), \
('Mad Max: Fury Road', 8.1), ('Star Wars: Episode VII - The Force Awakens', 8.1)]
    """
    # Prepare genre filter
    genre_list = [g.strip() for g in genre.split(',')] if genre else []

    # Create a dictionary for highest rating per actor
    actor_highest_rating = {}
    for movie in data:
        try:
            rating = float(movie[8])  # Movie rating
            # Assuming actors are listed in column 6
            actors = movie[5].split(', ')
            for actor in actors:
                if actor in actor_highest_rating:
                    actor_highest_rating[actor] = max(
                        actor_highest_rating[actor], rating)
                else:
                    actor_highest_rating[actor] = rating
        except (ValueError, IndexError):
            continue  # Skip movies with invalid or missing rating data

    # Filter and calculate actor_rating for each movie
    filtered_movies = []
    for movie in data:
        title = movie[1]
        movie_genres = movie[2].split(',')
        try:
            rating = float(movie[8])  # Movie rating
            actors = movie[5].split(', ')  # Actors column

            # Check if movie matches genre filter
            if not genre_list or any(g in movie_genres for g in genre_list):
                # Calculate actor rating as the average highest rating of each actor in the movie
                actor_ratings = [actor_highest_rating.get(
                    actor, 0) for actor in actors]
                actor_rating = mean(actor_ratings) if actor_ratings else 0

                # Calculate combined rating and store result
                combined_rating = (rating + actor_rating) / 2
                filtered_movies.append(
                    (title, rating, actor_rating, combined_rating))
        except (ValueError, IndexError):
            continue  # Skip movies with invalid or missing rating data

    # Sort movies by combined rating (descending) and then lexicographically by title
    sorted_movies = sorted(filtered_movies, key=lambda x: (-x[3], x[0]))

    # Select top n or all movies, and format output
    selected_movies = sorted_movies[:n] if n > 0 else sorted_movies
    return [(title, combined_rating) for title, _, _, combined_rating in selected_movies]


def write_file(top: list, file_name: str):
    '''
    Writes each tuple's content to a new line in a specified file. Each line
    includes the movie title and its rating, separated by a comma.

    Args:
        top (list): A list of tuples containing movie titles and their respective ratings.
        file_name (str): The name of the file where the movie data should be saved.
    
    Returns:
        None
    '''
    with open(file_name, 'w') as file:
        for title, rating in top:
            file.write(f"{title},{rating:.1f}\n")

# data = top_n(read_file('films.csv'))
# print(data)
# write_file(data, 'out.txt')

if __name__ == '__main__':
    import doctest
    print(doctest.testmod())
