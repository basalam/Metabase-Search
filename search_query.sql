SELECT *
FROM (
        SELECT 'dashboard' AS "model",
            "dashboard"."id",
            "dashboard"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "dashboard"."description",
            "dashboard"."archived",
            "dashboard"."collection_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "dashboard"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "dashboard"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            CAST(NULL AS INTEGER) AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "report_dashboard" AS "dashboard"
            LEFT JOIN "dashboard_bookmark" AS "bookmark" ON ("bookmark"."dashboard_id" = "dashboard"."id")
            AND ("bookmark"."user_id" = USER_ID)
            LEFT JOIN "collection" AS "collection" ON "dashboard"."collection_id" = "collection"."id"
        WHERE ("dashboard"."archived" = FALSE)
            AND (
                (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (LOWER("dashboard"."name") LIKE SEARCH_TERM)
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
                OR (
                    LOWER("dashboard"."description") LIKE SEARCH_TERM
                )
            )
            AND TRUE
            AND ("collection"."namespace" IS NULL)
        UNION ALL
        SELECT 'metric' AS "model",
            "metric"."id",
            "metric"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "metric"."description",
            "metric"."archived",
            CAST(NULL AS INTEGER) AS "collection_id",
            CAST(NULL AS TEXT) AS "collection_name",
            CAST(NULL AS TEXT) AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CAST(NULL AS BOOLEAN) AS "bookmark",
            "metric"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            "metric"."table_id",
            "table"."schema" AS "table_schema",
            "table"."name" AS "table_name",
            "table"."description" AS "table_description",
            "table"."db_id" AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "metric" AS "metric"
            LEFT JOIN "metabase_table" AS "table" ON "metric"."table_id" = "table"."id"
        WHERE ("metric"."archived" = FALSE)
            AND (
                (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
                OR (LOWER("metric"."name") LIKE SEARCH_TERM)
            )
        UNION ALL
        SELECT 'segment' AS "model",
            "segment"."id",
            "segment"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "segment"."description",
            "segment"."archived",
            CAST(NULL AS INTEGER) AS "collection_id",
            CAST(NULL AS TEXT) AS "collection_name",
            CAST(NULL AS TEXT) AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CAST(NULL AS BOOLEAN) AS "bookmark",
            "segment"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            "segment"."table_id",
            "table"."schema" AS "table_schema",
            "table"."name" AS "table_name",
            "table"."description" AS "table_description",
            "table"."db_id" AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "segment" AS "segment"
            LEFT JOIN "metabase_table" AS "table" ON "segment"."table_id" = "table"."id"
        WHERE ("segment"."archived" = FALSE)
            AND (
                (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
                OR (LOWER("segment"."name") LIKE SEARCH_TERM)
            )
        UNION ALL
        SELECT 'card' AS "model",
            "card"."id",
            "card"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "card"."description",
            "card"."archived",
            "card"."collection_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "card"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "card"."updated_at",
            (
                SELECT COUNT(*)
                FROM "report_dashboardcard"
                WHERE "report_dashboardcard"."card_id" = "card"."id"
            ) AS "dashboardcard_count",
            (
                SELECT "status"
                FROM "moderation_review"
                WHERE ("moderated_item_type" = SEARCH_TERM)
                    AND ("moderated_item_id" = "card"."id")
                    AND ("most_recent" = TRUE)
                ORDER BY "id" DESC
                LIMIT 1
            ) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            CAST(NULL AS INTEGER) AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            "card"."dataset_query"
        FROM "report_card" AS "card"
            LEFT JOIN "card_bookmark" AS "bookmark" ON ("bookmark"."card_id" = "card"."id")
            AND ("bookmark"."user_id" = USER_ID)
            LEFT JOIN "collection" AS "collection" ON "card"."collection_id" = "collection"."id"
        WHERE ("card"."dataset" = FALSE)
            AND (
                ("card"."archived" = FALSE)
                AND (
                    (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                )
            )
            AND TRUE
            AND ("collection"."namespace" IS NULL)
        UNION ALL
        SELECT 'dataset' AS "model",
            "card"."id",
            "card"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "card"."description",
            "card"."archived",
            "card"."collection_id",
            "collection"."name" AS "collection_name",
            "collection"."authority_level" AS "collection_authority_level",
            "card"."collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            "card"."updated_at",
            (
                SELECT COUNT(*)
                FROM "report_dashboardcard"
                WHERE "report_dashboardcard"."card_id" = "card"."id"
            ) AS "dashboardcard_count",
            (
                SELECT "status"
                FROM "moderation_review"
                WHERE ("moderated_item_type" = SEARCH_TERM)
                    AND ("moderated_item_id" = "card"."id")
                    AND ("most_recent" = TRUE)
                ORDER BY "id" DESC
                LIMIT 1
            ) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            CAST(NULL AS INTEGER) AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            "card"."dataset_query"
        FROM "report_card" AS "card"
            LEFT JOIN "card_bookmark" AS "bookmark" ON ("bookmark"."card_id" = "card"."id")
            AND ("bookmark"."user_id" = USER_ID)
            LEFT JOIN "collection" AS "collection" ON "card"."collection_id" = "collection"."id"
        WHERE ("card"."dataset" = TRUE)
            AND (
                ("card"."archived" = FALSE)
                AND (
                    (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (LOWER("card"."name") LIKE SEARCH_TERM)
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (
                        ("card"."query_type" = SEARCH_TERM)
                        AND (LOWER("card"."dataset_query") LIKE SEARCH_TERM)
                    )
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                    OR (LOWER("card"."description") LIKE SEARCH_TERM)
                )
            )
            AND TRUE
            AND ("collection"."namespace" IS NULL)
        UNION ALL
        SELECT 'collection' AS "model",
            "collection"."id",
            "collection"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "collection"."description",
            "collection"."archived",
            "collection"."id" AS "collection_id",
            "name" AS "collection_name",
            "authority_level" AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CASE
                WHEN "bookmark"."id" IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS "bookmark",
            CAST(NULL AS TIMESTAMP) AS "updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            CAST(NULL AS INTEGER) AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "collection" AS "collection"
            LEFT JOIN "collection_bookmark" AS "bookmark" ON ("bookmark"."collection_id" = "collection"."id")
            AND ("bookmark"."user_id" = USER_ID)
        WHERE ("collection"."archived" = FALSE)
            AND (
                (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
                OR (LOWER("collection"."name") LIKE SEARCH_TERM)
            )
            AND TRUE
            AND ("collection"."namespace" IS NULL)
        UNION ALL
        SELECT 'table' AS "model",
            "table"."id",
            "table"."name",
            "table"."display_name",
            "table"."description",
            CAST(NULL AS BOOLEAN) AS "archived",
            CAST(NULL AS INTEGER) AS "collection_id",
            CAST(NULL AS TEXT) AS "collection_name",
            CAST(NULL AS TEXT) AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CAST(NULL AS BOOLEAN) AS "bookmark",
            "table"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            "id" AS "table_id",
            "schema" AS "table_schema",
            "name" AS "table_name",
            "description" AS "table_description",
            "db_id" AS "database_id",
            "table"."initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "metabase_table" AS "table"
        WHERE (
                ("table"."active" = TRUE)
                AND ("table"."visibility_type" IS NULL)
            )
            AND (
                (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
                OR (LOWER("table"."display_name") LIKE SEARCH_TERM)
            )
        UNION ALL
        SELECT 'action' AS "model",
            "action"."id",
            "action"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "action"."description",
            "action"."archived",
            "model"."collection_id" AS "collection_id",
            CAST(NULL AS TEXT) AS "collection_name",
            CAST(NULL AS TEXT) AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CAST(NULL AS BOOLEAN) AS "bookmark",
            "action"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            "query_action"."database_id" AS "database_id",
            CAST(NULL AS TEXT) AS "initial_sync_status",
            "model"."id" AS "model_id",
            "model"."name" AS "model_name",
            "query_action"."dataset_query" AS "dataset_query"
        FROM "action" AS "action"
            LEFT JOIN "report_card" AS "model" ON "model"."id" = "action"."model_id"
            LEFT JOIN "query_action" ON "query_action"."action_id" = "action"."id"
            LEFT JOIN "collection" AS "collection" ON "model"."collection_id" = "collection"."id"
        WHERE ("action"."archived" = FALSE)
            AND (
                (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."name") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
                OR (LOWER("action"."description") LIKE SEARCH_TERM)
            )
            AND TRUE
            AND ("collection"."namespace" IS NULL)
        UNION ALL
        SELECT 'database' AS "model",
            "database"."id",
            "database"."name",
            CAST(NULL AS TEXT) AS "display_name",
            "database"."description",
            CAST(NULL AS BOOLEAN) AS "archived",
            CAST(NULL AS INTEGER) AS "collection_id",
            CAST(NULL AS TEXT) AS "collection_name",
            CAST(NULL AS TEXT) AS "collection_authority_level",
            CAST(NULL AS INTEGER) AS "collection_position",
            CAST(NULL AS BOOLEAN) AS "bookmark",
            "database"."updated_at",
            CAST(NULL AS INTEGER) AS "dashboardcard_count",
            CAST(NULL AS TEXT) AS "moderated_status",
            CAST(NULL AS INTEGER) AS "table_id",
            CAST(NULL AS TEXT) AS "table_schema",
            CAST(NULL AS TEXT) AS "table_name",
            CAST(NULL AS TEXT) AS "table_description",
            CAST(NULL AS INTEGER) AS "database_id",
            "database"."initial_sync_status",
            CAST(NULL AS INTEGER) AS "model_id",
            CAST(NULL AS TEXT) AS "model_name",
            CAST(NULL AS TEXT) AS "dataset_query"
        FROM "metabase_database" AS "database"
        WHERE 1 = 1
            AND (
                (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."name") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
                OR (LOWER("database"."description") LIKE SEARCH_TERM)
            )
    ) AS "alias_is_required_by_sql_but_not_needed_here" CONDITIONS
ORDER BY CASE
        WHEN LOWER("model") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("name") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("display_name") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("description") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("collection_name") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("table_schema") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("table_name") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("table_description") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("model_name") LIKE SEARCH_TERM THEN 0
        WHEN LOWER("dataset_query") LIKE SEARCH_TERM THEN 0
        ELSE 1
    END ASC
LIMIT QUERY_LIMIT OFFSET QUERY_OFFSET
