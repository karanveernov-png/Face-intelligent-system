import type {
  AnalyzeImageResponse,
  AnalyzeVideoResponse,
  EnrollResponse,
  EnrolledEntry,
  ModelStatus,
  AnalyzeOptions,
} from "../types/api";

const API_KEY = import.meta.env.VITE_API_KEY as string | undefined;

function authenticatedHeaders(): HeadersInit {
  if (!API_KEY) {
    throw new Error("VITE_API_KEY is not configured for this frontend build.");
  }
  return { "X-API-Key": API_KEY };
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // response body wasn't JSON -- fall back to statusText, already set above
    }
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export async function getHealth(): Promise<{ status: string; version: string }> {
  const res = await fetch("/health");
  return parseOrThrow(res);
}

export async function getModelsStatus(): Promise<ModelStatus[]> {
  const res = await fetch("/api/models/status");
  return parseOrThrow(res);
}

export async function analyzeImage(
  file: File,
  options: AnalyzeOptions
): Promise<AnalyzeImageResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("run_recognition", String(options.run_recognition));
  form.append("run_expression", String(options.run_expression));
  form.append("run_age", String(options.run_age));
  const res = await fetch("/api/analyze/image", {
    method: "POST",
    headers: authenticatedHeaders(),
    body: form,
  });
  return parseOrThrow(res);
}

export async function analyzeVideo(
  file: File,
  options: AnalyzeOptions
): Promise<AnalyzeVideoResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("run_recognition", String(options.run_recognition));
  form.append("run_expression", String(options.run_expression));
  form.append("run_age", String(options.run_age));
  const res = await fetch("/api/analyze/video", {
    method: "POST",
    headers: authenticatedHeaders(),
    body: form,
  });
  return parseOrThrow(res);
}

export async function enrollFace(
  file: File,
  name: string,
  consentConfirmed: boolean
): Promise<EnrollResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("name", name);
  form.append("consent_confirmed", String(consentConfirmed));
  const res = await fetch("/api/faces/enroll", {
    method: "POST",
    headers: authenticatedHeaders(),
    body: form,
  });
  return parseOrThrow(res);
}

export async function listFaces(): Promise<EnrolledEntry[]> {
  const res = await fetch("/api/faces", { headers: authenticatedHeaders() });
  return parseOrThrow(res);
}

export async function deleteFace(faceId: string): Promise<void> {
  const res = await fetch(`/api/faces/${encodeURIComponent(faceId)}`, {
    method: "DELETE",
    headers: authenticatedHeaders(),
  });
  await parseOrThrow(res);
}

export { ApiError };