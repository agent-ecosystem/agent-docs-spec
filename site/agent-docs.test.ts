import { describeAgentDocsPerCheck } from 'afdocs/helpers';

// The spec is served as per-category pages (12+ pages vs the old 3), so a
// polite full scan takes longer than the helper's 120s default.
describeAgentDocsPerCheck(undefined, 360_000);
