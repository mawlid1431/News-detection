import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CheckCircle, AlertTriangle, HelpCircle, Send, Link2, Type } from "lucide-react";

interface DetectionResult {
  type: "verified" | "warning" | "uncertain";
  title: string;
  message: string;
  sources?: string[];
  confidence?: number;
}

const DetectionWidget = () => {
  const [textInput, setTextInput] = useState("");
  const [linkInput, setLinkInput] = useState("");
  const [results, setResults] = useState<DetectionResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const mockDetection = (input: string, isLink: boolean): DetectionResult => {
    // Mock detection logic
    const keywords = input.toLowerCase();
    
    if (keywords.includes("covid") || keywords.includes("vaccine")) {
      return {
        type: "warning",
        title: "Potentially Misleading Information Detected",
        message: "This content contains claims about COVID-19 that may be misleading. Please verify with trusted health authorities.",
        sources: ["WHO", "CDC", "Reuters Fact Check"],
        confidence: 85
      };
    } else if (keywords.includes("election") || keywords.includes("voting")) {
      return {
        type: "uncertain",
        title: "Partially Verified Information",
        message: "Some aspects of this content have been verified, but other claims require additional fact-checking.",
        sources: ["AP News", "BBC", "Politifact"],
        confidence: 65
      };
    } else {
      return {
        type: "verified",
        title: "Information Appears Credible",
        message: "This content has been cross-referenced with multiple trusted sources and appears to be accurate.",
        sources: ["Reuters", "Associated Press", "BBC News"],
        confidence: 92
      };
    }
  };

  const handleSubmit = async (input: string, isLink: boolean) => {
    if (!input.trim()) return;

    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      const result = mockDetection(input, isLink);
      setResults(prev => [...prev, result]);
      setIsLoading(false);
    }, 2000);
  };

  const getResultIcon = (type: DetectionResult["type"]) => {
    switch (type) {
      case "verified":
        return <CheckCircle className="w-5 h-5 text-verified" />;
      case "warning":
        return <AlertTriangle className="w-5 h-5 text-warning" />;
      case "uncertain":
        return <HelpCircle className="w-5 h-5 text-uncertain" />;
    }
  };

  const getResultStyle = (type: DetectionResult["type"]) => {
    switch (type) {
      case "verified":
        return "border-verified/20 bg-verified/5";
      case "warning":
        return "border-warning/20 bg-warning/5";
      case "uncertain":
        return "border-uncertain/20 bg-uncertain/5";
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-semibold">AI-Powered Fact Checker</h2>
        <p className="text-muted-foreground">
          Enter a headline, statement, or news link to verify its credibility
        </p>
      </div>

      <Card className="p-6">
        <Tabs defaultValue="text" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="text" className="flex items-center gap-2">
              <Type className="w-4 h-4" />
              Text Input
            </TabsTrigger>
            <TabsTrigger value="link" className="flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              News Link
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="text" className="space-y-4">
            <Textarea
              placeholder="Paste a headline, statement, or paragraph to verify..."
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              className="min-h-[100px] resize-none"
            />
            <Button 
              onClick={() => handleSubmit(textInput, false)}
              disabled={!textInput.trim() || isLoading}
              className="w-full"
            >
              <Send className="w-4 h-4 mr-2" />
              {isLoading ? "Analyzing..." : "Verify Text"}
            </Button>
          </TabsContent>
          
          <TabsContent value="link" className="space-y-4">
            <Input
              placeholder="https://example.com/news-article"
              value={linkInput}
              onChange={(e) => setLinkInput(e.target.value)}
              type="url"
            />
            <Button 
              onClick={() => handleSubmit(linkInput, true)}
              disabled={!linkInput.trim() || isLoading}
              className="w-full"
            >
              <Send className="w-4 h-4 mr-2" />
              {isLoading ? "Analyzing..." : "Verify Link"}
            </Button>
          </TabsContent>
        </Tabs>
      </Card>

      {/* Results Section */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Detection Results</h3>
          <div className="space-y-3">
            {results.map((result, index) => (
              <Card 
                key={index} 
                className={`p-4 chat-bubble-fade ${getResultStyle(result.type)}`}
              >
                <div className="flex items-start gap-3">
                  {getResultIcon(result.type)}
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{result.title}</h4>
                      {result.confidence && (
                        <span className="text-sm text-muted-foreground">
                          {result.confidence}% confidence
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {result.message}
                    </p>
                    {result.sources && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-xs text-muted-foreground">Sources:</span>
                        {result.sources.map((source, idx) => (
                          <span 
                            key={idx}
                            className="text-xs bg-muted px-2 py-1 rounded-md"
                          >
                            {source}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {isLoading && (
        <Card className="p-4 chat-bubble-fade">
          <div className="flex items-center gap-3">
            <div className="animate-spin w-5 h-5 border-2 border-primary border-t-transparent rounded-full"></div>
            <div>
              <p className="font-medium">Analyzing content...</p>
              <p className="text-sm text-muted-foreground">
                Cross-referencing with trusted sources
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default DetectionWidget;