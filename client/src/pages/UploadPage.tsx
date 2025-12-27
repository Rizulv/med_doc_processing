import { useState } from "react";
import { UploadCard } from "@/components/UploadCard";
import { ClassificationPanel } from "@/components/ClassificationPanel";
import { CodeCard } from "@/components/CodeCard";
import { SummaryCard } from "@/components/SummaryCard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import {
  AlertCircle,
  CheckCircle2,
  Languages,
  MessageCircle,
  Pill,
  ClipboardList,
  Sparkles,
  Send,
  Loader2
} from "lucide-react";
import api from "@/lib/api";
import type { UploadResponse } from "@shared/schema";
import DocTypeSelect, { type DocTypeChoice } from "@/components/DocTypeSelect";

export default function UploadPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [docType, setDocType] = useState<DocTypeChoice>("AUTO");
  const { toast } = useToast();

  // Patient-facing features state
  const [documentText, setDocumentText] = useState<string>("");
  const [translatedText, setTranslatedText] = useState<any>(null);
  const [isTranslating, setIsTranslating] = useState(false);

  const [chatQuestion, setChatQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState<any[]>([]);
  const [isAsking, setIsAsking] = useState(false);

  const [medications, setMedications] = useState<any>(null);
  const [medicationList, setMedicationList] = useState("");
  const [interactions, setInteractions] = useState<any>(null);
  const [isCheckingMeds, setIsCheckingMeds] = useState(false);

  const [actionItems, setActionItems] = useState<any>(null);
  const [isGettingActions, setIsGettingActions] = useState(false);

  const handleFileUpload = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("run_pipeline", "true");

      if (docType !== "AUTO") {
        formData.append("document_type_hint", docType);
      }

      const response = await api.post<UploadResponse>("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data);

      // Extract document text for patient-facing features
      const textResponse = await api.get(`/documents/${response.data.document_id}`);
      // We'll need to store the text somehow - for now we'll ask user to paste it

      toast({
        title: "Processing Complete",
        description: "Document classified and analyzed successfully",
      });
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail || err.message || "Failed to process document";
      setError(errorMessage);

      toast({
        title: "Processing Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
    setTranslatedText(null);
    setChatHistory([]);
    setMedications(null);
    setInteractions(null);
    setActionItems(null);
    setDocumentText("");
  };

  const handleTranslate = async () => {
    if (!documentText.trim()) {
      toast({
        title: "No Text",
        description: "Please enter or paste medical text to translate",
        variant: "destructive",
      });
      return;
    }

    setIsTranslating(true);
    try {
      const response = await api.post("/api/translate", {
        document_text: documentText,
        target_language: "simple"
      });
      setTranslatedText(response.data);
      toast({
        title: "Translation Complete",
        description: "Medical terms translated to simple English",
      });
    } catch (err: any) {
      toast({
        title: "Translation Failed",
        description: err.response?.data?.detail || "Failed to translate",
        variant: "destructive",
      });
    } finally {
      setIsTranslating(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!chatQuestion.trim() || !documentText.trim()) {
      toast({
        title: "Missing Information",
        description: "Please enter both document text and your question",
        variant: "destructive",
      });
      return;
    }

    setIsAsking(true);
    try {
      const response = await api.post("/api/chat", {
        document_text: documentText,
        question: chatQuestion,
        conversation_history: chatHistory
      });

      setChatHistory([...chatHistory, {
        question: chatQuestion,
        answer: response.data.answer,
        confidence: response.data.confidence,
        sources: response.data.sources
      }]);
      setChatQuestion("");

      toast({
        title: "Answer Received",
        description: "Your question has been answered",
      });
    } catch (err: any) {
      toast({
        title: "Chat Failed",
        description: err.response?.data?.detail || "Failed to get answer",
        variant: "destructive",
      });
    } finally {
      setIsAsking(false);
    }
  };

  const handleExtractMedications = async () => {
    if (!documentText.trim()) {
      toast({
        title: "No Text",
        description: "Please enter medical document text",
        variant: "destructive",
      });
      return;
    }

    setIsCheckingMeds(true);
    try {
      const response = await api.post("/api/extract-medications", {
        document_text: documentText
      });
      setMedications(response.data);

      // Auto-populate medication list
      if (response.data.medications?.length > 0) {
        setMedicationList(response.data.medications.map((m: any) => m.name).join(", "));
      }

      toast({
        title: "Medications Extracted",
        description: `Found ${response.data.medications?.length || 0} medications`,
      });
    } catch (err: any) {
      toast({
        title: "Extraction Failed",
        description: err.response?.data?.detail || "Failed to extract medications",
        variant: "destructive",
      });
    } finally {
      setIsCheckingMeds(false);
    }
  };

  const handleCheckInteractions = async () => {
    if (!medicationList.trim()) {
      toast({
        title: "No Medications",
        description: "Please enter medication names (comma separated)",
        variant: "destructive",
      });
      return;
    }

    setIsCheckingMeds(true);
    try {
      const meds = medicationList.split(",").map(m => m.trim()).filter(m => m);
      const response = await api.post("/api/check-interactions", {
        medications: meds
      });
      setInteractions(response.data);

      toast({
        title: "Interaction Check Complete",
        description: `Found ${response.data.interactions?.length || 0} interactions`,
      });
    } catch (err: any) {
      toast({
        title: "Check Failed",
        description: err.response?.data?.detail || "Failed to check interactions",
        variant: "destructive",
      });
    } finally {
      setIsCheckingMeds(false);
    }
  };

  const handleGetActionItems = async () => {
    if (!documentText.trim()) {
      toast({
        title: "No Text",
        description: "Please enter medical document text",
        variant: "destructive",
      });
      return;
    }

    setIsGettingActions(true);
    try {
      const response = await api.post("/api/action-items", {
        document_text: documentText,
        codes: result?.results?.codes?.codes || []
      });
      setActionItems(response.data);

      toast({
        title: "Action Items Generated",
        description: "Your personalized action plan is ready",
      });
    } catch (err: any) {
      toast({
        title: "Generation Failed",
        description: err.response?.data?.detail || "Failed to generate action items",
        variant: "destructive",
      });
    } finally {
      setIsGettingActions(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">
            Medical Document Analysis
          </h1>
          <p className="text-slate-600 text-lg max-w-3xl mx-auto">
            Upload your medical document for AI-powered analysis with patient-friendly insights
          </p>
        </div>

        <div className="max-w-2xl mx-auto mb-4">
          <DocTypeSelect value={docType} onChange={setDocType} />
        </div>

        <div className="max-w-2xl mx-auto mb-8">
          <UploadCard onFileSelect={handleFileUpload} isProcessing={isProcessing} />
        </div>

        {error && (
          <div className="max-w-4xl mx-auto mb-8">
            <Card className="border-destructive/50 bg-destructive/5">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-destructive mb-1">Processing Error</h3>
                    <p className="text-sm text-destructive/90">{error}</p>
                  </div>
                  <Button variant="outline" onClick={handleReset} size="sm">
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {result && result.processed && result.results && (
          <div className="max-w-6xl mx-auto space-y-6 pb-16">
            <div className="flex items-center justify-between sticky top-0 bg-white z-10 py-4 -mt-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
                <h2 className="text-2xl font-semibold">Analysis Results</h2>
              </div>
              <Button variant="outline" onClick={handleReset}>
                Analyze Another Document
              </Button>
            </div>

            {/* Core Analysis Tab */}
            <Tabs defaultValue="analysis" className="w-full">
              <TabsList className="grid w-full grid-cols-5 h-12 sticky top-16 bg-white z-10">
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
              <TabsContent value="analysis" className="space-y-6 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
                <ClassificationPanel classification={result.results.classification} />

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">ICD-10 Diagnostic Codes</h3>
                  {!result.results.codes?.codes || result.results.codes.codes.length === 0 ? (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <p className="text-sm text-muted-foreground">
                          No diagnostic codes identified
                        </p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="grid gap-4 sm:grid-cols-2">
                      {result.results.codes.codes.map((code, idx) => (
                        <CodeCard key={idx} code={code} />
                      ))}
                    </div>
                  )}
                </div>

                <SummaryCard summary={result.results.summary} />
              </TabsContent>

              {/* Medical Translator */}
              <TabsContent value="translator" className="space-y-6 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Languages className="w-5 h-5" />
                      Medical Translator (ELI5 Mode)
                    </CardTitle>
                    <CardDescription>
                      Convert complex medical jargon to simple, easy-to-understand language
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">
                        Paste your medical document text:
                      </label>
                      <Textarea
                        placeholder="Example: Patient presents with leukocytosis and elevated CRP..."
                        value={documentText}
                        onChange={(e) => setDocumentText(e.target.value)}
                        className="min-h-32"
                      />
                    </div>
                    <Button
                      onClick={handleTranslate}
                      disabled={isTranslating}
                      className="w-full"
                    >
                      {isTranslating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Translating...
                        </>
                      ) : (
                        <>
                          <Languages className="w-4 h-4 mr-2" />
                          Translate to Simple English
                        </>
                      )}
                    </Button>

                    {translatedText && (
                      <div className="mt-6 space-y-4">
                        <Card className="bg-green-50 dark:bg-green-950/20 border-green-200">
                          <CardContent className="p-4">
                            <h4 className="font-semibold mb-2">Simple Translation:</h4>
                            <p className="text-sm">{translatedText.translated_text}</p>
                          </CardContent>
                        </Card>

                        {translatedText.explanations?.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="font-semibold">Term Explanations:</h4>
                            {translatedText.explanations.map((exp: any, idx: number) => (
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
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Document Chat */}
              <TabsContent value="chat" className="space-y-6 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageCircle className="w-5 h-5" />
                      Chat with Your Document
                    </CardTitle>
                    <CardDescription>
                      Ask questions about your medical document and get instant answers
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {!documentText && (
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          First, paste your document text:
                        </label>
                        <Textarea
                          placeholder="Paste your medical document here..."
                          value={documentText}
                          onChange={(e) => setDocumentText(e.target.value)}
                          className="min-h-24"
                        />
                      </div>
                    )}

                    {chatHistory.length > 0 && (
                      <div className="space-y-3 max-h-96 overflow-y-auto">
                        {chatHistory.map((chat, idx) => (
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
                                {chat.sources?.length > 0 && (
                                  <div className="mt-2 text-xs text-muted-foreground">
                                    <strong>Sources:</strong> {chat.sources.join(", ")}
                                  </div>
                                )}
                              </CardContent>
                            </Card>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Input
                        placeholder="Ask a question: What does my WBC count mean?"
                        value={chatQuestion}
                        onChange={(e) => setChatQuestion(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                      />
                      <Button
                        onClick={handleAskQuestion}
                        disabled={isAsking}
                        size="icon"
                      >
                        {isAsking ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Send className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Medications */}
              <TabsContent value="medications" className="space-y-6 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
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
                    {!documentText && (
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Paste document with medications:
                        </label>
                        <Textarea
                          placeholder="Example: Patient on Metformin 500mg twice daily..."
                          value={documentText}
                          onChange={(e) => setDocumentText(e.target.value)}
                          className="min-h-24"
                        />
                      </div>
                    )}

                    <Button
                      onClick={handleExtractMedications}
                      disabled={isCheckingMeds}
                      className="w-full"
                    >
                      {isCheckingMeds ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Extracting...
                        </>
                      ) : (
                        "Extract Medications"
                      )}
                    </Button>

                    {medications?.medications?.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-semibold">Found Medications:</h4>
                        {medications.medications.map((med: any, idx: number) => (
                          <Card key={idx}>
                            <CardContent className="p-3">
                              <div className="font-semibold">{med.name}</div>
                              {med.dosage && <div className="text-sm">Dosage: {med.dosage}</div>}
                              {med.frequency && <div className="text-sm">Frequency: {med.frequency}</div>}
                              {med.instructions && <div className="text-sm text-muted-foreground">{med.instructions}</div>}
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}

                    <div className="pt-4 border-t">
                      <label className="text-sm font-medium mb-2 block">
                        Check Drug Interactions (comma-separated):
                      </label>
                      <Input
                        placeholder="Example: Warfarin, Aspirin, Vitamin K"
                        value={medicationList}
                        onChange={(e) => setMedicationList(e.target.value)}
                      />
                      <Button
                        onClick={handleCheckInteractions}
                        disabled={isCheckingMeds}
                        className="w-full mt-2"
                      >
                        Check Interactions
                      </Button>
                    </div>

                    {interactions && (
                      <div className="space-y-2">
                        {interactions.interactions?.length > 0 ? (
                          <>
                            <h4 className="font-semibold text-red-600">Found Interactions:</h4>
                            {interactions.interactions.map((int: any, idx: number) => (
                              <Card key={idx} className="border-red-200 bg-red-50 dark:bg-red-950/20">
                                <CardContent className="p-3">
                                  <div className="font-semibold">
                                    {int.severity?.toUpperCase()} - {int.medications_involved?.join(" + ")}
                                  </div>
                                  <div className="text-sm mt-1">{int.description}</div>
                                  <div className="text-sm text-blue-600 mt-1">
                                    💡 {int.recommendation}
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                          </>
                        ) : (
                          <Card className="border-green-200 bg-green-50 dark:bg-green-950/20">
                            <CardContent className="p-4 text-center">
                              <CheckCircle2 className="w-6 h-6 text-green-600 mx-auto mb-2" />
                              <p className="text-sm">No significant interactions found</p>
                            </CardContent>
                          </Card>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Action Items */}
              <TabsContent value="actions" className="space-y-6 max-h-[calc(100vh-16rem)] overflow-y-auto pr-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <ClipboardList className="w-5 h-5" />
                      Action Items Generator
                    </CardTitle>
                    <CardDescription>
                      Get personalized next steps, questions for your doctor, and reminders
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {!documentText && (
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Paste your medical document:
                        </label>
                        <Textarea
                          placeholder="Paste your medical document here..."
                          value={documentText}
                          onChange={(e) => setDocumentText(e.target.value)}
                          className="min-h-24"
                        />
                      </div>
                    )}

                    <Button
                      onClick={handleGetActionItems}
                      disabled={isGettingActions}
                      className="w-full"
                    >
                      {isGettingActions ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        "Generate Action Items"
                      )}
                    </Button>

                    {actionItems && (
                      <div className="space-y-4">
                        {actionItems.urgency && (
                          <Card className={
                            actionItems.urgency === 'emergency' ? 'border-red-500 bg-red-50' :
                            actionItems.urgency === 'urgent' ? 'border-orange-500 bg-orange-50' :
                            'border-blue-500 bg-blue-50'
                          }>
                            <CardContent className="p-3 text-center">
                              <span className="font-semibold">
                                Urgency: {actionItems.urgency?.toUpperCase()}
                              </span>
                            </CardContent>
                          </Card>
                        )}

                        {actionItems.action_items?.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">✅ Action Items:</h4>
                            <ul className="space-y-2">
                              {actionItems.action_items.map((item: string, idx: number) => (
                                <li key={idx}>
                                  <Card>
                                    <CardContent className="p-3 text-sm">
                                      {item}
                                    </CardContent>
                                  </Card>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {actionItems.questions?.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">❓ Questions for Your Doctor:</h4>
                            <ul className="space-y-2">
                              {actionItems.questions.map((q: string, idx: number) => (
                                <li key={idx}>
                                  <Card className="bg-purple-50 dark:bg-purple-950/20">
                                    <CardContent className="p-3 text-sm">
                                      {q}
                                    </CardContent>
                                  </Card>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {actionItems.reminders?.length > 0 && (
                          <div>
                            <h4 className="font-semibold mb-2">🔔 Reminders:</h4>
                            <ul className="space-y-2">
                              {actionItems.reminders.map((r: string, idx: number) => (
                                <li key={idx}>
                                  <Card className="bg-yellow-50 dark:bg-yellow-950/20">
                                    <CardContent className="p-3 text-sm">
                                      {r}
                                    </CardContent>
                                  </Card>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        )}
      </div>
    </div>
  );
}
