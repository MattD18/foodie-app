from fuzzywuzzy import process

from .models import Place

class QueryParser():


    def __init__(self) -> None:
        self.query_trigger = 'rec me'

    def classify_intent(self, user_query: str) -> str:
        if user_query.lower().startswith(self.query_trigger):
            return 'RECOMMENDATION'
        else:
            return 'FALLBACK'
        
    def extract_place(self, user_query: str, match_threshold:int=80) -> str:
        # extract place string
        place_str = user_query.lower() \
            .replace(self.query_trigger, "") \
            .strip()
        
        # extract set of place from db
        place_dict = {p.name.lower():p.id for p in Place.objects.all()}

        # find closest matching string and return place_id
        match_candidates = process.extract(place_str, place_dict.keys(), limit=1)
        match_key = match_candidates[0][0]
        match_score = match_candidates[0][1]
        if match_score < match_threshold:
            place_id = None
        else:
            place_id = place_dict.get(match_key)

        return place_id
