"""
Test script to verify the Movie Recommender System is working correctly.
This script tests all API endpoints and the data loading pipeline.
"""

import requests
import json
import time
import sys


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_result(success=True, message=""):
    """Print a test result."""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"{status}: {message}")


def test_api_health():
    """Test API health endpoint."""
    print_header("Testing API Health")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"API is healthy - {data.get('message')}")
            return True
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_result(False, "Could not connect to API on http://127.0.0.1:8000")
        print("   Make sure to start the API with: python -m uvicorn api:app --reload")
        return False
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_popular_movies():
    """Test getting popular movies."""
    print_header("Testing Popular Movies Endpoint")
    try:
        response = requests.get("http://127.0.0.1:8000/api/movies/popular?limit=5")
        if response.status_code == 200:
            movies = response.json()
            print_result(True, f"Retrieved {len(movies)} popular movies")
            
            if movies:
                print("\nFirst 3 movies:")
                for i, movie in enumerate(movies[:3]):
                    print(f"  {i+1}. {movie['title']} (Rating: {movie['vote_average']}/10)")
            
            return True, movies
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False, None
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False, None


def test_search_movies():
    """Test searching for movies."""
    print_header("Testing Movie Search Endpoint")
    try:
        response = requests.get("http://127.0.0.1:8000/api/movies/search?q=avatar&limit=5")
        if response.status_code == 200:
            movies = response.json()
            print_result(True, f"Found {len(movies)} movies matching 'avatar'")
            
            if movies:
                print("\nSearch results:")
                for i, movie in enumerate(movies[:3]):
                    print(f"  {i+1}. {movie['title']} (ID: {movie['movie_id']})")
            
            return True, movies
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False, None
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False, None


def test_movie_details(movie_id):
    """Test getting movie details."""
    print_header(f"Testing Movie Details Endpoint (ID: {movie_id})")
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/movies/{movie_id}")
        if response.status_code == 200:
            movie = response.json()
            print_result(True, f"Retrieved details for: {movie['title']}")
            
            print(f"\nMovie Information:")
            print(f"  Title: {movie['title']}")
            print(f"  Rating: {movie['vote_average']}/10")
            print(f"  Year: {movie['release_year']}")
            print(f"  Director: {movie['director']}")
            print(f"  Genres: {', '.join(movie['genres'][:3])}")
            print(f"  Cast: {', '.join(movie['cast'][:3])}")
            print(f"  Overview: {movie['overview'][:100]}...")
            
            return True, movie
        elif response.status_code == 404:
            print_result(False, f"Movie with ID {movie_id} not found")
            return False, None
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False, None
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False, None


def test_recommendations(movie_id):
    """Test getting recommendations."""
    print_header(f"Testing Recommendations Endpoint (ID: {movie_id})")
    try:
        response = requests.get(f"http://127.0.0.1:8000/api/recommendations/{movie_id}?top_n=5")
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            movie_title = data.get("title", "Unknown")
            
            print_result(True, f"Retrieved {len(recommendations)} recommendations for '{movie_title}'")
            
            if recommendations:
                print("\nRecommended movies:")
                for i, rec in enumerate(recommendations):
                    print(f"  {i+1}. {rec['title']} (Score: {rec['score']:.4f})")
            
            return True, recommendations
        elif response.status_code == 404:
            print_result(False, f"Movie with ID {movie_id} not found")
            return False, None
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False, None
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False, None


def test_recommendation_by_title():
    """Test getting recommendations by movie title."""
    print_header("Testing Recommendations by Title Endpoint")
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/recommendations/by-title",
            params={"title": "Avatar", "top_n": 5}
        )
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get("recommendations", [])
            movie_title = data.get("title", "Unknown")
            
            print_result(True, f"Retrieved {len(recommendations)} recommendations for '{movie_title}'")
            
            if recommendations:
                print("\nTop recommendations:")
                for i, rec in enumerate(recommendations[:3]):
                    print(f"  {i+1}. {rec['title']} (Score: {rec['score']:.4f})")
            
            return True
        elif response.status_code == 404:
            print_result(False, "Movie title not found")
            return False
        else:
            print_result(False, f"API returned status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_api_documentation():
    """Test API documentation endpoints."""
    print_header("Testing API Documentation")
    try:
        response = requests.get("http://127.0.0.1:8000/docs")
        if response.status_code == 200:
            print_result(True, "Interactive API docs available at http://127.0.0.1:8000/docs")
            return True
        else:
            print_result(False, f"API docs returned status {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║  Movie Recommender System - API Test Suite".ljust(59) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: API Health
    if test_api_health():
        passed_tests += 1
        total_tests += 1
    else:
        print("\n" + "!"*60)
        print("  API is not running!")
        print("  Please start it with: python -m uvicorn api:app --reload")
        print("!"*60)
        return
    
    # Small delay to ensure API is ready
    time.sleep(1)
    
    # Test 2: Popular movies
    success, popular_movies = test_popular_movies()
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Test 3: Search movies
    success, search_movies_list = test_search_movies()
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Get a movie ID for further tests
    movie_id = None
    if popular_movies:
        movie_id = popular_movies[0]["movie_id"]
    elif search_movies_list:
        movie_id = search_movies_list[0]["movie_id"]
    
    if movie_id:
        # Test 4: Movie details
        success, movie_data = test_movie_details(movie_id)
        total_tests += 1
        if success:
            passed_tests += 1
        
        # Test 5: Recommendations
        success, _ = test_recommendations(movie_id)
        total_tests += 1
        if success:
            passed_tests += 1
    
    # Test 6: Recommendations by title
    success = test_recommendation_by_title()
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Test 7: API Documentation
    success = test_api_documentation()
    total_tests += 1
    if success:
        passed_tests += 1
    
    # Summary
    print_header("Test Summary")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n✓ All tests passed! Your API is working correctly.")
        print("\nNext steps:")
        print("  1. Start the Streamlit frontend: streamlit run app.py")
        print("  2. Open http://localhost:8501 in your browser")
        print("  3. Explore movies and get recommendations!")
    else:
        print(f"\n✗ {total_tests - passed_tests} test(s) failed. Check the output above.")
    
    print("\nAPIs available at:")
    print("  - Frontend: http://localhost:8501")
    print("  - API Docs: http://127.0.0.1:8000/docs")
    print("  - API Server: http://127.0.0.1:8000")
    print()


if __name__ == "__main__":
    main()
