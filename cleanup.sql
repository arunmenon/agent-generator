
ALTER TABLE crew_metadata ADD COLUMN domain TEXT DEFAULT '';
ALTER TABLE crew_metadata ADD COLUMN problem_context TEXT DEFAULT '';
ALTER TABLE crew_metadata ADD COLUMN input_context TEXT DEFAULT '';
ALTER TABLE crew_metadata ADD COLUMN output_context TEXT DEFAULT '';
ALTER TABLE crew_metadata ADD COLUMN input_schema TEXT DEFAULT '{}';
ALTER TABLE crew_metadata ADD COLUMN output_schema TEXT DEFAULT '{}';
ALTER TABLE agent ADD COLUMN backstory TEXT DEFAULT '';
ALTER TABLE agent ADD COLUMN tools TEXT DEFAULT '[]';
ALTER TABLE agent ADD COLUMN allow_delegation BOOLEAN DEFAULT 1;

