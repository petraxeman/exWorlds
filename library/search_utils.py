def make_ngram(query: str, sn: int = 3, mn: int = 4) -> str:
    """
    Convert text to serie of ngrams
    query: string - Text what convert
    sn: integer - Start N
    mn: integer - Max N
    Return: string - ngrams in string divded by space
    """
    words = query.strip().split(" ")
    ngrams = []
    for length in range(sn, mn + 1):
        for word in words:
            word = word.lower()
            for i in range(length, len(word) + 1):
                ngrams.append(word[i-length:i])
    return ngrams


def make_search_pipeline(query: str, field: str = "$search-field") -> list[dict]:
    return [{"$addFields": {"text-score": {"$size": {"$setUnion": {"$setIntersection": [field, make_ngram(query)]}}}}}]