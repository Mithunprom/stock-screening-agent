export function billingConfig() {
  return {
    publishableKey: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "",
    priceResearchPro: process.env.STRIPE_PRICE_RESEARCH_PRO || "",
    priceTeam: process.env.STRIPE_PRICE_TEAM || ""
  };
}

export function billingReady() {
  const config = billingConfig();
  return Boolean(config.publishableKey && config.priceResearchPro);
}
