import { useState } from "react";
import { ClassificationPanel } from "@/components/ClassificationPanel";
import { CodeCard } from "@/components/CodeCard";
import { SummaryCard } from "@/components/SummaryCard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Link } from "wouter";
import {
  CheckCircle2,
  Languages,
  MessageCircle,
  Pill,
  ClipboardList,
  Sparkles,
  AlertCircle,
  Home
} from "lucide-react";

// Mock data - pre-loaded example results
const DEMO_DATA = {
  classification: {
    document_type: "COMPLETE BLOOD COUNT",
    confidence: 0.95,
    rationale: "The document contains typical CBC parameters including WBC, hemoglobin, hematocrit, and platelet counts.",
    evidence: ["WBC 13.2 x10^3/µL", "Hemoglobin 14.1 g/dL", "Platelets 250 x10^3/µL"]
  },
  codes: {
    codes: [
      {
        code: "D72.829",
        description: "Elevated white blood cell count (Leukocytosis)",
        confidence: 0.90,
        evidence: ["WBC 13.2 x10^3/µL (elevated)", "Impression: leukocytosis"]
      }
    ]
  },
  summary: {
    summary: "Your Complete Blood Count (CBC) test shows that most of your blood components are within normal ranges. The main finding is an elevated white blood cell count (13.2, normal range is 4-11). This could indicate your body is fighting an infection or inflammation. Your hemoglobin (14.1) and platelets (250) are both normal, which is good news.",
    bullets: [
      "White Blood Cells (WBC): 13.2 x10^3/µL - ELEVATED (normal: 4-11). This means your body might be fighting an infection.",
      "Hemoglobin (Hgb): 14.1 g/dL - NORMAL (normal: 12-16). Your oxygen-carrying cells are healthy.",
      "Platelets: 250 x10^3/µL - NORMAL (normal: 150-400). Your blood clotting ability is good."
    ],
    citations: ["WBC 13.2 x10^3/µL (elevated)", "Hgb 14.1 g/dL", "Platelets 250 x10^3/µL"],
    confidence: 0.85
  },
  translator: {
    translated_text: "Your blood test shows that your white blood cells are a bit high. This usually means your body is fighting off something, like an infection or inflammation. Think of white blood cells as your body's army - when there's a threat, the army gets bigger. Your red blood cells (which carry oxygen) and platelets (which help blood clot) are both at normal, healthy levels.",
    explanations: [
      {
        term: "Leukocytosis",
        simple: "High white blood cell count",
        meaning: "Your body is making extra white blood cells to fight something"
      },
      {
        term: "WBC (White Blood Cells)",
        simple: "Infection-fighting cells",
        meaning: "Like soldiers in your bloodstream that protect you from germs"
      },
      {
        term: "Hemoglobin",
        simple: "Oxygen carrier",
        meaning: "The part of red blood cells that carries oxygen to your organs"
      }
    ]
  },
  chat: [
    {
      question: "What does elevated WBC mean?",
      answer: "Elevated WBC (white blood cells) means your body has more infection-fighting cells than normal. This is usually your body's natural response to fighting an infection, inflammation, or stress. A count of 13.2 is mildly elevated (normal is 4-11). It's not necessarily dangerous, but your doctor may want to investigate the cause.",
      confidence: 0.88,
      sources: ["WBC 13.2 x10^3/µL (elevated)"]
    },
    {
      question: "Should I be worried about this?",
      answer: "A mildly elevated WBC like yours (13.2) is usually not a major concern. It often resolves on its own once your body finishes fighting whatever triggered it. However, you should follow up with your doctor to determine the cause, especially if you have symptoms like fever, fatigue, or pain. Your doctor may recommend repeating the test in a few weeks.",
      confidence: 0.82,
      sources: ["Impression: leukocytosis"]
    }
  ],
  medications: {
    medications: []  // No medications in this example
  },
  actionItems: {
    action_items: [
      "Follow up with your doctor within 2-3 weeks to discuss the elevated WBC",
      "Repeat CBC test in 4-6 weeks to monitor WBC count",
      "Keep track of any symptoms (fever, fatigue, infections)"
    ],
    questions: [
      "What could be causing my elevated white blood cell count?",
      "Do I need any additional tests to find the cause?",
      "Should I be concerned about infection?"
    ],
    reminders: [
      "Bring previous test results to your next appointment",
      "Mention any recent illnesses or infections to your doctor",
      "Ask about recommended follow-up timeline"
    ],
    urgency: "routine"
  }
};

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState("analysis");

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold text-slate-900 mb-2">
                Demo: CBC Lab Report Analysis
              </h1>
              <p className="text-slate-600 text-lg">
                Example results showing all features (no API calls - instant results)
              </p>
            </div>
            <Link href="/upload">
              <Button variant="outline" size="lg">
                <Home className="w-4 h-4 mr-2" />
                Try Live Version
              </Button>
            </Link>
          </div>

          <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div className="text-sm">
                  <strong>Demo Mode:</strong> This page shows pre-loaded example results. All features work instantly without making API calls. Try uploading your own document on the home page for real analysis!
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        <div className="space-y-8">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-green-600" />
            <h2 className="text-2xl font-semibold">Analysis Results</h2>
            <Badge variant="secondary">Demo Data</Badge>
          </div>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-5 h-12">
              <TabsTrigger value="analysis" className="font-medium">
                Analysis
              </TabsTrigger>
              <TabsTrigger value="translator" className="font-medium">
                Translator
              </TabsTrigger>
              <TabsTrigger value="chat" className="font-medium">
                Chat
              </TabsTrigger>
              <TabsTrigger value="medications" className="font-medium">
                Medications
              </TabsTrigger>
              <TabsTrigger value="actions" className="font-medium">
                Action Items
              </TabsTrigger>
            </TabsList>

            {/* Core Analysis */}
            <TabsContent value="analysis" className="space-y-6">
              <ClassificationPanel classification={DEMO_DATA.classification} />

              <div className="space-y-4">
                <h3 className="text-xl font-semibold">ICD-10 Diagnostic Codes</h3>
                <div className="grid gap-4 sm:grid-cols-2">
                  {DEMO_DATA.codes.codes.map((code, idx) => (
                    <CodeCard key={idx} code={code} />
                  ))}
                </div>
              </div>

              <SummaryCard summary={DEMO_DATA.summary} />
            </TabsContent>

            {/* Medical Translator */}
            <TabsContent value="translator" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Languages className="w-5 h-5" />
                    Medical Translator (ELI5 Mode)
                  </CardTitle>
                  <CardDescription>
                    Complex medical terms translated to simple English
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Card className="bg-green-50 dark:bg-green-950/20 border-green-200">
                    <CardContent className="p-4">
                      <h4 className="font-semibold mb-2">Simple Translation:</h4>
                      <p className="text-sm">{DEMO_DATA.translator.translated_text}</p>
                    </CardContent>
                  </Card>

                  <div className="space-y-2">
                    <h4 className="font-semibold">Term Explanations:</h4>
                    {DEMO_DATA.translator.explanations.map((exp, idx) => (
                      <Card key={idx}>
                        <CardContent className="p-3">
                          <div className="flex items-start gap-2">
                            <span className="font-semibold text-blue-600">{exp.term}:</span>
                            <div>
                              <p className="text-sm">{exp.simple}</p>
                              <p className="text-xs text-muted-foreground mt-1">{exp.meaning}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Document Chat */}
            <TabsContent value="chat" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5" />
                    Chat with Your Document
                  </CardTitle>
                  <CardDescription>
                    Example conversation showing how the chat feature works
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    {DEMO_DATA.chat.map((chat, idx) => (
                      <div key={idx} className="space-y-2">
                        <Card className="bg-blue-50 dark:bg-blue-950/20">
                          <CardContent className="p-3">
                            <p className="text-sm font-semibold text-blue-700 dark:text-blue-300">
                              Q: {chat.question}
                            </p>
                          </CardContent>
                        </Card>
                        <Card className="bg-green-50 dark:bg-green-950/20">
                          <CardContent className="p-3">
                            <p className="text-sm">{chat.answer}</p>
                            {chat.sources.length > 0 && (
                              <div className="mt-2 text-xs text-muted-foreground">
                                <strong>Sources:</strong> {chat.sources.join(", ")}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </div>
                    ))}
                  </div>

                  <Card className="bg-purple-50 dark:bg-purple-950/20 border-purple-200">
                    <CardContent className="p-4 text-sm">
                      <strong>Try it live:</strong> Upload your own document to ask custom questions!
                    </CardContent>
                  </Card>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Medications */}
            <TabsContent value="medications" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Pill className="w-5 h-5" />
                    Medication Intelligence
                  </CardTitle>
                  <CardDescription>
                    Extract medications and check for drug interactions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Card className="bg-gray-50 dark:bg-gray-950/20">
                    <CardContent className="p-4 text-center text-sm text-muted-foreground">
                      No medications found in this CBC report.
                      <br />
                      Try uploading a clinical note or prescription to see medication extraction!
                    </CardContent>
                  </Card>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Action Items */}
            <TabsContent value="actions" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ClipboardList className="w-5 h-5" />
                    Action Items Generator
                  </CardTitle>
                  <CardDescription>
                    Personalized next steps based on your results
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Card className="border-blue-500 bg-blue-50">
                    <CardContent className="p-3 text-center">
                      <span className="font-semibold">
                        Urgency: {DEMO_DATA.actionItems.urgency.toUpperCase()}
                      </span>
                    </CardContent>
                  </Card>

                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3">Action Items</h4>
                    <ul className="space-y-2">
                      {DEMO_DATA.actionItems.action_items.map((item, idx) => (
                        <li key={idx}>
                          <Card className="border-slate-200">
                            <CardContent className="p-3 text-sm text-slate-700">
                              {item}
                            </CardContent>
                          </Card>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3">Questions for Your Doctor</h4>
                    <ul className="space-y-2">
                      {DEMO_DATA.actionItems.questions.map((q, idx) => (
                        <li key={idx}>
                          <Card className="bg-purple-50 dark:bg-purple-950/20 border-purple-200">
                            <CardContent className="p-3 text-sm text-slate-700">
                              {q}
                            </CardContent>
                          </Card>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-slate-900 mb-3">Reminders</h4>
                    <ul className="space-y-2">
                      {DEMO_DATA.actionItems.reminders.map((r, idx) => (
                        <li key={idx}>
                          <Card className="bg-yellow-50 dark:bg-yellow-950/20 border-yellow-200">
                            <CardContent className="p-3 text-sm text-slate-700">
                              {r}
                            </CardContent>
                          </Card>
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* CTA */}
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
            <CardContent className="p-8 text-center">
              <h3 className="text-2xl font-bold mb-2">Like what you see?</h3>
              <p className="text-muted-foreground mb-4">
                Upload your own medical document for real AI-powered analysis
              </p>
              <Link href="/">
                <Button size="lg">
                  Try With Your Own Document
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}
