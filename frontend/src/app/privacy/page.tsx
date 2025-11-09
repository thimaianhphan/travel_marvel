export const metadata = {
  title: "Privacy | Travel Marvel",
};

export default function PrivacyPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-16 md:py-24">
      <h1 className="text-4xl font-semibold text-slate-900">Privacy</h1>
      <p className="mt-6 text-sm text-slate-600">
        This hackathon preview does not collect personal data. Any production
        launch will outline transparent data practices, including how we handle
        location lookups, consent for analytics, and third-party services.
      </p>
      <p className="mt-4 text-sm text-slate-600">
        For now, all journey data is hardcoded test content so designers can
        iterate on UI/UX direction without needing live inputs.
      </p>
    </div>
  );
}


