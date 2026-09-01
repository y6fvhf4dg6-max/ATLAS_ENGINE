from __future__ import annotations

import numpy as np

from CORE.atlas_portrait_dense_image_surface_evidence import (
    AtlasPortraitDenseImageSurfaceEvidence,
)


class AtlasPortraitDenseImageSurfaceEvidenceProducer:
    @classmethod
    def build(
        cls,
        *,
        evidence_id: str,
        source_view_id: str,
        source_rgb: object,
        canonical_vertex_indices: object,
        projected_xy: object,
        rendered_rgb: object,
        confidence: object,
    ) -> AtlasPortraitDenseImageSurfaceEvidence:
        source = np.asarray(
            source_rgb,
            dtype=np.float64,
        )

        if (
            source.ndim != 3
            or source.shape[2] != 3
        ):
            raise ValueError(
                "source_rgb must have shape (H, W, 3)."
            )

        if source.shape[0] <= 0 or source.shape[1] <= 0:
            raise ValueError(
                "source_rgb image dimensions must be positive."
            )

        if not np.all(np.isfinite(source)):
            raise ValueError(
                "source_rgb must contain only finite values."
            )

        if np.any(source < 0.0) or np.any(source > 1.0):
            raise ValueError(
                "source_rgb rgb values must be inside "
                "the 0.0..1.0 range."
            )

        points = np.asarray(
            projected_xy,
            dtype=np.float64,
        )

        if (
            points.ndim != 2
            or points.shape[1] != 2
        ):
            raise ValueError(
                "projected_xy must have shape (N, 2)."
            )

        if points.shape[0] == 0:
            raise ValueError(
                "projected_xy must not be empty."
            )

        if not np.all(np.isfinite(points)):
            raise ValueError(
                "projected_xy must contain only finite values."
            )

        height, width = source.shape[:2]

        x = points[:, 0]
        y = points[:, 1]

        inside = (
            (x >= 0.0)
            & (x <= float(width - 1))
            & (y >= 0.0)
            & (y <= float(height - 1))
        )

        if not np.all(inside):
            raise ValueError(
                "all projected_xy samples must be inside "
                "source image."
            )

        observed_rgb = cls._bilinear_sample(
            source,
            points,
        )

        return AtlasPortraitDenseImageSurfaceEvidence(
            evidence_id=evidence_id,
            source_view_id=source_view_id,
            image_width=width,
            image_height=height,
            canonical_vertex_indices=(
                canonical_vertex_indices
            ),
            projected_xy=points,
            observed_rgb=observed_rgb,
            rendered_rgb=rendered_rgb,
            confidence=confidence,
        )

    @staticmethod
    def _bilinear_sample(
        source_rgb: np.ndarray,
        projected_xy: np.ndarray,
    ) -> np.ndarray:
        x = projected_xy[:, 0]
        y = projected_xy[:, 1]

        x0 = np.floor(x).astype(np.int64)
        y0 = np.floor(y).astype(np.int64)

        x1 = np.minimum(
            x0 + 1,
            source_rgb.shape[1] - 1,
        )
        y1 = np.minimum(
            y0 + 1,
            source_rgb.shape[0] - 1,
        )

        wx = x - x0
        wy = y - y0

        c00 = source_rgb[y0, x0]
        c10 = source_rgb[y0, x1]
        c01 = source_rgb[y1, x0]
        c11 = source_rgb[y1, x1]

        top = (
            c00 * (1.0 - wx[:, None])
            + c10 * wx[:, None]
        )

        bottom = (
            c01 * (1.0 - wx[:, None])
            + c11 * wx[:, None]
        )

        return (
            top * (1.0 - wy[:, None])
            + bottom * wy[:, None]
        )

    @staticmethod
    def rasterized_vertex_visibility_mask(
        *,
        projected_xy,
        camera_z,
        faces,
        image_width: int,
        image_height: int,
        image_support_mask=None,
    ):
        """
        Return a per-vertex image-space visibility mask.

        Visibility is established by reusing
        AtlasProjectedSemanticMeshDepthRasterizer with
        reciprocal positive camera depth (1 / Z), because
        that rasterizer retains the greatest depth value.
        Under the ATLAS portrait camera convention, smaller
        positive Z is nearer the camera and therefore has the
        greater reciprocal depth.

        A vertex is visible only when the rasterized winning
        face at its projected pixel contains that vertex.
        An optional image-space support mask is then applied.
        """
        import numpy as np

        from CORE.atlas_projected_semantic_mesh_depth_rasterizer import (
            AtlasProjectedSemanticMeshDepthRasterizer,
        )

        xy = np.asarray(
            projected_xy,
            dtype=np.float64,
        )
        z = np.asarray(
            camera_z,
            dtype=np.float64,
        )
        indexed_faces = np.asarray(
            faces,
            dtype=np.int64,
        )

        if (
            xy.ndim != 2
            or xy.shape[1] != 2
            or not np.isfinite(xy).all()
        ):
            raise ValueError(
                "projected_xy must have shape "
                "(vertex_count, 2) and be finite"
            )

        vertex_count = xy.shape[0]

        if (
            z.ndim != 1
            or z.shape[0] != vertex_count
            or not np.isfinite(z).all()
            or np.any(z <= 0.0)
        ):
            raise ValueError(
                "camera_z must contain one finite positive "
                "depth per projected vertex"
            )

        if (
            indexed_faces.ndim != 2
            or indexed_faces.shape[1] != 3
        ):
            raise ValueError(
                "faces must have shape (face_count, 3)"
            )

        if (
            np.any(indexed_faces < 0)
            or np.any(indexed_faces >= vertex_count)
        ):
            raise ValueError(
                "faces reference invalid vertex indices"
            )

        if (
            isinstance(image_width, bool)
            or not isinstance(image_width, int)
            or image_width <= 0
            or isinstance(image_height, bool)
            or not isinstance(image_height, int)
            or image_height <= 0
        ):
            raise ValueError(
                "image dimensions must be positive integers"
            )

        support = None
        if image_support_mask is not None:
            support = np.asarray(
                image_support_mask,
                dtype=np.bool_,
            )

            if support.shape != (
                image_height,
                image_width,
            ):
                raise ValueError(
                    "image_support_mask must match "
                    "(image_height, image_width)"
                )

        reciprocal_z = 1.0 / z

        raster_triangles = tuple(
            tuple(
                (
                    float(xy[vertex_index, 0]),
                    float(xy[vertex_index, 1]),
                    float(reciprocal_z[vertex_index]),
                )
                for vertex_index in face
            )
            for face in indexed_faces
        )

        raster = (
            AtlasProjectedSemanticMeshDepthRasterizer
            .rasterize(
                mesh={
                    "triangles": raster_triangles,
                },
                width_mm=float(image_width - 1),
                depth_mm=float(image_height - 1),
                rows=image_height,
                columns=image_width,
            )
        )

        face_index_map = np.asarray(
            raster["face_index_map"],
            dtype=np.int64,
        )

        visible = np.zeros(
            vertex_count,
            dtype=np.bool_,
        )

        rounded_x = np.rint(
            xy[:, 0]
        ).astype(np.int64)
        rounded_y = np.rint(
            xy[:, 1]
        ).astype(np.int64)

        inside = (
            (rounded_x >= 0)
            & (rounded_x < image_width)
            & (rounded_y >= 0)
            & (rounded_y < image_height)
        )

        for vertex_index in np.flatnonzero(inside):
            row = int(
                rounded_y[vertex_index]
            )
            column = int(
                rounded_x[vertex_index]
            )

            winning_face_index = int(
                face_index_map[
                    row,
                    column,
                ]
            )

            if winning_face_index < 0:
                continue

            if vertex_index not in indexed_faces[
                winning_face_index
            ]:
                continue

            if (
                support is not None
                and not support[
                    row,
                    column,
                ]
            ):
                continue

            visible[
                vertex_index
            ] = True

        return visible

    @classmethod
    def candidate_sensitive_pairwise_photometric_residual(
        cls,
        *,
        source_rgb_a,
        source_rgb_b,
        canonical_vertex_indices,
        baseline_confidence,
        candidate_projected_xy_a,
        candidate_camera_z_a,
        candidate_projected_xy_b,
        candidate_camera_z_b,
        faces,
        image_support_mask_a=None,
        image_support_mask_b=None,
    ) -> np.ndarray:
        """
        Build a fixed-cardinality pairwise dense image residual
        from the current candidate geometry.

        Candidate projection and rasterized visibility are live
        evaluation inputs.  The accepted canonical vertex set
        and baseline confidence remain fixed.

        Samples visible in both views use the current pairwise
        RGB difference.  Accepted samples which become
        candidate-invisible or leave either image retain their
        residual slots and receive the maximum normalized RGB
        mismatch weighted only by frozen baseline confidence.
        """
        source_a = np.asarray(
            source_rgb_a,
            dtype=np.float64,
        )
        source_b = np.asarray(
            source_rgb_b,
            dtype=np.float64,
        )

        for name, source in (
            ("source_rgb_a", source_a),
            ("source_rgb_b", source_b),
        ):
            if (
                source.ndim != 3
                or source.shape[2] != 3
                or source.shape[0] <= 0
                or source.shape[1] <= 0
                or not np.all(np.isfinite(source))
                or np.any(source < 0.0)
                or np.any(source > 1.0)
            ):
                raise ValueError(
                    f"{name} must have shape (H, W, 3) "
                    "with finite rgb inside 0.0..1.0"
                )

        vertex_indices = np.asarray(
            canonical_vertex_indices,
            dtype=np.int64,
        )
        confidence = np.asarray(
            baseline_confidence,
            dtype=np.float64,
        )

        if vertex_indices.ndim != 1 or vertex_indices.size == 0:
            raise ValueError(
                "canonical_vertex_indices must be a nonempty "
                "1D array"
            )

        if (
            confidence.ndim != 1
            or confidence.shape != vertex_indices.shape
            or not np.all(np.isfinite(confidence))
            or np.any(confidence < 0.0)
            or np.any(confidence > 1.0)
        ):
            raise ValueError(
                "baseline_confidence must match accepted "
                "vertex cardinality and be inside 0.0..1.0"
            )

        xy_a = np.asarray(
            candidate_projected_xy_a,
            dtype=np.float64,
        )
        xy_b = np.asarray(
            candidate_projected_xy_b,
            dtype=np.float64,
        )
        z_a = np.asarray(
            candidate_camera_z_a,
            dtype=np.float64,
        )
        z_b = np.asarray(
            candidate_camera_z_b,
            dtype=np.float64,
        )

        if (
            xy_a.ndim != 2
            or xy_a.shape[1] != 2
            or xy_b.shape != xy_a.shape
            or z_a.shape != (xy_a.shape[0],)
            or z_b.shape != (xy_a.shape[0],)
        ):
            raise ValueError(
                "candidate projections/depths must share one "
                "full-mesh vertex cardinality"
            )

        if (
            np.any(vertex_indices < 0)
            or np.any(vertex_indices >= xy_a.shape[0])
        ):
            raise ValueError(
                "canonical_vertex_indices reference invalid "
                "candidate vertices"
            )

        visible_a = cls.rasterized_vertex_visibility_mask(
            projected_xy=xy_a,
            camera_z=z_a,
            faces=faces,
            image_width=int(source_a.shape[1]),
            image_height=int(source_a.shape[0]),
            image_support_mask=image_support_mask_a,
        )
        visible_b = cls.rasterized_vertex_visibility_mask(
            projected_xy=xy_b,
            camera_z=z_b,
            faces=faces,
            image_width=int(source_b.shape[1]),
            image_height=int(source_b.shape[0]),
            image_support_mask=image_support_mask_b,
        )

        accepted_xy_a = xy_a[vertex_indices]
        accepted_xy_b = xy_b[vertex_indices]

        inside_a = (
            (accepted_xy_a[:, 0] >= 0.0)
            & (
                accepted_xy_a[:, 0]
                <= float(source_a.shape[1] - 1)
            )
            & (accepted_xy_a[:, 1] >= 0.0)
            & (
                accepted_xy_a[:, 1]
                <= float(source_a.shape[0] - 1)
            )
        )
        inside_b = (
            (accepted_xy_b[:, 0] >= 0.0)
            & (
                accepted_xy_b[:, 0]
                <= float(source_b.shape[1] - 1)
            )
            & (accepted_xy_b[:, 1] >= 0.0)
            & (
                accepted_xy_b[:, 1]
                <= float(source_b.shape[0] - 1)
            )
        )

        joint_visible = (
            visible_a[vertex_indices]
            & visible_b[vertex_indices]
            & inside_a
            & inside_b
        )

        residual = np.ones(
            (vertex_indices.size, 3),
            dtype=np.float64,
        )

        if np.any(joint_visible):
            observed_a = cls._bilinear_sample(
                source_a,
                accepted_xy_a[joint_visible],
            )
            observed_b = cls._bilinear_sample(
                source_b,
                accepted_xy_b[joint_visible],
            )
            residual[joint_visible] = (
                observed_a - observed_b
            )

        residual *= np.sqrt(confidence)[:, None]

        return np.asarray(
            residual.reshape(-1),
            dtype=np.float64,
        )

    @staticmethod
    def photometric_residual(
        evidence: AtlasPortraitDenseImageSurfaceEvidence,
    ) -> np.ndarray:
        if not isinstance(
            evidence,
            AtlasPortraitDenseImageSurfaceEvidence,
        ):
            raise TypeError(
                "evidence must be an "
                "AtlasPortraitDenseImageSurfaceEvidence."
            )

        weighted = (
            np.sqrt(
                evidence.confidence
            )[:, None]
            * (
                evidence.observed_rgb
                - evidence.rendered_rgb
            )
        )

        return np.asarray(
            weighted,
            dtype=np.float64,
        ).reshape(-1)
