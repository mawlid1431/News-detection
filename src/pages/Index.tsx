import Navigation from "@/components/Navigation";
import TypewriterText from "@/components/TypewriterText";
import DetectionWidget from "@/components/DetectionWidget";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Shield, Search, Database, Users, CheckCircle, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";

const Index = () => {
  const taglines = [
    "Verify to Trust AI",
    "See Truth, Not Just Headlines", 
    "Verify Instantly. Trust Confidently",
    "AI That Fights Misinformation, For You"
  ];

  const features = [
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Fake News Detection",
      description: "Advanced AI algorithms analyze content and cross-reference with trusted sources to identify misinformation."
    },
    {
      icon: <Database className="w-8 h-8" />,
      title: "Trusted Sources",
      description: "Connected to 100+ verified news outlets and fact-checking organizations worldwide."
    },
    {
      icon: <Search className="w-8 h-8" />,
      title: "AI + NLP",
      description: "Natural Language Processing models trained on millions of verified articles and fact-checks."
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Community Verified",
      description: "Crowdsourced verification from journalists, experts, and trusted community members."
    }
  ];

  const stats = [
    { label: "Articles Verified Daily", value: "10,000+" },
    { label: "Trusted Sources", value: "100+" },
    { label: "Detection Accuracy", value: "94%" },
    { label: "Active Users", value: "50,000+" }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto text-center">
          <div className="space-y-8">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
              <TypewriterText 
                texts={taglines}
                typingSpeed={80}
                deletingSpeed={40}
                pauseDuration={3000}
              />
            </h1>
            
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Fight misinformation with AI-powered fact-checking. Verify headlines, 
              check sources, and make informed decisions with Trustify AI.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/signup">
                <Button size="lg" className="text-lg px-8">
                  Start Verifying
                </Button>
              </Link>
              <Link to="/resources">
                <Button variant="outline" size="lg" className="text-lg px-8">
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Detection Widget Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="container mx-auto">
          <DetectionWidget />
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          <div className="text-center space-y-8">
            <h2 className="text-3xl font-bold">Trusted by Thousands</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold text-primary mb-2">
                    {stat.value}
                  </div>
                  <div className="text-muted-foreground">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center space-y-8">
            <h2 className="text-3xl font-bold">How Trustify AI Works</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <Card key={index} className="p-6 text-center hover:shadow-lg transition-shadow">
                  <div className="flex justify-center mb-4 text-primary">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm">
                    {feature.description}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto text-center">
          <div className="space-y-8">
            <h2 className="text-3xl font-bold">
              Ready to Fight Misinformation?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Join thousands of users who trust Trustify AI to verify news and combat fake information.
            </p>
            <Link to="/signup">
              <Button size="lg" className="text-lg px-8">
                <CheckCircle className="w-5 h-5 mr-2" />
                Get Started Free
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Simple Footer */}
      <footer className="bg-primary text-primary-foreground py-12">
        <div className="container mx-auto px-4 text-center">
          <div className="space-y-4">
            <h3 className="text-2xl font-bold">Trustify AI</h3>
            <p className="text-primary-foreground/80">
              Connected to 100+ sources • Daily verification stats • Fighting misinformation with AI
            </p>
            <div className="flex justify-center space-x-6">
              <Link to="/" className="hover:text-primary-foreground/80">Home</Link>
              <Link to="/resources" className="hover:text-primary-foreground/80">Resources</Link>
              <Link to="/get-into-tech" className="hover:text-primary-foreground/80">Get Into Tech</Link>
              <Link to="/login" className="hover:text-primary-foreground/80">Login</Link>
            </div>
            <div className="pt-4 border-t border-primary-foreground/20">
              <p className="text-sm text-primary-foreground/60">
                © 2025 Trustify AI. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
