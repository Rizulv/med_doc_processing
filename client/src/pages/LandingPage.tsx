import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Link } from "wouter";

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-slate-50 to-white py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center space-y-6">
            <div className="inline-block">
              <span className="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                Medical Document Intelligence Platform
              </span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 leading-tight">
              Transform Medical Documents
              <br />
              <span className="text-blue-600">Into Actionable Insights</span>
            </h1>

            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Enterprise-grade AI platform for automated medical document analysis,
              ICD-10 code extraction, and patient-friendly report generation.
            </p>

            <div className="flex gap-4 justify-center pt-4">
              <Link href="/upload">
                <Button size="lg" className="text-lg px-8 py-6">
                  Start Analysis
                </Button>
              </Link>
              <Link href="/about">
                <Button size="lg" variant="outline" className="text-lg px-8 py-6">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Comprehensive Document Processing
            </h2>
            <p className="text-lg text-slate-600">
              Automated analysis and extraction powered by advanced AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-2">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Document Classification
                </h3>
                <p className="text-slate-600">
                  Automatically identify document types including lab reports, imaging studies, and clinical notes with high accuracy.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  ICD-10 Code Extraction
                </h3>
                <p className="text-slate-600">
                  Extract diagnosis codes with supporting evidence, confidence scores, and detailed clinical context.
                </p>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardContent className="p-8">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">
                  Clinical Summarization
                </h3>
                <p className="text-slate-600">
                  Generate patient-friendly summaries with clear explanations and actionable recommendations.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 bg-slate-50">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">95%+</div>
              <div className="text-slate-600">Classification Accuracy</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">5+</div>
              <div className="text-slate-600">Document Types Supported</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">Real-time</div>
              <div className="text-slate-600">Processing Speed</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-blue-600 mb-2">HIPAA</div>
              <div className="text-slate-600">Privacy Compliant</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-blue-600 text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Streamline Your Document Workflow?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Start processing medical documents with AI-powered intelligence today.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/upload">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-6">
                Get Started
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 bg-transparent text-white border-white hover:bg-white hover:text-blue-600">
                View Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
