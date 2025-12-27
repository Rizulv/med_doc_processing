import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppHeader } from "@/components/AppHeader";
import LandingPage from "@/pages/LandingPage";
import UploadPage from "@/pages/UploadPage";
import DocumentsPage from "@/pages/DocumentsPage";
import DocumentDetailPage from "@/pages/DocumentDetailPage";
import EvalReportPage from "@/pages/EvalReportPage";
import AboutPage from "@/pages/AboutPage";
import DemoPage from "@/pages/DemoPage";
import NotFound from "@/pages/not-found";

function Router() {
  return (
    <Switch>
      <Route path="/" component={LandingPage} />
      <Route path="/upload" component={UploadPage} />
      <Route path="/about" component={AboutPage} />
      <Route path="/demo" component={DemoPage} />
      <Route path="/eval-report" component={EvalReportPage} />
      <Route path="/documents" component={DocumentsPage} />
      <Route path="/documents/:id" component={DocumentDetailPage} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AppHeader />
        <Router />
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
