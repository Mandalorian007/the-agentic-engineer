import { ImageResponse } from "next/og";
import { loadInter } from "./_lib/load-fonts";
import { loadLogoDataUri } from "./_lib/load-logo";
import { BrandLockup } from "./_lib/brand-lockup";

export const runtime = "nodejs";

export async function GET() {
  const [fonts, logo] = await Promise.all([
    loadInter([400, 700, 800]),
    loadLogoDataUri(),
  ]);
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: "#0a0e27",
          padding: "60px 100px",
          fontFamily: "Inter",
        }}
      >
        <BrandLockup logo={logo} color="#22d3ee" />
        <div
          style={{
            display: "flex",
            flex: 1,
            flexDirection: "row",
            alignItems: "center",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              fontWeight: 800,
              fontSize: 68,
              lineHeight: 1.04,
              letterSpacing: "-0.035em",
              color: "#ffffff",
              width: 500,
            }}
          >
            <div style={{ display: "flex" }}>More PRs.</div>
            <div style={{ display: "flex" }}>Same features.</div>
          </div>
          <div
            style={{
              display: "flex",
              width: 3,
              height: 240,
              background: "#22d3ee",
              marginLeft: 28,
              marginRight: 44,
            }}
          />
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              fontWeight: 800,
              fontSize: 44,
              lineHeight: 1.12,
              letterSpacing: "-0.025em",
              flex: 1,
            }}
          >
            <div style={{ display: "flex", color: "#ffffff" }}>
              Use AI to ship
            </div>
            <div style={{ display: "flex", color: "#ffffff" }}>
              the roadmap.
            </div>
            <div
              style={{ display: "flex", color: "#22d3ee", marginTop: 16 }}
            >
              Not just merge PRs.
            </div>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            fontSize: 22,
            fontWeight: 400,
            color: "#a5b4fc",
            letterSpacing: "0.01em",
          }}
        >
          Field notes on agentic engineering.
        </div>
      </div>
    ),
    { width: 1200, height: 630, fonts },
  );
}
