from .models import Place

class QueryParser():


    def __init__(self) -> None:
        self.query_trigger = 'rec me'

    def classify_intent(self, user_query: str) -> str:
        if user_query.lower().startswith(self.query_trigger):
            return 'RECOMMENDATION'
        else:
            return 'FALLBACK'
        
    def extract_place(self, user_query: str) -> str:
        # extract place string
        place_str = user_query.lower() \
            .replace(self.query_trigger, "") \
            .strip()
        
        # extract set of place from db
        place_set = Place.objects.all()

        # iterate through places to find a match
        for p in place_set:
            if p.name.lower() in place_str:
                return p
        return None




if __name__ == "__main__":
    print('hi')