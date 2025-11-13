import { z } from "zod";

// Document Types (5 types as per classification requirements)
export const DOCUMENT_TYPES = [
  "COMPLETE BLOOD COUNT",
  "BASIC METABOLIC PANEL",
  "X-RAY",
  "CT",
  "CLINICAL NOTE"
] as const;

export type DocumentType = typeof DOCUMENT_TYPES[number];

// ICD-10 Code
export const icd10CodeSchema = z.object({
  code: z.string(),
  description: z.string(),
  confidence: z.number().min(0).max(1),
  evidence: z.array(z.string()),
});

export type ICD10Code = z.infer<typeof icd10CodeSchema>;

// Classification Result
export const classificationSchema = z.object({
  document_type: z.enum(DOCUMENT_TYPES),
  confidence: z.number().min(0).max(1),
  rationale: z.string(),
  evidence: z.array(z.string()),
});

export type Classification = z.infer<typeof classificationSchema>;

// Summary Result
export const summarySchema = z.object({
  summary: z.string(),
  confidence: z.number().min(0).max(1),
  evidence: z.array(z.string()),
});

export type Summary = z.infer<typeof summarySchema>;

// Combined Pipeline Result
export const pipelineResultSchema = z.object({
  classification: classificationSchema,
  codes: z.object({
    codes: z.array(icd10CodeSchema),
  }),
  summary: summarySchema,
});

export type PipelineResult = z.infer<typeof pipelineResultSchema>;

// Document
export const documentSchema = z.object({
  id: z.number(),
  original_filename: z.string(),
  created_at: z.string(),
  local_path: z.string().optional(),
});

export type Document = z.infer<typeof documentSchema>;

// Document with Results
export const documentWithResultsSchema = documentSchema.extend({
  results: pipelineResultSchema.optional(),
});

export type DocumentWithResults = z.infer<typeof documentWithResultsSchema>;

// API Responses
export const uploadResponseSchema = z.object({
  document_id: z.number(),
  processed: z.boolean(),
  results: pipelineResultSchema.optional(),
});

export type UploadResponse = z.infer<typeof uploadResponseSchema>;

// Request schemas
export const classifyRequestSchema = z.object({
  document_text: z.string(),
});

export const extractCodesRequestSchema = z.object({
  document_text: z.string(),
  document_type: z.enum(DOCUMENT_TYPES).optional(),
});

export const summarizeRequestSchema = z.object({
  document_text: z.string(),
  document_type: z.enum(DOCUMENT_TYPES).optional(),
  codes: z.array(icd10CodeSchema).optional(),
});

// User schemas
export const userSchema = z.object({
  id: z.string(),
  username: z.string(),
  password: z.string(),
});

export type User = z.infer<typeof userSchema>;

export const insertUserSchema = userSchema.omit({ id: true });

export type InsertUser = z.infer<typeof insertUserSchema>;
