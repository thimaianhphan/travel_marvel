export type AlternativePoi = {
  name: string;
  lat: number;
  lon: number;
  poi_type: string;
  source: string;
  score: number | null;
  tags: Record<string, unknown>;
};

export type AlternativeRoute = {
  destination: AlternativePoi;
  scenic_waypoints: AlternativePoi[];
  score: number | null;
  route_path: [number, number][];
};

export type AlternativesResponse = {
  video_url: string;
  target_name: string;
  alternatives: AlternativeRoute[];
};

export type AlternativesRequestPayload = {
  user_lat: number;
  user_lon: number;
  max_alternatives?: number;
  search_radius_km?: number;
  video_url?: string;
  manual_places?: string[];
};

