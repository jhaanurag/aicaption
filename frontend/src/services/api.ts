import type { CaptionRequest, User } from "../typings";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

function token() {
  return localStorage.getItem("token") || "";
}

async function request(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token()}`,
      ...(options.headers || {})
    }
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

export const api = {
  sendOtp: (email_id: string) =>
    request("/auth/submit-email", {
      method: "POST",
      body: JSON.stringify({ email_id })
    }),

  verifyOtp: (email_id: string, otp: string) =>
    request("/auth/submit-otp", {
      method: "POST",
      body: JSON.stringify({ email_id, otp })
    }),

  me: () => request("/users/me") as Promise<User>,

  users: (isActive?: string) => {
    const query = isActive ? `?is_active=${isActive}` : "";
    return request(`/users${query}`) as Promise<{ users: User[] }>;
  },

  createUser: (data: Partial<User>) =>
    request("/users", {
      method: "POST",
      body: JSON.stringify(data)
    }),

  updateUser: (email: string, data: Partial<User> & { email_id: string }) =>
    request(`/users/${email}`, {
      method: "PATCH",
      body: JSON.stringify(data)
    }),

  deactivateUser: (email: string) =>
    request(`/users/${email}/deactivate`, {
      method: "PATCH"
    }),

  credits: () => request("/captions/credits") as Promise<{ max_ai_credits: number }>,

  generateCaption: (product_description: string, campaign_tone: string) =>
    request("/captions/generate", {
      method: "POST",
      body: JSON.stringify({ product_description, campaign_tone })
    }) as Promise<{ generated_caption: string }>,

  submitRequest: (data: {
    product_description: string;
    campaign_tone: string;
    generated_caption: string;
  }) =>
    request("/captions/approval-requests", {
      method: "POST",
      body: JSON.stringify(data)
    }) as Promise<CaptionRequest>,

  myRequests: () => request("/captions/my-requests") as Promise<{ requests: CaptionRequest[] }>,

  approvalRequests: (requestedBy?: string, status = "PENDING") => {
    const params = new URLSearchParams();
    if (requestedBy) params.set("requested_by", requestedBy);
    if (status) params.set("request_status", status);
    return request(`/captions/approval-requests?${params}`) as Promise<{ requests: CaptionRequest[] }>;
  },

  reviewRequest: (request_id: string, status: string, reason = "") =>
    request("/captions/approval-requests/review", {
      method: "POST",
      body: JSON.stringify({ request_id, status, reason })
    })
};
