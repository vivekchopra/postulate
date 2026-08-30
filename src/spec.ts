import { z } from "zod";

export const ScenarioSchema = z.object({
  name: z.string().min(1),
  given: z.record(z.any()).optional().default({}),
  when: z.record(z.any()).optional().default({}),
  then: z.record(z.any()).optional().default({})
});

export const PostulateSchema = z.object({
  feature: z.string().min(1),
  owner: z.string().optional(),
  risk: z.enum(["low", "medium", "high", "critical"]).optional().default("medium"),
  contract: z.object({
    preconditions: z.array(z.string()).min(1),
    postconditions: z.array(z.string()).min(1),
    failure_cases: z.array(z.string()).optional().default([])
  }),
  invariants: z.array(z.string()).optional().default([]),
  bdd: z.array(ScenarioSchema).min(1),
  policies: z.array(z.string()).optional().default([]),
  test_mapping: z.record(z.string()).optional().default({}),
  correctness_argument: z.string().optional()
});

export type PostulateSpec = z.infer<typeof PostulateSchema>;
export type Scenario = z.infer<typeof ScenarioSchema>;
