-- PostgreSQL reference schema; apply only after reviewing with your DBA.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TYPE call_channel_type AS ENUM ('VOICE_WEBPHONE', 'VOIP_SIP_TRUNK', 'WHATSAPP_VOICE');
CREATE TYPE lead_stage_type AS ENUM ('NEW', 'CONTACTED', 'DEMO_SCHEDULED', 'PROPOSAL_SENT', 'WON_CLOSED');
CREATE TABLE tenants (
  tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_name VARCHAR(255) NOT NULL,
  industry_type VARCHAR(100) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE agent_configs (
  config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  pod_role VARCHAR(50) NOT NULL,
  channel_type call_channel_type NOT NULL DEFAULT 'VOIP_SIP_TRUNK',
  voice_model VARCHAR(50) NOT NULL DEFAULT 'af_heart',
  system_prompt TEXT NOT NULL,
  brevity_limit INT NOT NULL DEFAULT 18 CHECK (brevity_limit BETWEEN 1 AND 50),
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  UNIQUE (tenant_id, pod_role)
);
CREATE TABLE leads_crm (
  lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  full_name VARCHAR(255) NOT NULL,
  phone_number VARCHAR(50) NOT NULL,
  company_name VARCHAR(255),
  service_inquired VARCHAR(255),
  estimated_value NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (estimated_value >= 0),
  stage lead_stage_type NOT NULL DEFAULT 'NEW',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE agent_performance_logs (
  log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
  call_id VARCHAR(100) NOT NULL,
  pod_role VARCHAR(50) NOT NULL,
  latency_ms NUMERIC(8,2),
  word_count INT,
  cost_per_minute NUMERIC(8,4),
  transcript TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads_crm ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_performance_logs ENABLE ROW LEVEL SECURITY;
-- Set app.current_tenant_id only from trusted server-side transaction code.
CREATE POLICY tenant_isolation_policy ON tenants
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
CREATE POLICY config_isolation_policy ON agent_configs
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
CREATE POLICY crm_isolation_policy ON leads_crm
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
CREATE POLICY logs_isolation_policy ON agent_performance_logs
  USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid)
  WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
