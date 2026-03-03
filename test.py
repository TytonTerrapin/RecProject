from recommender import HybridRecommender

rec = HybridRecommender()

results = rec.recommend_by_title("Scream 7", top_n=10)

for r in results:
    print(r)