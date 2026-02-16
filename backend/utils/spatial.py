import math
import os
from typing import Tuple, Optional
import jageocoder

# JIS X 0410 Standard Area Mesh calculation

def lat_lon_to_mesh(lat: float, lon: float, level: int = 3) -> str:
    """
    Convert lat/lon to JIS X 0410 mesh code.
    
    Level 1: 4 digits (approx 80km)
    Level 2: 6 digits (approx 10km)
    Level 3: 8 digits (approx 1km) - Standard for most stats
    Level 4: 9 digits (approx 500m) - Half standard
    Level 5: 10 digits (approx 250m) - Quarter standard
    """
    
    # 1st Mesh
    # Lat difference: 40 mins (2/3 degree)
    # Lon difference: 1 degree
    lat_1 = int(lat * 1.5)
    lon_1 = int(lon - 100.0)
    
    code = f"{lat_1}{lon_1}"
    if level == 1:
        return code
        
    # 2nd Mesh (8x8 breakdown of 1st)
    # Lat diff: 5 mins (1/12 degree)
    # Lon diff: 7.5 mins (1/8 degree)
    res_lat_1 = lat * 1.5 - lat_1
    res_lon_1 = lon - 100.0 - lon_1
    
    lat_2 = int(res_lat_1 * 8)
    lon_2 = int(res_lon_1 * 8)
    
    code += f"{lat_2}{lon_2}"
    if level == 2:
        return code
        
    # 3rd Mesh (10x10 breakdown of 2nd) - Basic Grid
    # Lat diff: 30 secs
    # Lon diff: 45 secs
    res_lat_2 = res_lat_1 * 8 - lat_2
    res_lon_2 = res_lon_1 * 8 - lon_2
    
    lat_3 = int(res_lat_2 * 10)
    lon_3 = int(res_lon_2 * 10)
    
    code += f"{lat_3}{lon_3}"
    if level == 3:
        return code
        
    # 4th Mesh (2x2 breakdown of 3rd) - Half Grid
    res_lat_3 = res_lat_2 * 10 - lat_3
    res_lon_3 = res_lon_2 * 10 - lon_3
    
    lat_4 = int(res_lat_3 * 2)
    lon_4 = int(res_lon_3 * 2)
    
    # 1=SW, 2=SE, 3=NW, 4=NE (JIS convention: 1 for lower-left, 2 for lower-right...)
    # Actually:
    # lat 0, lon 0 -> 1
    # lat 0, lon 1 -> 2
    # lat 1, lon 0 -> 3
    # lat 1, lon 1 -> 4
    n_4 = (lat_4 * 2) + (lon_4 + 1)
    
    code += f"{n_4}"
    
    if level == 4:
        return code

    # Higher levels logic can be added if needed
    return code

def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode address string to (lat, lon) using jageocoder.
    Returns None if not found or dictionary not initialized.
    """
    try:
        # Check if jageocoder is initialized
        if not jageocoder.is_initialized():
            # Try to init with default (env var or default path)
            db_dir = os.getenv("JAGEOCODER_DB_DIR", "/app/data/jageocoder_db")
            if os.path.exists(db_dir):
                try:
                    jageocoder.init(db_dir=db_dir)
                except Exception as e:
                    print(f"❌ jageocoder init failed: {e}")
                    return None
            else:
                 # print(f"❌ DB dir not found: {db_dir}")
                 return None

        results = jageocoder.searchNode(address)
        if results and len(results) > 0:
            # Best match
            node = results[0].node
            return (node.y, node.x) # lat, lon
        
        print(f"⚠️ No results for '{address}'")
        return None
        
    except Exception as e:
        print(f"❌ Geocoding error: {e}")
    return None
