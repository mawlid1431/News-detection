import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BookOpen, FileText, Video, Users, ExternalLink, TrendingUp } from "lucide-react";

const Resources = () => {
  const resources = [
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Misinformation Detection Guide",
      description: "Learn how to identify fake news and misleading information online.",
      type: "Guide",
      readTime: "10 min read"
    },
    {
      icon: <FileText className="w-6 h-6" />,
      title: "Understanding AI Fact-Checking",
      description: "Deep dive into how artificial intelligence helps verify news credibility.",
      type: "Article",
      readTime: "15 min read"
    },
    {
      icon: <Video className="w-6 h-6" />,
      title: "Video Tutorial: Using Trustify AI",
      description: "Step-by-step walkthrough of our detection platform.",
      type: "Video",
      readTime: "8 min watch"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Community Guidelines",
      description: "Best practices for sharing and verifying information responsibly.",
      type: "Guidelines",
      readTime: "5 min read"
    }
  ];

  const trustedSources = [
    "Reuters",
    "Associated Press",
    "BBC News",
    "NPR",
    "The Guardian",
    "Politifact",
    "Snopes",
    "FactCheck.org",
    "AllSides",
    "MediaBias/FactCheck"
  ];

  const categories = [
    {
      title: "Politics & Elections",
      description: "Verify political claims and election information",
      articles: 45
    },
    {
      title: "Health & Medicine",
      description: "Check medical claims and health misinformation",
      articles: 38
    },
    {
      title: "Science & Technology",
      description: "Fact-check scientific claims and tech news",
      articles: 29
    },
    {
      title: "Finance & Economy",
      description: "Verify financial news and economic data",
      articles: 22
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          {/* Header */}
          <div className="text-center space-y-4 mb-16">
            <h1 className="text-4xl font-bold">Resources</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Educational content, guides, and tools to help you identify misinformation 
              and make informed decisions about the news you consume.
            </p>
          </div>

          {/* Featured Resources */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Featured Resources</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {resources.map((resource, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-primary">
                          {resource.icon}
                        </div>
                        <div>
                          <CardTitle className="text-lg">{resource.title}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs bg-muted px-2 py-1 rounded">
                              {resource.type}
                            </span>
                            <span className="text-xs text-muted-foreground">
                              {resource.readTime}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="mb-4">
                      {resource.description}
                    </CardDescription>
                    <Button variant="outline" className="w-full">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Read More
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Categories */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Misinformation Categories</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {categories.map((category, index) => (
                <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{category.title}</CardTitle>
                    <CardDescription>
                      {category.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground mb-4">
                      <TrendingUp className="w-4 h-4" />
                      {category.articles} articles
                    </div>
                    <Button variant="outline" size="sm" className="w-full">
                      Explore
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Trusted Sources */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Our Trusted Sources</h2>
            <Card>
              <CardHeader>
                <CardTitle>100+ Verified News Outlets</CardTitle>
                <CardDescription>
                  We cross-reference information with these trusted sources to provide accurate fact-checking.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {trustedSources.map((source, index) => (
                    <div 
                      key={index}
                      className="text-center p-3 bg-muted rounded-lg text-sm font-medium"
                    >
                      {source}
                    </div>
                  ))}
                </div>
                <div className="mt-6 text-center">
                  <Button variant="outline">
                    View All Sources
                    <ExternalLink className="w-4 h-4 ml-2" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* CTA Section */}
          <section className="text-center bg-muted/30 rounded-lg p-12">
            <h2 className="text-2xl font-semibold mb-4">
              Ready to Start Fact-Checking?
            </h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Use our AI-powered detection tool to verify news headlines, 
              check sources, and fight misinformation.
            </p>
            <Button size="lg">
              Try Detection Tool
            </Button>
          </section>
        </div>
      </div>
    </div>
  );
};

export default Resources;