import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Activity, ClipboardCheck, FolderOpen } from "lucide-react";

export function AppHeader() {
  const [location] = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between max-w-7xl">
        <Link href="/">
          <div className="flex items-center gap-2 cursor-pointer hover-elevate px-2 py-1 rounded-md transition-colors">
            <div className="p-1.5 bg-primary rounded">
              <Activity className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-semibold text-lg">Medical Doc AI</span>
          </div>
        </Link>

        <nav className="flex items-center gap-2">
          <Link href="/eval-report">
            <Button
              variant={location === "/eval-report" ? "default" : "ghost"}
              size="default"
              data-testid="link-eval-report"
            >
              <ClipboardCheck className="w-4 h-4 mr-2" />
              Eval Test Report
            </Button>
          </Link>
          <Link href="/documents">
            <Button
              variant={location.startsWith("/documents") ? "default" : "ghost"}
              size="default"
              data-testid="link-documents"
            >
              <FolderOpen className="w-4 h-4 mr-2" />
              Documents
            </Button>
          </Link>
        </nav>
      </div>
    </header>
  );
}
