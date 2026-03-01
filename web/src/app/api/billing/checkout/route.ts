import { NextResponse } from "next/server";

import { billingConfig, billingReady } from "@/lib/server/billing";

export async function POST() {
  if (!billingReady()) {
    return NextResponse.json(
      {
        ok: false,
        message: "Stripe is not configured yet. This endpoint is scaffolding only."
      },
      { status: 501 }
    );
  }
  return NextResponse.json({
    ok: false,
    message: "Stripe checkout scaffolding is present, but live billing has not been wired yet.",
    config: billingConfig()
  });
}
