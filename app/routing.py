from app.models import ClassifiedSegment, RouteSummary, GoogleMapsRoute, ValhallaSegment
from app.services.google_client import call_compute_routes,parse_routes
from app.classification.osm_classifier import OsmRulesClassifier
from app.services.valhalla_client import get_segments

CRITICAL_SCORE_THRESHOLD = 2

def summarize(
    pairs: list[tuple[ValhallaSegment, ClassifiedSegment | None]],
    route: GoogleMapsRoute,
) -> RouteSummary:
    """Summarize route"""

    total_classified_meters = 0.0
    total_non_classified_meters = 0.0
    total_classified_score = 0.0
    total_critical_meters = 0.0
    total_meters = 0.0

    meters_by_road_type = {}
    meters_by_road_surface = {}

    for val_seg,class_seg in pairs:            
        if class_seg is not None:
            total_classified_meters += val_seg.length
            total_classified_score += class_seg.condition_score * val_seg.length
            if class_seg.condition_score <= CRITICAL_SCORE_THRESHOLD :
                total_critical_meters += val_seg.length

            meters_by_road_type[class_seg.road_type] = meters_by_road_type.get(class_seg.road_type,0) + val_seg.length 
            meters_by_road_surface[class_seg.surface_type] = meters_by_road_surface.get(class_seg.surface_type,0) + val_seg.length      
        else: 
            total_non_classified_meters += val_seg.length

        total_meters += val_seg.length

    quality_score = None
    coverage = 0.0

    if total_classified_meters != 0 : 
        quality_score = total_classified_score / total_classified_meters 

    if total_meters != 0: 
        coverage = total_classified_meters / total_meters

    return RouteSummary(polyline=route.polyline, distance_m=route.distance_m, duration_s=route.duration_s, quality_score=quality_score, coverage=coverage, distance_by_road_type=meters_by_road_type, distance_by_surface=meters_by_road_surface, critical_m=total_critical_meters, unrated_m=total_non_classified_meters, pairs=pairs)
        


def analyze_route(route: GoogleMapsRoute) -> RouteSummary:
    """Analizza UNA route: Valhalla -> classificazione -> summarize."""

    segments = get_segments(route.points_list)
    classifier = OsmRulesClassifier()

    pairs = [(seg, classifier.classify(seg)) for seg in segments]

    return summarize(pairs,route)

def get_scored_routes(start: str, end: str, avoid_tolls: bool = False) -> list[RouteSummary]:
    """Public functions: from a couple of indexes returns a list of summarized routes"""
    summarized_routes = []
    for route in parse_routes(call_compute_routes(starting_point=start, destination_point=end, avoidTolls=avoid_tolls)):
        summarized_routes.append(analyze_route(route))

    return summarized_routes
        
