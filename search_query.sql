SELECT *
FROM (
        SELECT 'dashboard' AS "model",
            "dashboard"."id",
            "dashboard"."name",
            CAST(NULL AS text) AS "display_name",
            "dashboard"."description",
            "dashboard"."archived",
            "dashboard"."collection_id",
            "collection_app"."id" AS "collection_app_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "dashboard"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "dashboard"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "report_dashboard" "dashboard"
            LEFT JOIN "dashboard_bookmark" "bookmark" ON (
                "bookmark"."dashboard_id" = "dashboard"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "collection" "collection" ON "dashboard"."collection_id" = "collection"."id"
            LEFT JOIN "app" "collection_app" ON "collection"."id" = "collection_app"."collection_id"
        WHERE (
                "dashboard"."is_app_page" = FALSE
                AND (
                    "dashboard"."archived" = SEARCH_ARCHIVED
                    AND (
                        (lower("dashboard"."name") like SEARCH_TERM)
                        OR (
                            lower("dashboard"."description") like SEARCH_TERM
                        )
                    )
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'page' AS "model",
            "dashboard"."id",
            "dashboard"."name",
            CAST(NULL AS text) AS "display_name",
            "dashboard"."description",
            "dashboard"."archived",
            "dashboard"."collection_id",
            "collection_app"."id" AS "collection_app_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "dashboard"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "dashboard"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "report_dashboard" "dashboard"
            LEFT JOIN "dashboard_bookmark" "bookmark" ON (
                "bookmark"."dashboard_id" = "dashboard"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "collection" "collection" ON "dashboard"."collection_id" = "collection"."id"
            LEFT JOIN "app" "collection_app" ON "collection"."id" = "collection_app"."collection_id"
        WHERE (
                "dashboard"."is_app_page" = TRUE
                AND (
                    "dashboard"."archived" = SEARCH_ARCHIVED
                    AND (
                        (lower("dashboard"."name") like SEARCH_TERM)
                        OR (
                            lower("dashboard"."description") like SEARCH_TERM
                        )
                    )
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'metric' AS "model",
            "metric"."id",
            "metric"."name",
            CAST(NULL AS text) AS "display_name",
            "metric"."description",
            "metric"."archived",
            CAST(NULL AS integer) AS "collection_id",
            CAST(NULL AS integer) AS "collection_app_id",
            CAST(NULL AS text) AS "collection_name",
            CAST(NULL AS text) AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CAST(NULL AS boolean) AS "bookmark",
            "metric"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            "metric"."table_id",
            "table"."db_id" AS "database_id",
            "table"."schema" AS "table_schema",
            "table"."name" AS "table_name",
            "table"."description" AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "metric" "metric"
            LEFT JOIN "metabase_table" "table" ON "metric"."table_id" = "table"."id"
        WHERE (
                "metric"."archived" = SEARCH_ARCHIVED
                AND ((lower("metric"."name") like SEARCH_TERM))
            )
        UNION ALL
        SELECT 'segment' AS "model",
            "segment"."id",
            "segment"."name",
            CAST(NULL AS text) AS "display_name",
            "segment"."description",
            "segment"."archived",
            CAST(NULL AS integer) AS "collection_id",
            CAST(NULL AS integer) AS "collection_app_id",
            CAST(NULL AS text) AS "collection_name",
            CAST(NULL AS text) AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CAST(NULL AS boolean) AS "bookmark",
            "segment"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            "segment"."table_id",
            "table"."db_id" AS "database_id",
            "table"."schema" AS "table_schema",
            "table"."name" AS "table_name",
            "table"."description" AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "segment" "segment"
            LEFT JOIN "metabase_table" "table" ON "segment"."table_id" = "table"."id"
        WHERE (
                "segment"."archived" = SEARCH_ARCHIVED
                AND ((lower("segment"."name") like SEARCH_TERM))
            )
        UNION ALL
        SELECT 'card' AS "model",
            "card"."id",
            "card"."name",
            CAST(NULL AS text) AS "display_name",
            "card"."description",
            "card"."archived",
            "card"."collection_id",
            "collection_app"."id" AS "collection_app_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "card"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "card"."updated_at",
            (
                SELECT count(*)
                FROM "report_dashboardcard"
                WHERE "report_dashboardcard"."card_id" = "card"."id"
            ) AS "dashboardcard_count",
            "card"."dataset_query",
            (
                SELECT "status"
                FROM "moderation_review"
                WHERE (
                        "moderated_item_type" = SEARCH_TERM
                        AND "moderated_item_id" = "card"."id"
                        AND "most_recent" = TRUE
                    )
                ORDER BY "id" DESC
                LIMIT 1
            ) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "report_card" "card"
            LEFT JOIN "card_bookmark" "bookmark" ON (
                "bookmark"."card_id" = "card"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "collection" "collection" ON "card"."collection_id" = "collection"."id"
            LEFT JOIN "app" "collection_app" ON "collection"."id" = "collection_app"."collection_id"
        WHERE (
                "card"."dataset" = FALSE
                AND (
                    "card"."archived" = SEARCH_ARCHIVED
                    AND (
                        (lower("card"."name") like SEARCH_TERM)
                        OR (
                            "card"."query_type" = SEARCH_TERM
                            AND (lower("card"."dataset_query") like SEARCH_TERM)
                        )
                        OR (lower("card"."description") like SEARCH_TERM)
                    )
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'dataset' AS "model",
            "card"."id",
            "card"."name",
            CAST(NULL AS text) AS "display_name",
            "card"."description",
            "card"."archived",
            "card"."collection_id",
            "collection_app"."id" AS "collection_app_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "card"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "card"."updated_at",
            (
                SELECT count(*)
                FROM "report_dashboardcard"
                WHERE "report_dashboardcard"."card_id" = "card"."id"
            ) AS "dashboardcard_count",
            "card"."dataset_query",
            (
                SELECT "status"
                FROM "moderation_review"
                WHERE (
                        "moderated_item_type" = SEARCH_TERM
                        AND "moderated_item_id" = "card"."id"
                        AND "most_recent" = TRUE
                    )
                ORDER BY "id" DESC
                LIMIT 1
            ) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "report_card" "card"
            LEFT JOIN "card_bookmark" "bookmark" ON (
                "bookmark"."card_id" = "card"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "collection" "collection" ON "card"."collection_id" = "collection"."id"
            LEFT JOIN "app" "collection_app" ON "collection"."id" = "collection_app"."collection_id"
        WHERE (
                "card"."dataset" = TRUE
                AND (
                    "card"."archived" = SEARCH_ARCHIVED
                    AND (
                        (lower("card"."name") like SEARCH_TERM)
                        OR (
                            "card"."query_type" = SEARCH_TERM
                            AND (lower("card"."dataset_query") like SEARCH_TERM)
                        )
                        OR (lower("card"."description") like SEARCH_TERM)
                    )
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'collection' AS "model",
            "collection"."id",
            "collection"."name",
            CAST(NULL AS text) AS "display_name",
            "collection"."description",
            "collection"."archived",
            "collection"."id" AS "collection_id",
            "app"."id" AS "collection_app_id",
            "name" AS "collection_name",
            "authority_level" AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            CAST(NULL AS timestamp) AS "updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            "app"."id" AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "collection" "collection"
            LEFT JOIN "collection_bookmark" "bookmark" ON (
                "bookmark"."collection_id" = "collection"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "app" "app" ON "app"."collection_id" = "collection"."id"
        WHERE (
                "app"."id" IS NULL
                AND (
                    "collection"."archived" = SEARCH_ARCHIVED
                    AND ((lower("collection"."name") like SEARCH_TERM))
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'app' AS "model",
            "collection"."id",
            "collection"."name",
            CAST(NULL AS text) AS "display_name",
            "collection"."description",
            "collection"."archived",
            "collection"."id" AS "collection_id",
            "app"."id" AS "collection_app_id",
            "name" AS "collection_name",
            "authority_level" AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            CAST(NULL AS timestamp) AS "updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            "app"."id" AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "collection" "collection"
            LEFT JOIN "collection_bookmark" "bookmark" ON (
                "bookmark"."collection_id" = "collection"."id"
                AND "bookmark"."user_id" = USER_ID
            )
            LEFT JOIN "app" "app" ON "app"."collection_id" = "collection"."id"
        WHERE (
                "app"."id" IS NOT NULL
                AND (
                    "collection"."archived" = SEARCH_ARCHIVED
                    AND ((lower("collection"."name") like SEARCH_TERM))
                )
                AND TRUE
                AND "collection"."namespace" IS NULL
            )
        UNION ALL
        SELECT 'table' AS "model",
            "table"."id",
            "table"."name",
            "table"."display_name",
            "table"."description",
            CAST(NULL AS boolean) AS "archived",
            CAST(NULL AS integer) AS "collection_id",
            CAST(NULL AS integer) AS "collection_app_id",
            CAST(NULL AS text) AS "collection_name",
            CAST(NULL AS text) AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CAST(NULL AS boolean) AS "bookmark",
            "table"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            "id" AS "table_id",
            "db_id" AS "database_id",
            "schema" AS "table_schema",
            "name" AS "table_name",
            "description" AS "table_description",
            "table"."initial_sync_status"
        FROM "metabase_table" "table"
        WHERE (
                (
                    "table"."active" = TRUE
                    AND "table"."visibility_type" IS NULL
                )
                AND (
                    (lower("table"."name") like SEARCH_TERM)
                    OR (lower("table"."display_name") like SEARCH_TERM)
                )
            )
        UNION ALL
        SELECT 'pulse' AS "model",
            "pulse"."id",
            "pulse"."name",
            CAST(NULL AS text) AS "display_name",
            CAST(NULL AS text) AS "description",
            CAST(NULL AS boolean) AS "archived",
            "pulse"."collection_id",
            "collection_app"."id" AS "collection_app_id",
            "collection"."name" AS "collection_name",
            CAST(NULL AS text) AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CAST(NULL AS boolean) AS "bookmark",
            CAST(NULL AS timestamp) AS "updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            CAST(NULL AS text) AS "initial_sync_status"
        FROM "pulse" "pulse"
            LEFT JOIN "collection" "collection" ON "pulse"."collection_id" = "collection"."id"
            LEFT JOIN "app" "collection_app" ON "collection"."id" = "collection_app"."collection_id"
        WHERE (
                "pulse"."archived" = SEARCH_ARCHIVED
                AND ((lower("pulse"."name") like SEARCH_TERM))
                AND TRUE
                AND "collection"."namespace" IS NULL
                AND "alert_condition" IS NULL
                AND "pulse"."dashboard_id" IS NULL
            )
        UNION ALL
        SELECT 'database' AS "model",
            "database"."id",
            "database"."name",
            CAST(NULL AS text) AS "display_name",
            "database"."description",
            CAST(NULL AS boolean) AS "archived",
            CAST(NULL AS integer) AS "collection_id",
            CAST(NULL AS integer) AS "collection_app_id",
            CAST(NULL AS text) AS "collection_name",
            CAST(NULL AS text) AS "collection_authority_level",
            CAST(NULL AS integer) AS "collection_position",
            CAST(NULL AS boolean) AS "bookmark",
            "database"."updated_at",
            CAST(NULL AS integer) AS "dashboardcard_count",
            CAST(NULL AS text) AS "dataset_query",
            CAST(NULL AS text) AS "moderated_status",
            CAST(NULL AS integer) AS "app_id",
            CAST(NULL AS integer) AS "table_id",
            CAST(NULL AS integer) AS "database_id",
            CAST(NULL AS text) AS "table_schema",
            CAST(NULL AS text) AS "table_name",
            CAST(NULL AS text) AS "table_description",
            "database"."initial_sync_status"
        FROM "metabase_database" "database"
        WHERE (
                1 = 1
                AND (
                    (lower("database"."name") like SEARCH_TERM)
                    OR (lower("database"."description") like SEARCH_TERM)
                )
            )
    ) "alias_is_required_by_sql_but_not_needed_here"
CONDITIONS
ORDER BY CASE
        WHEN (lower("model") like SEARCH_TERM) THEN 0
        WHEN (lower("name") like SEARCH_TERM) THEN 0
        WHEN (lower("display_name") like SEARCH_TERM) THEN 0
        WHEN (lower("description") like SEARCH_TERM) THEN 0
        WHEN (lower("collection_name") like SEARCH_TERM) THEN 0
        WHEN (lower("dataset_query") like SEARCH_TERM) THEN 0
        WHEN (lower("table_schema") like SEARCH_TERM) THEN 0
        WHEN (lower("table_name") like SEARCH_TERM) THEN 0
        WHEN (lower("table_description") like SEARCH_TERM) THEN 0
        ELSE 1
    END
LIMIT QUERY_LIMIT OFFSET QUERY_OFFSET