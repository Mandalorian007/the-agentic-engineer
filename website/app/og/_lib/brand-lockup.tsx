type Props = {
  logo: string;
  color?: string;
  size?: number;
  fontSize?: number;
};

export function BrandLockup({
  logo,
  color = "#ffffff",
  size = 60,
  fontSize = 22,
}: Props) {
  return (
    <div style={{ display: "flex", alignItems: "center" }}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={logo} alt="" width={size} height={size} />
      <div
        style={{
          display: "flex",
          marginLeft: 18,
          fontSize,
          fontWeight: 700,
          color,
          letterSpacing: "0.22em",
        }}
      >
        THE AGENTIC ENGINEER
      </div>
    </div>
  );
}
