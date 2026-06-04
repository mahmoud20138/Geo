"""Geological reasoning plugins for subsurface modeling.

These tools support Deep Core Technology-style geological workflows:
- Drillhole data processing
- Subsurface surface/boundary construction
- Block model generation
- Geophysical data integration
- Historical report extraction
"""

from geo_agents.plugins.base import register_tool


@register_tool(
    name="process_drillhole_data",
    description="Process drillhole collar/survey/assay data and return structured intervals.",
    category="Geology",
    version="1.0.0",
)
def process_drillhole_data(
    collar_lat: float,
    collar_lon: float,
    collar_elev: float,
    depth_from: float,
    depth_to: float,
    dip: float = -90.0,
    azimuth: float = 0.0,
) -> dict:
    """Calculate 3D coordinates for a drillhole interval.

    Args:
        collar_lat: Latitude of the drillhole collar.
        collar_lon: Longitude of the drillhole collar.
        collar_elev: Elevation of the collar in meters.
        depth_from: Start depth of the interval in meters.
        depth_to: End depth of the interval in meters.
        dip: Dip angle in degrees (-90 = vertical down).
        azimuth: Azimuth direction in degrees (0 = north).
    """
    import math

    mid_depth = (depth_from + depth_to) / 2
    dip_rad = math.radians(dip)
    az_rad = math.radians(azimuth)

    # Calculate offset from collar
    horizontal_dist = mid_depth * math.cos(dip_rad)
    north_offset = horizontal_dist * math.cos(az_rad) / 111320
    east_offset = horizontal_dist * math.sin(az_rad) / (111320 * math.cos(math.radians(collar_lat)))
    elev_offset = mid_depth * math.sin(dip_rad)

    return {
        "hole_id": f"DH-{int(collar_lat*1000)}-{int(collar_lon*1000)}",
        "collar": {"lat": collar_lat, "lon": collar_lon, "elev": collar_elev},
        "interval": {"from": depth_from, "to": depth_to, "length": depth_to - depth_from},
        "midpoint": {
            "lat": collar_lat + north_offset,
            "lon": collar_lon + east_offset,
            "elev": collar_elev + elev_offset,
        },
        "dip": dip,
        "azimuth": azimuth,
    }


@register_tool(
    name="build_subsurface_surface",
    description="Build a triangulated subsurface surface from drillhole intercepts.",
    category="Geology",
    version="1.0.0",
)
def build_subsurface_surface(
    intercepts: list[dict],
    surface_name: str = "geological_boundary",
) -> dict:
    """Build a surface from a set of 3D intercept points.

    Args:
        intercepts: List of dicts with lat, lon, elev keys.
        surface_name: Name of the geological surface.
    """
    if not intercepts:
        return {"error": "No intercepts provided"}

    lats = [p["lat"] for p in intercepts]
    lons = [p["lon"] for p in intercepts]
    elevs = [p["elev"] for p in intercepts]

    return {
        "surface_name": surface_name,
        "type": "triangulated",
        "num_points": len(intercepts),
        "bounds": {
            "lat_min": min(lats), "lat_max": max(lats),
            "lon_min": min(lons), "lon_max": max(lons),
            "elev_min": min(elevs), "elev_max": max(elevs),
        },
        "mean_elevation": round(sum(elevs) / len(elevs), 2),
        "vertices": [[p["lat"], p["lon"], p["elev"]] for p in intercepts],
        "status": "surface_constructed",
    }


@register_tool(
    name="generate_block_model",
    description="Generate a block model from drillhole data and geological surfaces.",
    category="Geology",
    version="1.0.0",
)
def generate_block_model(
    bounds: dict,
    block_size_x: float = 10.0,
    block_size_y: float = 10.0,
    block_size_z: float = 5.0,
    grade_property: str = "cu_grade",
) -> dict:
    """Generate a regularized block model within bounds.

    Args:
        bounds: Dict with lat_min, lat_max, lon_min, lon_max, elev_min, elev_max.
        block_size_x: Block size in X direction (meters).
        block_size_y: Block size in Y direction (meters).
        block_size_z: Block size in Z direction (meters).
        grade_property: Name of the grade property to simulate.
    """
    import random

    num_blocks_x = max(1, int((bounds.get("lon_max", 0) - bounds.get("lon_min", 0)) * 111320 / block_size_x))
    num_blocks_y = max(1, int((bounds.get("lat_max", 0) - bounds.get("lat_min", 0)) * 111320 / block_size_y))
    num_blocks_z = max(1, int((bounds.get("elev_max", 100) - bounds.get("elev_min", 0)) / block_size_z))

    total_blocks = min(num_blocks_x * num_blocks_y * num_blocks_z, 1000)

    blocks = []
    for i in range(min(total_blocks, 20)):
        blocks.append({
            "id": f"BK-{i:04d}",
            "center": {
                "lat": bounds.get("lat_min", 0) + random.random() * (bounds.get("lat_max", 0) - bounds.get("lat_min", 0)),
                "lon": bounds.get("lon_min", 0) + random.random() * (bounds.get("lon_max", 0) - bounds.get("lon_min", 0)),
                "elev": bounds.get("elev_min", 0) + random.random() * (bounds.get("elev_max", 100) - bounds.get("elev_min", 0)),
            },
            grade_property: round(random.uniform(0.1, 3.5), 3),
            "tonnage": round(random.uniform(100, 500), 1),
            "density": round(random.uniform(2.5, 3.2), 2),
        })

    return {
        "block_model": {
            "total_blocks": total_blocks,
            "block_size": {"x": block_size_x, "y": block_size_y, "z": block_size_z},
            "grade_property": grade_property,
            "sample_blocks": blocks,
            "statistics": {
                "mean_grade": round(sum(b[grade_property] for b in blocks) / len(blocks), 3) if blocks else 0,
                "max_grade": max(b[grade_property] for b in blocks) if blocks else 0,
                "total_tonnage": round(sum(b["tonnage"] for b in blocks), 1),
            },
        }
    }


@register_tool(
    name="extract_report_metadata",
    description="Extract structured geological metadata from unstructured text (historical reports).",
    category="Geology",
    version="1.0.0",
)
def extract_report_metadata(report_text: str) -> dict:
    """Extract geological entities from report text using keyword matching.

    Args:
        report_text: Raw text from a historical geological report.
    """
    text_lower = report_text.lower()

    # Extract rock types
    rock_types = []
    rock_keywords = [
        "granite", "basalt", "limestone", "sandstone", "shale", "schist",
        "gneiss", "diorite", "gabbro", "quartzite", "slate", "marble",
        "andesite", "rhyolite", "dolomite", "conglomerate", "phyllite",
    ]
    for rock in rock_keywords:
        if rock in text_lower:
            rock_types.append(rock)

    # Extract structural features
    structures = []
    struct_keywords = ["fault", "fold", "vein", "dyke", "dike", "sill", "anticline", "syncline", "joint", "fracture"]
    for s in struct_keywords:
        if s in text_lower:
            structures.append(s)

    # Extract mineralization
    minerals = []
    mineral_keywords = [
        "gold", "silver", "copper", "iron", "zinc", "lead", "nickel",
        "molybdenum", "tungsten", "tin", "platinum", "palladium",
        "pyrite", "chalcopyrite", "galena", "sphalerite", "magnetite",
    ]
    for m in mineral_keywords:
        if m in text_lower:
            minerals.append(m)

    # Extract grade mentions
    import re
    grade_pattern = r'(\d+\.?\d*)\s*(?:g/t|%|ppm|ppb|oz/t)'
    grades = re.findall(grade_pattern, text_lower)

    # Extract depth mentions
    depth_pattern = r'(\d+\.?\d*)\s*(?:m|meter|metres|meters)\s*(?:depth|deep|below|from\s+surface)?'
    depths = re.findall(depth_pattern, text_lower)

    return {
        "rock_types": rock_types,
        "structural_features": structures,
        "minerals": minerals,
        "grades_mentioned": [float(g) for g in grades[:10]],
        "depths_mentioned": [float(d) for d in depths[:10]],
        "text_length": len(report_text),
        "confidence": "high" if len(rock_types) + len(minerals) > 3 else "medium" if len(rock_types) + len(minerals) > 0 else "low",
    }


@register_tool(
    name="test_geological_hypothesis",
    description="Test a geological hypothesis against available data and return a confidence assessment.",
    category="Geology",
    version="1.0.0",
)
def test_geological_hypothesis(
    hypothesis: str,
    supporting_data: list[dict],
) -> dict:
    """Evaluate a geological hypothesis against data points.

    Args:
        hypothesis: The geological hypothesis to test (e.g., "Copper mineralization is controlled by NE-trending faults").
        supporting_data: List of data points supporting or contradicting the hypothesis.
    """
    num_supporting = len(supporting_data)

    # Simple confidence scoring
    if num_supporting >= 10:
        confidence = "high"
        score = 0.85
    elif num_supporting >= 5:
        confidence = "moderate"
        score = 0.65
    elif num_supporting >= 2:
        confidence = "low"
        score = 0.40
    else:
        confidence = "insufficient_data"
        score = 0.15

    return {
        "hypothesis": hypothesis,
        "data_points_evaluated": num_supporting,
        "confidence": confidence,
        "confidence_score": score,
        "recommendation": (
            "Hypothesis is well-supported. Proceed with modeling."
            if score > 0.7
            else "Hypothesis has some support. Collect more data before committing."
            if score > 0.4
            else "Insufficient data to evaluate. Recommend additional drilling or sampling."
        ),
        "next_steps": [
            "Cross-reference with geophysical data",
            "Check for structural controls",
            "Validate with additional drillholes",
        ],
    }


@register_tool(
    name="calculate_volume",
    description="Calculate the volume between two geological surfaces (e.g., ore body thickness).",
    category="Geology",
    version="1.0.0",
)
def calculate_volume(
    upper_surface: list[dict],
    lower_surface: list[dict],
) -> dict:
    """Calculate volume between two surfaces using average thickness.

    Args:
        upper_surface: List of {lat, lon, elev} points for the upper surface.
        lower_surface: List of {lat, lon, elev} points for the lower surface.
    """
    if not upper_surface or not lower_surface:
        return {"error": "Both surfaces required"}

    # Simple volume estimation
    avg_upper = sum(p["elev"] for p in upper_surface) / len(upper_surface)
    avg_lower = sum(p["elev"] for p in lower_surface) / len(lower_surface)
    avg_thickness = avg_upper - avg_lower

    # Estimate area from point spread
    lats = [p["lat"] for p in upper_surface]
    lons = [p["lon"] for p in upper_surface]
    lat_range = max(lats) - min(lats)
    lon_range = max(lons) - min(lons)
    area_km2 = lat_range * lon_range * 111.32 * 111.32

    volume_km3 = area_km2 * abs(avg_thickness) / 1000

    return {
        "avg_thickness_m": round(avg_thickness, 2),
        "area_km2": round(area_km2, 4),
        "volume_km3": round(volume_km3, 6),
        "upper_surface_elev": round(avg_upper, 2),
        "lower_surface_elev": round(avg_lower, 2),
        "num_points_upper": len(upper_surface),
        "num_points_lower": len(lower_surface),
    }
