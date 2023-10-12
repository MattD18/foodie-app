import numpy as np
import pandas as pd

from .models import Restaurant, RestaurantFeatures


class RecEngine():

    def __init__(self) -> None:
        pass

    def get_recommendation(self, query):
        candidate_set = self.retrieval_pass(query)
        ranked_set = self.ranking_pass(candidate_set, query)
        rec = self.business_logic_pass(ranked_set, query)
        return rec

    def retrieval_pass(self, query, retrieval_cap=100):
        rec_set = [r.id for r in Restaurant.objects.all()]
        rec_set = np.random.choice(rec_set, retrieval_cap).tolist()
        print(len(rec_set))
        return rec_set

    def ranking_pass(self, rec_set, query):
        ranked_rec_set = []
        for rec in rec_set:
            ranking_quality_score = RestaurantFeatures.objects.get(restaurant=rec).ranking_quality_score
            ranked_rec_set.append({
                'id':rec,
                'ranking_qualty_score':ranking_quality_score
            })
        ranked_rec_set = pd.DataFrame(ranked_rec_set).sort_values(by='ranking_qualty_score', ascending=False)
        ranked_rec_set = ranked_rec_set[ranked_rec_set['ranking_qualty_score'] != 5.0]
        print(ranked_rec_set.head(1), ranked_rec_set.tail(1))
        ranked_rec_set = ranked_rec_set['id'].to_list()
        return ranked_rec_set

    def business_logic_pass(self, rec_set, query):
        rec = rec_set[0]
        print(rec)
        return rec