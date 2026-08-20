from CORE.atlas_foundation_first_engine import AtlasFoundationFirstEngine


def test_default_terrain_grid_limits_physical_cell_size_for_150mm_product():
    assert AtlasFoundationFirstEngine._resolve_terrain_grid_size(
        requested_grid_size=None,
        size_x_mm=150.0,
        size_y_mm=150.0,
    ) == 49


def test_default_terrain_grid_scales_with_larger_product():
    assert AtlasFoundationFirstEngine._resolve_terrain_grid_size(
        requested_grid_size=None,
        size_x_mm=200.0,
        size_y_mm=200.0,
    ) == 65


def test_explicit_terrain_grid_override_is_preserved():
    assert AtlasFoundationFirstEngine._resolve_terrain_grid_size(
        requested_grid_size=25,
        size_x_mm=150.0,
        size_y_mm=150.0,
    ) == 25


def test_generate_city_stl_uses_adaptive_terrain_grid_by_default():
    import inspect
    parameter = inspect.signature(AtlasFoundationFirstEngine.generate_city_stl).parameters["terrain_grid_size"]
    assert parameter.default is None


def test_adaptive_terrain_grid_falls_back_to_target_size_when_xy_sizes_unresolved():
    assert AtlasFoundationFirstEngine._resolve_terrain_grid_size(
        requested_grid_size=None,
        size_x_mm=None,
        size_y_mm=None,
        target_size_mm=100.0,
    ) == 33
