export type Role = "ADMIN" | "USER";
export type RequestStatus = "PENDING" | "APPROVED" | "REJECTED";

export interface User {
  id?: string;
  email_id: string;
  first_name: string;
  last_name: string;
  role: Role;
  max_ai_credits: number;
  is_active: boolean;
}

export interface CaptionRequest {
  id: string;
  requested_by: string;
  product_description: string;
  campaign_tone: string;
  generated_caption: string;
  request_status: RequestStatus;
  request_reject_reason: string;
  created_at: string;
}
