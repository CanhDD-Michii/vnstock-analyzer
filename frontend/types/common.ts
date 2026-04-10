/** Khớp contract API (CODE_RULES_BE_FE §42) — response thành công. */
export interface ApiSuccessResponse<T> {
  data: T;
  message: string;
}

/** Khớp contract API — response lỗi. */
export interface ApiErrorBody {
  message: string;
  errorCode: string;
}

export interface HealthData {
  status: string;
}

export interface PlaceholderData {
  placeholder: boolean;
}
