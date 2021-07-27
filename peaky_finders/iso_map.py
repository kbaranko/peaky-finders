import geopandas as gpd
import pandas as pd
from shapely import wkt


ISO_MAP_IDS = {
    56669: 'MISO',
    14725: 'PJM',
    2775: 'CAISO',
    13434: 'ISONE',
    13501: 'NYISO'
}


def get_iso_map() -> gpd.GeoDataFrame:
    """Reads the csv of ISO geographies and returns as gdf."""
    iso_df = pd.read_csv('iso_map_final.csv')
    iso_df['geometry'] = iso_df['geometry'].apply(wkt.loads)
    iso_gdf = gpd.GeoDataFrame(iso_df, crs="EPSG:4326", geometry='geometry')
    return iso_gdf
