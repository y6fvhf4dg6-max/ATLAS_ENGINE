from __future__ import annotations

import math


class AtlasArchitecturalSemanticReliefComparisonReport:
    @staticmethod
    def _score(
        production,
        *,
        field_name,
    ):
        if not isinstance(production, dict):
            raise TypeError(
                f"{field_name} must be a dictionary"
            )

        if "feature_readability_score" not in production:
            raise ValueError(
                f"{field_name} must contain "
                "feature_readability_score"
            )

        try:
            score = float(
                production[
                    "feature_readability_score"
                ]
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "feature_readability_score "
                "must be numeric"
            ) from exc

        if not math.isfinite(score):
            raise ValueError(
                "feature_readability_score "
                "must be finite"
            )

        if not 0.0 <= score <= 1.0:
            raise ValueError(
                "feature_readability_score "
                "must satisfy 0 <= score <= 1"
            )

        return score

    @classmethod
    def feature_retention_score(
        cls,
        decisions,
    ):
        decisions = tuple(decisions)

        if not decisions:
            raise ValueError(
                "decisions must not be empty"
            )

        retained_actions = {
            "preserve",
            "enlarge",
            "merge",
            "simplify",
            "convert_to_engraving",
        }

        retained_count = 0

        for decision in decisions:
            action = getattr(
                decision,
                "action",
                None,
            )
            requires_operator_review = getattr(
                decision,
                "requires_operator_review",
                None,
            )

            if action is None:
                raise TypeError(
                    "decision must expose action"
                )

            if requires_operator_review is None:
                raise TypeError(
                    "decision must expose "
                    "requires_operator_review"
                )

            if (
                action in retained_actions
                and not requires_operator_review
            ):
                retained_count += 1

        return retained_count / len(decisions)

    @classmethod
    def build_from_decisions(
        cls,
        *,
        baseline_decisions,
        semantic_decisions,
    ):
        baseline_score = (
            cls.feature_retention_score(
                baseline_decisions
            )
        )
        semantic_score = (
            cls.feature_retention_score(
                semantic_decisions
            )
        )

        return cls.build(
            baseline={
                "feature_readability_score": (
                    baseline_score
                ),
            },
            semantic={
                "feature_readability_score": (
                    semantic_score
                ),
            },
        )

    @classmethod
    def build(
        cls,
        *,
        baseline,
        semantic,
    ):
        baseline_score = cls._score(
            baseline,
            field_name="baseline",
        )
        semantic_score = cls._score(
            semantic,
            field_name="semantic",
        )

        readability_delta = (
            semantic_score
            - baseline_score
        )

        semantic_more_readable = (
            readability_delta > 0.0
        )

        return {
            "type": (
                "architectural_semantic_relief_comparison_report"
            ),
            "baseline_feature_readability_score": (
                baseline_score
            ),
            "semantic_feature_readability_score": (
                semantic_score
            ),
            "readability_delta": (
                readability_delta
            ),
            "semantic_more_readable": (
                semantic_more_readable
            ),
            "status": (
                "PASS"
                if semantic_more_readable
                else "FAIL"
            ),
        }
