import { useState } from "react";

export default function DevinInfoModal() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[13px] font-medium text-gray-500 hover:text-gray-700 hover:bg-gray-50 transition-colors"
      >
        <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
        How It Works
      </button>

      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="bg-white border border-gray-200 rounded-xl max-w-lg w-full mx-4 p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-bold text-gray-900">How SecureFlow Works</h2>
              <button onClick={() => setOpen(false)} className="text-gray-400 hover:text-gray-600 text-lg leading-none">&times;</button>
            </div>
            <div className="space-y-5 text-[13px] text-gray-600">
              <div>
                <h3 className="text-blue-700 font-semibold text-xs uppercase tracking-wider mb-1.5">Why Devin?</h3>
                <p className="leading-relaxed">
                  Unlike code suggestion tools, Devin is a <strong className="text-gray-900">full autonomous software engineer</strong>.
                  It clones your repository, understands the codebase context, implements fixes, runs your test suite, and opens pull requests
                  all in an isolated environment that can&apos;t affect your main branch.
                </p>
              </div>
              <div>
                <h3 className="text-blue-700 font-semibold text-xs uppercase tracking-wider mb-1.5">The Pipeline</h3>
                <ol className="list-decimal list-inside space-y-1 text-gray-500 text-[12px]">
                  <li>CodeQL scans detect vulnerabilities automatically</li>
                  <li>SecureFlow triages findings by CWE type and severity</li>
                  <li>Standard vulnerabilities are dispatched to Devin</li>
                  <li>Complex issues are escalated to engineers</li>
                  <li>Devin creates PRs with targeted, minimal fixes</li>
                  <li>Confidence scoring helps reviewers prioritize</li>
                  <li>If a fix is rejected, Devin retries with feedback</li>
                </ol>
              </div>
              <div>
                <h3 className="text-blue-700 font-semibold text-xs uppercase tracking-wider mb-1.5">Closing the Loop</h3>
                <p className="leading-relaxed">
                  Security teams see findings remediated in hours, not months. Engineering teams review PRs instead of
                  writing fixes from scratch. Compliance gets an audit trail of every action. Nobody has to babysit the process.
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4">
                <p className="text-[9px] text-gray-400 uppercase font-bold tracking-widest mb-1">Powered by</p>
                <p className="text-gray-900 font-semibold text-sm">Devin by Cognition: The first AI Software Engineer</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
