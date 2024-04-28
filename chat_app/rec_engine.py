import re

import numpy as np
import pandas as pd

from . import models


class RecEngine():

    def __init__(self, db) -> None:
        self.db = db

    def get_recommendation(self, query_parameters:dict):
        candidate_set = self.retrieval_pass(query_parameters)
        ranked_set = self.ranking_pass(candidate_set, query_parameters)
        rec = self.business_logic_pass(ranked_set, query_parameters)
        return rec

    def retrieval_pass(self, query_parameters, retrieval_cap:int=10):
        rec_set = []
        place_id = query_parameters.get('place_id')

        place = self.db.query(models.Place).filter(models.Place.id == place_id).first()
        if place:
            rec_set = place.restaurants

        if rec_set:
            rec_set = np.random.choice(rec_set, retrieval_cap).tolist()
        return rec_set

    #TODO: revamp for database migration
    def ranking_pass(self, rec_set, query_parameter, ranking_cap:int=5):
        ranked_rec_set = []

        def top_k_keys(d, k):
            return sorted(d, key=lambda k: d[k], reverse=True)[:k]
        
        if rec_set:
            score_dict = {r.id:r.ranking_quality_score for r in rec_set if r.ranking_quality_score is not None}
            ranked_rec_set = top_k_keys(score_dict, k=ranking_cap)
        else: 
            ranked_rec_set = rec_set
        return ranked_rec_set

    def business_logic_pass(self, ranked_rec_set, query_parameters):
        if ranked_rec_set: 
            rec = int(np.random.choice(ranked_rec_set))
            query_status = 'FOUND'
        else:
            rec = None
            query_status = 'NOT_FOUND'
        return rec, query_status