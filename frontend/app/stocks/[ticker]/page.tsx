import { PageShell } from "@/components/common/PageShell";
import { StockDetailClient } from "@/components/stock/StockDetailClient";
import { ApiClientError } from "@/services/api-client";
import { getStockDetail, getStockPrices } from "@/services/stock.service";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function StockDetailPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = await params;
  try {
    const detail = await getStockDetail(ticker);
    const prices = await getStockPrices(ticker, 400);
    return (
      <PageShell title={`Mã ${detail.ticker}`} description={detail.companyName}>
        <StockDetailClient
          ticker={detail.ticker}
          initialDetail={detail}
          initialPrices={prices}
        />
      </PageShell>
    );
  } catch (e: unknown) {
    if (e instanceof ApiClientError && e.status === 404) {
      notFound();
    }
    throw e;
  }
}
