import { getQuote } from "@/lib/server/research-store";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const tickers = (searchParams.get("tickers") ?? "")
    .split(",")
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean)
    .slice(0, 8);

  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      let closed = false;
      const emit = async () => {
        if (closed) {
          return;
        }
        const quotes = await Promise.all(tickers.map((ticker) => getQuote(ticker)));
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ quotes })}\n\n`));
      };

      await emit();
      const timer = setInterval(emit, 10000);

      request.signal.addEventListener("abort", () => {
        closed = true;
        clearInterval(timer);
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive"
    }
  });
}
