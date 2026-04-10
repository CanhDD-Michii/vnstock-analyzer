import { redirect } from "next/navigation";
import { ROUTES } from "@/constants/routes";

/** Không còn trang dashboard — chuyển thẳng tới danh sách cổ phiếu. */
export default function DashboardRedirectPage() {
  redirect(ROUTES.stocks);
}
