from app.models import *
from app.services.google_client import call_compute_routes,parse_routes
from app.classification.osm_classifier import OsmRulesClassifier
from app.services.valhalla_client import get_segments
from math import inf

CRITICAL_SCORE_THRESHOLD = 2
MAX_CONFIDENCE_FOR_AI = 0.4

MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE = {
    "rural" : 500, 
    "extraurban" : 1000,
    "urban" : 700
}

SAMPLE_INTERVAL_PER_ROAD_TYPE = {
    "rural": 800,       # 1 foto ogni 800m
    "extraurban": 1500, # 1 foto ogni 1.5km
    "urban": 400        # 1 foto ogni 400m
}

def summarize(
    pairs: list[SegmentTuple],
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
        
def filter_segments_for_ai(pairs: list[SegmentTuple]) -> list[ClassifiedSegment]:
    #This function will select betweeen all road segments those that will need to be analyzed by AI
    segments_to_analyze = []

    for val_seg, class_seg in pairs:
        if(class_seg is None):
            continue

        if(class_seg.condition_score <= CRITICAL_SCORE_THRESHOLD or class_seg.confidence <= MAX_CONFIDENCE_FOR_AI):
            segments_to_analyze.append(class_seg)

    return segments_to_analyze 

def filter_road_chunks_for_ai(classified_segments: list[ClassifiedSegment]) -> list[SegmentsChunk]:
    """Defines which series of route segments needs to be analyzed with AI"""
    current_road_type = ""
    current_cumulative_distance = 0.0
    current_weighted_score = 0.0
    current_segments_list = []

    chunks = []

    for seg in classified_segments:
        if current_road_type and current_road_type != seg.road_type:
            if current_cumulative_distance > 0 : weighted_average =  current_weighted_score / current_cumulative_distance
            if current_cumulative_distance >= MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE.get(current_road_type,inf) and weighted_average <= 2.5:
                chunk = SegmentsChunk(road_type=current_road_type, length=current_cumulative_distance, avg_score=weighted_average,segments=current_segments_list.copy())
                chunks.append(chunk)

            current_cumulative_distance = 0.0
            current_weighted_score = 0.0
            current_segments_list.clear()
            current_road_type = ""
        
        current_road_type = seg.road_type 
        current_cumulative_distance += seg.segment.length
        current_segments_list.append(seg)

        score = seg.condition_score if seg.condition_score is not None else 0
        current_weighted_score += score * seg.segment.length

    if current_road_type:
        weighted_average = current_weighted_score / current_cumulative_distance
        if current_cumulative_distance >= MIN_CUMULATIVE_DISTANCE_PER_ROAD_TYPE.get(current_road_type,inf) and weighted_average <= 2.5:
            chunk = SegmentsChunk(road_type=current_road_type, length=current_cumulative_distance, avg_score=weighted_average,segments=current_segments_list.copy())
            chunks.append(chunk)
            
    return chunks


def get_sample_points_from_chunk(chunk: SegmentsChunk) -> list[Coord]:
    """Extract coordinates from chunks that will be given to vision ai for segment classification"""
    points_number = max(chunk.length // SAMPLE_INTERVAL_PER_ROAD_TYPE[chunk.road_type], 1)
    cumulative_lenght_from_start = 0 

    coordinates_list = []

    if(points_number == 1):
        #chunk shorter than distance hit rate for his road_type
        for seg in chunk.segments:
            cumulative_lenght_from_start += seg.segment.length

            if(cumulative_lenght_from_start >= chunk.length / 2):
                segment_coords_list_size = len(seg.segment.coords)
                coordinates_list.append(seg.segment.coords[segment_coords_list_size // 2]) #Extracts the coordinate in the middle of the segment coordinates array
                break
    else:
        #chunk longer than distance hit rate for his road_type 
        for seg in chunk.segments:
            cumulative_lenght_from_start += seg.segment.length 

            if(cumulative_lenght_from_start >= SAMPLE_INTERVAL_PER_ROAD_TYPE[chunk.road_type]):
                segment_coords_list_size = len(seg.segment.coords)
                coordinates_list.append(seg.segment.coords[segment_coords_list_size // 2])  
                cumulative_lenght_from_start = 0

    return coordinates_list


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
        
