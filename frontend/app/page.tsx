import Twin from '@/components/twin';

export default function Home() {
  return (
    <main
      className="min-h-screen bg-cover bg-center bg-no-repeat bg-fixed"
      style={{ backgroundImage: "url('/background_image.jpg')" }}
    >
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="flex justify-center mb-2">
            <img
              src="/reanblock-logo-horizontal.png"
              alt="Reanblock"
              className="h-16 w-auto"
            />
          </h1>
          <p className="text-center text-white mb-8">
            Digital Twin
          </p>

          <div className="h-[600px]">
            <Twin />
          </div>

          <footer className="mt-8 text-center text-sm text-gray-500">
            <nav className="p-4">
              <div className="container mx-auto mt-1 flex flex-wrap items-center justify-between gap-4">
                <p className="text-white mt-1">@ 2026 Reanblock: LLM Engineer and Security Researcher</p>
                <ul className="flex gap-4 ml-auto">
                  <li>
                    <a className="text-white" href="https://reanblock.com" target="_blank" rel="noopener noreferrer">Home</a>
                  </li>
                  <li>
                    <a className="text-white" href="https://www.youtube.com/channel/UCsec5JlNrA02iT4826EazTw" target="_blank" rel="noopener noreferrer">Tutorials</a>
                  </li>
                  <li>
                    <a className="text-white" href="https://github.com/reanblock/reanblock-audit-reports" target="_blank" rel="noopener noreferrer">Audits</a>
                  </li>
                  <li>
                    <a className="text-white" href="https://www.linkedin.com/in/jensendarren1" target="_blank" rel="noopener noreferrer">LinkedIn</a>
                  </li>
                </ul>
              </div>
            </nav>
          </footer>
        </div>
      </div>


    </main>
  );
}