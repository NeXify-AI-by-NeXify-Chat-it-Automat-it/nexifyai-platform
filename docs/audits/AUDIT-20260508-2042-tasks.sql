-- AUTO-GENERATED TASKS FROM DOS-v2.1 AUDIT 2026-05-08
-- Insert into Supabase tasks table when connection is available

INSERT INTO tasks (title, context, source, priority, status, assignee, reviewer, affected_systems)
VALUES 
('Health-Score auf >80% bringen (aktuell 70%)', 'Backend nicht erreichbar. Verbindungs-Health 4/8. GitHub SSH, Umami, Traefik down.', 'dos-v2.1-audit', 'critical', 'waiting', 'Hermes', 'Hermes', ARRAY['Backend','Umami','Traefik','GitHub']),
('4 Pflicht-Dokumente erstellen: zielarchitektur-v2, bauplan, rollen-kompendium, license-policy', 'Fehlende Architektur-Dokumentation. DOS v2.1 + nexify-builder verlangen diese.', 'dos-v2.1-audit', 'critical', 'waiting', 'Hermes', 'Hermes', ARRAY['docs']),
('Mock-Code in Agent-Scan-Methoden eliminieren', 'pass in refactor_agent, finops_agent, retrieval_agent Scan-Methoden. return [] in runtime_governance.', 'dos-v2.1-audit', 'high', 'waiting', 'Hermes', 'Hermes', ARRAY['backend/agents','backend/runtime']),
('Gitleaks + Trivy im Container installieren', 'Security-Tools fehlen lokal. Pre-Commit-Checks nicht möglich.', 'dos-v2.1-audit', 'high', 'waiting', 'Hermes', 'Hermes', ARRAY['Container']),
('except:pass in enterprise_health.py fixen', '3 bare except:pass Blöcke verschlucken Exceptions.', 'dos-v2.1-audit', 'medium', 'waiting', 'Hermes', 'Hermes', ARRAY['backend/health']),
('MiniMax-Testreferenzen auf nexify-v4-pro migrieren', 'test_openrouter_migration_iter81.py testet veraltetes Modell.', 'dos-v2.1-audit', 'medium', 'waiting', 'Hermes', 'Hermes', ARRAY['backend/tests']);

-- END
