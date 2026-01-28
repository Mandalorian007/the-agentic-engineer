const DISCORD_WEBHOOK =
  "https://discord.com/api/webhooks/1466077484528304301/g9gPCeKrwKqNbI_ep81vYg7B1-9nTOofFwaP9CRhhP04JYU62vTwv7gFrTmoie3VlM3w";

export async function POST(request: Request) {
  const { email } = await request.json();

  if (!email || typeof email !== "string") {
    return Response.json({ ok: false, error: "Email required" }, { status: 400 });
  }

  try {
    await fetch(DISCORD_WEBHOOK, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: `📬 **New waitlist signup**\n${email}`,
      }),
    });

    return Response.json({ ok: true });
  } catch {
    return Response.json({ ok: false, error: "Failed to submit" }, { status: 500 });
  }
}
