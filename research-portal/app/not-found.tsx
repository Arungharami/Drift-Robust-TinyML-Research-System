import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container">
      <div className="section-label">404</div>
      <h1>Page not found</h1>
      <p className="lede">
        This route does not exist. Return to <Link href="/">the homepage</Link> or browse{" "}
        <Link href="/pipeline">the pipeline</Link>.
      </p>
    </div>
  );
}
