/** Đồng bộ ý nghĩa với backend `Settings` / `crawler.constants` (URL, page size, max rounds). */

export const VIETSTOCK_FINANCE_ORIGIN = "https://finance.vietstock.vn";

export const VIETSTOCK_LIST_PRICE_PATH = "/data/GetStockDeal_ListPriceByTimeFrame";

export const VIETSTOCK_DEFAULT_LIST_PRICE_URL = `${VIETSTOCK_FINANCE_ORIGIN}${VIETSTOCK_LIST_PRICE_PATH}`;

export const VIETSTOCK_DEFAULT_PAGE_SIZE = 20;

export const VIETSTOCK_DEFAULT_MAX_ROUNDS = 500;

/** Mã mẫu trong form metadata (curl). */
export const VIETSTOCK_SAMPLE_FORM_STOCK_CODE = "HPG";

/** Giá trị mặc định cho ô ticker trên UI admin. */
export const ADMIN_DEFAULT_STOCK_TICKER = "FPT";

export function createDefaultVietstockCrawlMetadata(): Record<string, unknown> {
  const toDate = new Date().toISOString().slice(0, 10);
  return {
    url: VIETSTOCK_DEFAULT_LIST_PRICE_URL,
    form: {
      stockCode: VIETSTOCK_SAMPLE_FORM_STOCK_CODE,
      timeFrame: "C",
      toDate,
      page: "1",
      pageSize: String(VIETSTOCK_DEFAULT_PAGE_SIZE),
      languageID: "1",
    },
    crawl_strategy: {
      initial_to_date: "today",
      max_rounds: VIETSTOCK_DEFAULT_MAX_ROUNDS,
      page_size: VIETSTOCK_DEFAULT_PAGE_SIZE,
    },
  };
}
