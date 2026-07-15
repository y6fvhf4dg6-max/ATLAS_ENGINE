class AtlasAncientTheatreCaveaProfile:
    DEFAULT_EXPONENT = 1.25

    @staticmethod
    def normalized_height(
        radial_ratio,
        exponent=None,
    ):
        if exponent is None:
            exponent = (
                AtlasAncientTheatreCaveaProfile
                .DEFAULT_EXPONENT
            )

        radial_ratio = float(radial_ratio)
        exponent = float(exponent)

        if exponent <= 0.0:
            raise ValueError(
                "exponent must be greater than zero"
            )

        clamped_ratio = min(
            1.0,
            max(
                0.0,
                radial_ratio,
            ),
        )

        return clamped_ratio ** exponent

    @staticmethod
    def height_at_radius(
        radius,
        inner_radius,
        outer_radius,
        rise,
        exponent=None,
    ):
        radius = float(radius)
        inner_radius = float(inner_radius)
        outer_radius = float(outer_radius)
        rise = float(rise)

        radial_depth = (
            outer_radius
            - inner_radius
        )

        if radial_depth <= 0.0:
            raise ValueError(
                "outer_radius must be greater "
                "than inner_radius"
            )

        if rise < 0.0:
            raise ValueError(
                "rise must not be negative"
            )

        radial_ratio = (
            radius
            - inner_radius
        ) / radial_depth

        return (
            rise
            * AtlasAncientTheatreCaveaProfile
            .normalized_height(
                radial_ratio=radial_ratio,
                exponent=exponent,
            )
        )
