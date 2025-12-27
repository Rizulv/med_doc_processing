import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";

export function AppHeader() {
  const [location] = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between max-w-7xl">
        <Link href="/">
          <div className="flex items-center gap-3 cursor-pointer group">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
                <span className="text-white font-bold text-sm">MD</span>
              </div>
              <span className="font-semibold text-xl text-slate-900 group-hover:text-blue-600 transition-colors">
                Medical Doc Intelligence
              </span>
            </div>
          </div>
        </Link>

        <nav className="flex items-center gap-1">
          <Link href="/upload">
            <Button
              variant={location === "/upload" ? "default" : "ghost"}
              size="default"
              className="font-medium"
            >
              Upload
            </Button>
          </Link>
          <Link href="/about">
            <Button
              variant={location === "/about" ? "default" : "ghost"}
              size="default"
              className="font-medium"
            >
              Features
            </Button>
          </Link>
          <Link href="/demo">
            <Button
              variant={location === "/demo" ? "default" : "ghost"}
              size="default"
              className="font-medium"
            >
              Demo
            </Button>
          </Link>
          <Link href="/documents">
            <Button
              variant={location.startsWith("/documents") ? "default" : "ghost"}
              size="default"
              data-testid="link-documents"
              className="font-medium"
            >
              Documents
            </Button>
          </Link>
          <Link href="/eval-report">
            <Button
              variant={location === "/eval-report" ? "default" : "ghost"}
              size="default"
              data-testid="link-eval-report"
              className="font-medium"
            >
              Evaluation
            </Button>
          </Link>
        </nav>
      </div>
    </header>
  );
}
