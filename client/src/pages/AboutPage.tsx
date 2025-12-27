import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4 py-16 max-w-6xl">

        {/* Hero Section */}
        <div className="text-center mb-20">
          <h1 className="text-5xl font-bold text-slate-900 mb-6">
            Medical Document Intelligence Platform
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Enterprise-grade AI platform that transforms complex medical documents into
            patient-friendly insights. Built for patients, not providers.
          </p>
          <div className="flex gap-4 justify-center mt-8">
            <Link href="/upload">
              <Button size="lg" className="px-8">
                Start Analysis
              </Button>
            </Link>
            <Link href="/demo">
              <Button size="lg" variant="outline" className="px-8">
                View Demo
              </Button>
            </Link>
          </div>
        </div>

        {/* Core Features */}
        <div className="mb-20">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Core Features</h2>
            <p className="text-slate-600 text-lg">
              Comprehensive medical document analysis powered by advanced AI
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Document Classification</CardTitle>
                <CardDescription>Intelligent document type identification</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-slate-700">
                <p>Automatically identifies medical document types including:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Complete Blood Count (CBC)</li>
                  <li>Basic Metabolic Panel (BMP)</li>
                  <li>Imaging Reports (X-Ray, CT, MRI)</li>
                  <li>Clinical Notes</li>
                  <li>Pathology Reports</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">ICD-10 Code Extraction</CardTitle>
                <CardDescription>Automated diagnosis code identification</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-slate-700">
                <p>Extracts diagnostic codes with:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Evidence-based citations from document</li>
                  <li>Confidence scores for each code</li>
                  <li>Detailed clinical context</li>
                  <li>Supporting documentation</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Clinical Summarization</CardTitle>
                <CardDescription>Patient-friendly explanations</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-slate-700">
                <p>Generates clear summaries that include:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Simple language explanations</li>
                  <li>Key findings highlighted</li>
                  <li>Actionable recommendations</li>
                  <li>Normal vs abnormal ranges</li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-xl">Medical Translator</CardTitle>
                <CardDescription>Convert medical jargon to plain English</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3 text-slate-700">
                <p>Simplifies complex terminology with:</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>ELI5 (Explain Like I'm 5) mode</li>
                  <li>Term-by-term definitions</li>
                  <li>Real-world analogies</li>
                  <li>Multi-language support (coming soon)</li>
                </ul>
              </CardContent>
            </Card>

          </div>
        </div>

        {/* Patient-Centric Features */}
        <div className="mb-20">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Patient-Centric Intelligence</h2>
            <p className="text-slate-600 text-lg">
              Advanced features designed specifically for patient understanding
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Document Chat</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-slate-700">
                <p>Ask questions about your results in natural language</p>
                <p className="text-slate-500 italic">"What does my WBC count mean?"</p>
                <p>Get context-aware answers with source citations</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Medication Intelligence</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-slate-700">
                <p>Automatically extract medications from documents</p>
                <p>Check for dangerous drug interactions</p>
                <p>Get dosage and frequency information</p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <CardTitle className="text-lg">Action Items Generator</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-slate-700">
                <p>Personalized next steps based on results</p>
                <p>Questions to ask your doctor</p>
                <p>Urgency level assessment</p>
              </CardContent>
            </Card>

          </div>
        </div>

        {/* How It Works */}
        <div className="mb-20">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">How It Works</h2>
            <p className="text-slate-600 text-lg">
              Simple four-step process for medical document analysis
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl font-bold text-white">1</span>
              </div>
              <h3 className="font-semibold text-lg mb-2">Upload</h3>
              <p className="text-sm text-slate-600">
                Upload your medical document (PDF or TXT format)
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl font-bold text-white">2</span>
              </div>
              <h3 className="font-semibold text-lg mb-2">Analyze</h3>
              <p className="text-sm text-slate-600">
                AI processes and classifies your document automatically
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl font-bold text-white">3</span>
              </div>
              <h3 className="font-semibold text-lg mb-2">Review</h3>
              <p className="text-sm text-slate-600">
                View classification, codes, and patient-friendly summary
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl font-bold text-white">4</span>
              </div>
              <h3 className="font-semibold text-lg mb-2">Explore</h3>
              <p className="text-sm text-slate-600">
                Use translator, chat, and medication analysis features
              </p>
            </div>

          </div>
        </div>

        {/* Technology Stack */}
        <div className="mb-20">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Technology</h2>
            <p className="text-slate-600 text-lg">
              Built with enterprise-grade open-source technologies
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">

            <Card className="border-slate-200">
              <CardHeader>
                <CardTitle>Backend Infrastructure</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-semibold text-sm mb-1">Framework</p>
                    <p className="text-sm text-slate-600">FastAPI (Python)</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">AI Engine</p>
                    <p className="text-sm text-slate-600">Google Gemini</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Database</p>
                    <p className="text-sm text-slate-600">SQLAlchemy</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Processing</p>
                    <p className="text-sm text-slate-600">pypdf, LangChain</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader>
                <CardTitle>Frontend Stack</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="font-semibold text-sm mb-1">Framework</p>
                    <p className="text-sm text-slate-600">React + TypeScript</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Build Tool</p>
                    <p className="text-sm text-slate-600">Vite</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Styling</p>
                    <p className="text-sm text-slate-600">TailwindCSS</p>
                  </div>
                  <div>
                    <p className="font-semibold text-sm mb-1">Components</p>
                    <p className="text-sm text-slate-600">shadcn/ui</p>
                  </div>
                </div>
              </CardContent>
            </Card>

          </div>
        </div>

        {/* Key Benefits */}
        <div className="mb-20">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-slate-900 mb-3">Why Choose This Platform</h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">

            <Card className="border-slate-200 bg-white">
              <CardContent className="pt-6">
                <h3 className="font-semibold text-lg mb-3">Patient-First Design</h3>
                <p className="text-slate-700 text-sm leading-relaxed">
                  Built specifically for patients, not healthcare providers.
                  Every feature focuses on clarity, simplicity, and actionable insights.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 bg-white">
              <CardContent className="pt-6">
                <h3 className="font-semibold text-lg mb-3">Privacy Focused</h3>
                <p className="text-slate-700 text-sm leading-relaxed">
                  Real-time processing with optional storage. Your medical documents
                  remain private and secure throughout the analysis process.
                </p>
              </CardContent>
            </Card>

            <Card className="border-slate-200 bg-white">
              <CardContent className="pt-6">
                <h3 className="font-semibold text-lg mb-3">Free & Open Source</h3>
                <p className="text-slate-700 text-sm leading-relaxed">
                  Uses Google Gemini free tier (no credit card required).
                  Built with open-source technologies. Deploy anywhere.
                </p>
              </CardContent>
            </Card>

          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-white">
            <CardContent className="p-12">
              <h2 className="text-3xl font-bold mb-4 text-slate-900">
                Ready to Get Started?
              </h2>
              <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
                Upload your medical document and receive comprehensive AI-powered analysis in seconds.
              </p>
              <div className="flex gap-4 justify-center">
                <Link href="/upload">
                  <Button size="lg" className="px-8">
                    Start Analysis
                  </Button>
                </Link>
                <Link href="/demo">
                  <Button size="lg" variant="outline" className="px-8">
                    View Demo
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
