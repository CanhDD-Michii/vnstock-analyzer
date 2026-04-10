import { ROUTES } from "@/constants/routes";

/** True when `pathname` should highlight the nav item for `href`. */
export function isNavActive(href: string, pathname: string): boolean {
  if (href === ROUTES.stocks) {
    return pathname === ROUTES.stocks || pathname.startsWith(`${ROUTES.stocks}/`);
  }
  if (href === ROUTES.history) {
    return pathname.startsWith(ROUTES.history);
  }
  if (href === ROUTES.adminUsers) {
    return pathname === ROUTES.adminUsers || pathname.startsWith(`${ROUTES.adminUsers}/`);
  }
  return pathname === href;
}
