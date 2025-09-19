import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Code, Brain, Database, Users, ExternalLink, BookOpen, Trophy } from "lucide-react";

const GetIntoTech = () => {
  const learningPaths = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI & Machine Learning",
      description: "Learn how artificial intelligence powers fact-checking systems",
      topics: ["Natural Language Processing", "Classification Models", "BERT & Transformers", "TensorFlow"],
      level: "Intermediate",
      duration: "8-12 weeks"
    },
    {
      icon: <Code className="w-6 h-6" />,
      title: "Web Development",
      description: "Build platforms like Trustify AI with modern web technologies",
      topics: ["React", "TypeScript", "API Integration", "UI/UX Design"],
      level: "Beginner",
      duration: "6-10 weeks"
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: "Data Science",
      description: "Analyze news patterns and build detection algorithms",
      topics: ["Python", "Data Analysis", "Statistical Models", "Visualization"],
      level: "Beginner",
      duration: "10-14 weeks"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Journalism & Tech",
      description: "Bridge journalism with technology for better fact-checking",
      topics: ["Digital Journalism", "Fact-Checking Methods", "Ethics", "Media Literacy"],
      level: "Beginner",
      duration: "4-6 weeks"
    }
  ];

  const resources = [
    {
      category: "For Students",
      items: [
        "Computer Science degree pathways",
        "Data Science bootcamps and courses",
        "AI/ML research opportunities",
        "Internship programs in tech"
      ]
    },
    {
      category: "For Journalists",
      items: [
        "Digital journalism tools and techniques",
        "Fact-checking methodologies",
        "Understanding AI bias and limitations",
        "Ethics in automated content verification"
      ]
    },
    {
      category: "For Developers",
      items: [
        "NLP libraries and frameworks",
        "Building news aggregation systems",
        "API integration for fact-checking",
        "Scalable web application architecture"
      ]
    }
  ];

  const projects = [
    {
      title: "Build a Mini Fact-Checker",
      description: "Create a simple fact-checking tool using Python and NLP",
      difficulty: "Beginner",
      tech: ["Python", "NLTK", "Flask"]
    },
    {
      title: "News Sentiment Analyzer",
      description: "Analyze the sentiment and bias in news articles",
      difficulty: "Intermediate",
      tech: ["JavaScript", "React", "News API"]
    },
    {
      title: "Misinformation Detection Bot",
      description: "Train a machine learning model to classify fake news",
      difficulty: "Advanced",
      tech: ["Python", "TensorFlow", "BERT"]
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <div className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto">
          {/* Header */}
          <div className="text-center space-y-4 mb-16">
            <h1 className="text-4xl font-bold">Get Into Tech</h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Learn AI, NLP, and fact-checking methods. Whether you're a student, journalist, 
              or developer, discover how technology fights misinformation.
            </p>
          </div>

          {/* Learning Paths */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Learning Paths</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {learningPaths.map((path, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="text-primary">
                          {path.icon}
                        </div>
                        <div>
                          <CardTitle className="text-lg">{path.title}</CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant={path.level === "Beginner" ? "secondary" : "outline"}>
                              {path.level}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {path.duration}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="mb-4">
                      {path.description}
                    </CardDescription>
                    <div className="space-y-3">
                      <h4 className="font-medium text-sm">What you'll learn:</h4>
                      <div className="flex flex-wrap gap-2">
                        {path.topics.map((topic, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button variant="outline" className="w-full mt-4">
                      <BookOpen className="w-4 h-4 mr-2" />
                      Start Learning
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Hands-on Projects */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Hands-on Projects</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {projects.map((project, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center gap-2 mb-2">
                      <Trophy className="w-5 h-5 text-primary" />
                      <Badge variant={
                        project.difficulty === "Beginner" ? "secondary" :
                        project.difficulty === "Intermediate" ? "outline" : "default"
                      }>
                        {project.difficulty}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg">{project.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="mb-4">
                      {project.description}
                    </CardDescription>
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        {project.tech.map((tech, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {tech}
                          </Badge>
                        ))}
                      </div>
                      <Button variant="outline" size="sm" className="w-full">
                        View Project
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Resources by Audience */}
          <section className="mb-16">
            <h2 className="text-2xl font-semibold mb-8">Resources by Audience</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {resources.map((resource, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{resource.category}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {resource.items.map((item, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                    <Button variant="outline" size="sm" className="w-full mt-4">
                      <ExternalLink className="w-4 h-4 mr-2" />
                      Explore Resources
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </section>

          {/* Community Section */}
          <section className="text-center bg-muted/30 rounded-lg p-12">
            <h2 className="text-2xl font-semibold mb-4">
              Join the Community
            </h2>
            <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
              Connect with developers, journalists, and researchers working on 
              misinformation detection and AI-powered fact-checking solutions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button>
                <Users className="w-4 h-4 mr-2" />
                Join Discord
              </Button>
              <Button variant="outline">
                <ExternalLink className="w-4 h-4 mr-2" />
                GitHub Repository
              </Button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default GetIntoTech;