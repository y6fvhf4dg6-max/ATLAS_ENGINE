from atlas_config import PRODUCT_PROFILES, DEFAULT_PRODUCT
from atlas_geocoder import geocode_address
from atlas_area import calculate_area_bounds
from atlas_dem import get_elevation, get_dem_grid
from atlas_scale import scale_dem_grid
from atlas_mesh import build_mesh
from atlas_export import export_stl

print("======================================")
print("      ATLAS ENGINE v0.9")
print("======================================")

address = "Frankfurt Römer"
product_key = DEFAULT_PRODUCT
product = PRODUCT_PROFILES[product_key]

output_path = "STL/frankfurt_v0_9_signature.stl"

latitude, longitude = geocode_address(address)
elevation = get_elevation(latitude, longitude)

bounds = calculate_area_bounds(
    latitude,
    longitude,
    product["real_size_m"]
)

dem_grid = get_dem_grid(
    latitude,
    longitude,
    grid_size=16
)

scaled_grid = scale_dem_grid(
    dem_grid,
    model_size=product["model_size_mm"],
    base_thickness=product["base_thickness_mm"],
    terrain_height=product["terrain_height_mm"]
)

points, triangles = build_mesh(scaled_grid)

export_stl(points, triangles, output_path)

print()
print("Adres       :", address)
print("Ürün        :", product["name"])
print("Model       :", product["model_size_mm"], "mm")
print("Gerçek alan :", product["real_size_m"], "m x", product["real_size_m"], "m")
print("Ölçek       : 1:", product["scale"])
print("Enlem       :", latitude)
print("Boylam      :", longitude)
print("Yükseklik   :", elevation, "metre")

print()
print("Alan sınırları:")
print("North:", bounds["north"])
print("South:", bounds["south"])
print("East :", bounds["east"])
print("West :", bounds["west"])

print()
print("Mesh:")
print("Toplam nokta sayısı:", len(points))
print("Toplam üçgen sayısı:", len(triangles))

print()
print("STL oluşturuldu:", output_path)