CREATE EXTENSION pg_trgm;

CREATE INDEX collection_gin ON public.collection USING gin (name gin_trgm_ops);
CREATE INDEX metabase_database_gin ON public.metabase_database USING gin (name gin_trgm_ops, description gin_trgm_ops);
CREATE INDEX metabase_table_gin ON public.metabase_table USING gin (name gin_trgm_ops, display_name gin_trgm_ops);
CREATE INDEX metricnamex_gin ON public.metric USING gin (name gin_trgm_ops);
CREATE INDEX pulse_gin ON public.pulse USING gin (name gin_trgm_ops);
CREATE INDEX namex_gin ON public.report_card USING gin (name gin_trgm_ops);
CREATE INDEX report_card_gin ON public.report_card USING gin (name gin_trgm_ops, description gin_trgm_ops, dataset_query gin_trgm_ops, query_type gin_trgm_ops);
CREATE INDEX report_dashboard_name_gin ON public.report_dashboard USING gin (name gin_trgm_ops, description gin_trgm_ops);
CREATE INDEX segment_name_gin ON public.segment USING gin (name gin_trgm_ops);
