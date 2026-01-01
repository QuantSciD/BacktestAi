// frontend/app/api/backtest/route.ts
export const runtime = "nodejs";

export async function POST(req: Request) {
  const formData = await req.formData();

  const res = await fetch("http://localhost:8000/backtest", {
    method: "POST",
    body: formData,
  });

  const data = await res.text();

  if (!res.ok) {
    return new Response(data, { status: res.status });
  }

  return new Response(data, {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
