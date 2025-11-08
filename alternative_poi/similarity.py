from similarity import SimilarPOIFinder

if __name__ == "__main__":
    import json
    regional_pois = [
        {"name":"Königssee","lat":47.5551,"lon":12.9766,"category":"lake","tags":{"boundary":"protected_area"},"desc":"A lake, within a protected national park, surrounded by towering mountains, renowned for its clear, emerald-toned waters, with a long, fjord-like basin. Forest-lined slopes create a serene atmosphere."},
        {"name":"Chiemsee","lat":47.8811,"lon":12.4744,"category":"lake","tags":{},"desc":"A lake with clear waters and forested slopes, creating a calm alpine setting."},
        {"name":"Walchensee","lat":47.5933,"lon":11.3056,"category":"lake","tags":{},"desc":"A deep alpine lake with turquoise water and wooded shores, set among steep Bavarian peaks."},
        {"name":"Tegernsee","lat":47.7120,"lon":11.7587,"category":"lake","tags":{},"desc":"An alpine lake with clear waters, ringed by forested hills and small villages; calm and scenic."},
    ]
    user_center = (47.63, 13.00)
    video_pois = [
        {"name":"Königssee","lat":47.5551,"lon":12.9766,"category":"lake","tags":{"boundary":"protected_area"},"desc":"A lake, within a protected national park, surrounded by towering mountains, renowned for its clear, emerald-toned waters, with a long, fjord-like basin. Forest-lined slopes create a serene atmosphere."},
    ]
    finder = SimilarPOIFinder(alpha=0.7, radius_km=200)
    finder.build_index(regional_pois, user_center=user_center)
    res = finder.find_for_video_pois(video_pois, topk_each=5)
    print(json.dumps(res, indent=2))

from similarity import SimilarPOIFinder

if __name__ == "__main__":
    import json
    regional_pois = [
        {"name":"Königssee","lat":47.5551,"lon":12.9766,"category":"lake","tags":{"boundary":"protected_area"},"desc":"A lake, within a protected national park, surrounded by towering mountains, renowned for its clear, emerald-toned waters, with a long, fjord-like basin. Forest-lined slopes create a serene atmosphere."},
        {"name":"Chiemsee","lat":47.8811,"lon":12.4744,"category":"lake","tags":{},"desc":"A lake with clear waters and forested slopes, creating a calm alpine setting."},
        {"name":"Walchensee","lat":47.5933,"lon":11.3056,"category":"lake","tags":{},"desc":"A deep alpine lake with turquoise water and wooded shores, set among steep Bavarian peaks."},
        {"name":"Tegernsee","lat":47.7120,"lon":11.7587,"category":"lake","tags":{},"desc":"An alpine lake with clear waters, ringed by forested hills and small villages; calm and scenic."},
    ]
    user_center = (47.63, 13.00)
    video_pois = [
        {"name":"Königssee","lat":47.5551,"lon":12.9766,"category":"lake","tags":{"boundary":"protected_area"},"desc":"A lake, within a protected national park, surrounded by towering mountains, renowned for its clear, emerald-toned waters, with a long, fjord-like basin. Forest-lined slopes create a serene atmosphere."},
    ]
    finder = SimilarPOIFinder(alpha=0.7, radius_km=200)
    finder.build_index(regional_pois, user_center=user_center)
    res = finder.find_for_video_pois(video_pois, topk_each=5)
    print(json.dumps(res, indent=2))