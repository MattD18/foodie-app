import re

import numpy as np
import pandas as pd

from .models import Restaurant, RestaurantFeatures, Neighborhood


class RecEngine():

    def __init__(self) -> None:
        pass

    def get_recommendation(self, query):
        query_parameters = self.entity_resolution(query)
        candidate_set = self.retrieval_pass(query_parameters)
        ranked_set = self.ranking_pass(candidate_set, query_parameters)
        rec = self.business_logic_pass(ranked_set, query_parameters)
        return rec

    def retrieval_pass(self, query_parameters, retrieval_cap=100):
        neighborhood = query_parameters.get('neighborhood')
        # filter on neighborhood query if applicable
        if neighborhood:
            n = Neighborhood.objects.get(name=neighborhood)
            if n:
                rec_set = [r.restaurant.id for r in RestaurantFeatures.objects.filter(neighborhood=n)]
            else: 
                rec_set = []
        else:
            rec_set = [r.id for r in Restaurant.objects.all()]
        if rec_set:
            rec_set = np.random.choice(rec_set, retrieval_cap).tolist()
        print(len(rec_set))
        return rec_set

    def ranking_pass(self, rec_set, query_parameters):
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

    def business_logic_pass(self, rec_set, query_parameters):
        if rec_set:
            rec = rec_set[0]
            print(rec)
        else:
            rec = None
        return rec

    def entity_resolution(self, query):
        # Define a regular expression pattern
        pattern = r'Rec me\s+(\w+(?:\s+\w+)*)'
        # Use re.search to find the match
        match = re.search(pattern, query)
        # Check if a match is found and print the result
        if match:
            neighborhood = match.group(1)
            print(neighborhood)
        else:
            neighborhood = None
            print("No match found")
        query_parameters = {
            'neighborhood': neighborhood
        }
        return query_parameters
