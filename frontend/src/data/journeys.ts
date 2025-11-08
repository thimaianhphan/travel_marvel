export type JourneySegment = {
  from: string;
  to: string;
  distanceKm: number;
  mode: "rail" | "bike" | "hike";
  narrative: string;
};

export type PointOfInterest = {
  name: string;
  description: string;
  category: "nature" | "culture" | "food" | "history" | "viewpoint";
  municipality: string;
  coordinates: [number, number];
};

export type JourneyDestination = {
  name: string;
  summary: string;
  coordinates: [number, number];
  travelTip: string;
};

export type Journey = {
  slug: string;
  title: string;
  summary: string;
  heroTagline: string;
  heroImageAlt: string;
  videoUrl: string;
  videoTitle: string;
  userHomeBase: string;
  homeBaseCoordinates: [number, number];
  season: "spring" | "summer" | "autumn" | "winter";
  durationDays: number;
  distanceKm: number;
  carbonSavedKg: number;
  destinations: JourneyDestination[];
  featuredPoi: PointOfInterest[];
  segments: JourneySegment[];
  sustainabilityNotes: string;
  mapPath: [number, number][];
};

export const journeys: Journey[] = [
  {
    slug: "black-forest-loop",
    title: "Black Forest Slow Adventure",
    summary:
      "Swap influencer hotspots for a 3-day Baden-Württemberg loop along forest rail lines, village bakeries, and lakeside paths.",
    heroTagline: "Viral Schwarzwald views, local slow travel pace.",
    heroImageAlt: "Sunlight hitting a trail through dense Black Forest pines.",
    videoUrl: "https://www.youtube.com/watch?v=dummy-black-forest",
    videoTitle: "Top 10 Black Forest Destinations - Viral Travel Guide",
    userHomeBase: "Stuttgart, Baden-Württemberg",
    homeBaseCoordinates: [48.783, 9.181],
    season: "summer",
    durationDays: 3,
    distanceKm: 126,
    carbonSavedKg: 38,
    destinations: [
      {
        name: "Triberg Waterfalls",
        summary:
          "Famous cascades surrounded by spruce forest, reached via a vintage rail line.",
        coordinates: [48.1296, 8.2335],
        travelTip:
          "Arrive early to walk the quieter upper trail before tour buses.",
      },
      {
        name: "Lake Titisee",
        summary:
          "Glacial lake with paddleboards and cafés; ideal midday pause for seasonal Schwarzwälder Kirschtorte.",
        coordinates: [47.902, 8.1562],
        travelTip:
          "Rent a solar boat for a quieter loop and zero-emission cruising.",
      },
    ],
    featuredPoi: [
      {
        name: "Donauquelle Walking Loop",
        description:
          "Short interpretive trail tracing the emerging Danube springs, with kid-friendly signage and refill points.",
        category: "nature",
        municipality: "Donaueschingen",
        coordinates: [47.9548, 8.4978],
      },
      {
        name: "Haus der 1000 Uhren",
        description:
          "Community-run museum celebrating local clockmaking heritage with repair workshops on most weekends.",
        category: "history",
        municipality: "Triberg im Schwarzwald",
        coordinates: [48.1297, 8.2315],
      },
      {
        name: "Hinterzarten Farmers' Market",
        description:
          "Friday morning market highlighting regenerative Black Forest producers and seasonal picnic staples.",
        category: "food",
        municipality: "Hinterzarten",
        coordinates: [47.905, 8.1044],
      },
    ],
    segments: [
      {
        from: "Stuttgart Hbf",
        to: "Donaueschingen",
        distanceKm: 113,
        mode: "rail",
        narrative:
          "Regional-Express via Rottweil with ample bike storage; grab coffee at the zero-waste kiosk on platform 12.",
      },
      {
        from: "Donaueschingen",
        to: "Triberg im Schwarzwald",
        distanceKm: 35,
        mode: "bike",
        narrative:
          "Panoramic Breg Valley cycle path with optional detours to sculpture trail viewpoints.",
      },
      {
        from: "Triberg",
        to: "Titisee",
        distanceKm: 45,
        mode: "rail",
        narrative:
          "Höllentalbahn climb featuring glass-roof carriages—watch for ravines carved during the last ice age.",
      },
      {
        from: "Titisee",
        to: "Stuttgart Hbf",
        distanceKm: 162,
        mode: "rail",
        narrative:
          "Evening IRE connection via Freiburg; reserve the bike spot at least 24h ahead during summer weekends.",
      },
    ],
    sustainabilityNotes:
      "Keeps spend within village-owned cafés and encourages rail + pedal access instead of rental cars.",
    mapPath: [
      [48.783, 9.181],
      [47.9548, 8.4978],
      [48.1297, 8.2315],
      [47.902, 8.1562],
      [47.905, 8.1044],
      [48.783, 9.181],
    ],
  },
  {
    slug: "swabian-alb-escape",
    title: "Swabian Alb Ridge Escape",
    summary:
      "Two days chasing castle panoramas and slow-food stops along the Albtrauf ridge, inspired by viral drone footage.",
    heroTagline: "Dramatic ridgelines without the tourist crush.",
    heroImageAlt:
      "A limestone ridge with Hohenzollern Castle in the distance at golden hour.",
    videoUrl: "https://www.youtube.com/watch?v=dummy-schwabian-alb",
    videoTitle: "Germany's Fairytale Castles from Above",
    userHomeBase: "Tübingen, Baden-Württemberg",
    homeBaseCoordinates: [48.5216, 9.0576],
    season: "autumn",
    durationDays: 2,
    distanceKm: 78,
    carbonSavedKg: 21,
    destinations: [
      {
        name: "Hohenzollern Castle Plateau",
        summary:
          "Iconic hilltop palace with sunrise views across the Alb; swap the shuttle bus for the beech forest climb.",
        coordinates: [48.3259, 8.9637],
        travelTip:
          "Pack a thermos for the ridge picnic tables just south of the castle entrance.",
      },
      {
        name: "Bad Urach Waterfalls",
        summary:
          "Mossy cascade with misty gorge trail; popular in clips, but this route loops via lesser-known orchards.",
        coordinates: [48.4916, 9.3938],
        travelTip:
          "Visit midweek to combine with the geothermal spa before locals arrive after work.",
      },
    ],
    featuredPoi: [
      {
        name: "Burg Derneck Youth Hostel Terrace",
        description:
          "Community-run castle hostel with sunset terrace overlooking Lauter Valley limestone cliffs.",
        category: "viewpoint",
        municipality: "Hayingen",
        coordinates: [48.2736, 9.4714],
      },
      {
        name: "Alb Gold Pasta Trail Café",
        description:
          "Slow-food café right on the cycling trail known for regional spelt dishes and refillable water stations.",
        category: "food",
        municipality: "Trochtelfingen",
        coordinates: [48.3308, 9.2243],
      },
      {
        name: "Freeman Walk Beuron",
        description:
          "Meditative 4 km forest walk curated by local rangers with QR-triggered audio stories about rewilding.",
        category: "culture",
        municipality: "Beuron",
        coordinates: [48.0923, 8.9654],
      },
    ],
    segments: [
      {
        from: "Tübingen",
        to: "Hechingen",
        distanceKm: 31,
        mode: "rail",
        narrative:
          "20-minute RB86 ride; borrow the RegioRad bike right outside the station for the castle ascent.",
      },
      {
        from: "Hechingen",
        to: "Alb Gold Teich",
        distanceKm: 26,
        mode: "bike",
        narrative:
          "Albtrauf Panorama Cycle Route, weaving past orchards and community wind turbines.",
      },
      {
        from: "Alb Gold Teich",
        to: "Bad Urach",
        distanceKm: 18,
        mode: "hike",
        narrative:
          "Ridge-top hiking path lined with juniper heaths; stop at the Schäfermuseum for shepherding stories.",
      },
      {
        from: "Bad Urach",
        to: "Tübingen",
        distanceKm: 45,
        mode: "rail",
        narrative:
          "Regionalbahn via Metzingen; bring local Alb-lens cheese back on the late train.",
      },
    ],
    sustainabilityNotes:
      "Highlights off-peak visit times, community-owned accommodation, and rail-linked microadventures.",
    mapPath: [
      [48.5216, 9.0576],
      [48.3259, 8.9637],
      [48.3308, 9.2243],
      [48.2736, 9.4714],
      [48.4916, 9.3938],
      [48.5216, 9.0576],
    ],
  },
];

export const featuredJourneys = journeys.slice(0, 2);

export const getJourneyBySlug = (slug: string) =>
  journeys.find((journey) => journey.slug === slug);


