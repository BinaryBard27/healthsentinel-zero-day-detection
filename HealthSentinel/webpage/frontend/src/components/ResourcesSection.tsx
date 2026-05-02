import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { FileText, Video, Calendar, BookOpen, Download, ArrowRight, Clock, User } from "lucide-react";

export function ResourcesSection() {
  const resources = [
    {
      type: "whitepaper",
      title: "2024 Healthcare Cybersecurity Threat Landscape",
      description: "Comprehensive analysis of emerging threats targeting healthcare organizations and effective defense strategies.",
      category: "Threat Intelligence",
      readTime: "15 min read",
      author: "HealthSentinel Research Team",
      publishDate: "Dec 2024",
      popular: true,
      icon: FileText
    },
    {
      type: "case-study",
      title: "How Regional Medical Center Prevented a $2.3M Ransomware Attack",
      description: "Detailed breakdown of a sophisticated ransomware campaign and how HealthSentinel's AI detection prevented catastrophic damage.",
      category: "Case Study",
      readTime: "10 min read",
      author: "Dr. Sarah Mitchell, CISO",
      publishDate: "Nov 2024",
      popular: false,
      icon: BookOpen
    },
    {
      type: "webinar",
      title: "HIPAA Compliance in the Age of AI: A Practical Guide",
      description: "Expert panel discussion on maintaining regulatory compliance while leveraging AI for cybersecurity.",
      category: "Compliance",
      readTime: "45 min watch",
      author: "Compliance Experts Panel",
      publishDate: "Oct 2024",
      popular: true,
      icon: Video
    },
    {
      type: "guide",
      title: "Zero-Day Defense Implementation Playbook",
      description: "Step-by-step guide for implementing proactive threat detection and response in healthcare environments.",
      category: "Implementation",
      readTime: "20 min read",
      author: "Technical Team",
      publishDate: "Oct 2024",
      popular: false,
      icon: BookOpen
    },
    {
      type: "research",
      title: "The ROI of AI-Powered Cybersecurity in Healthcare",
      description: "Economic analysis demonstrating the financial benefits of investing in advanced cybersecurity solutions.",
      category: "Business Value",
      readTime: "12 min read", 
      author: "Business Intelligence Team",
      publishDate: "Sep 2024",
      popular: true,
      icon: FileText
    },
    {
      type: "webinar",
      title: "Live Demo: Stopping Zero-Day Attacks in Real-Time",
      description: "Interactive demonstration of HealthSentinel's AI engine detecting and blocking unknown threats.",
      category: "Product Demo",
      readTime: "30 min watch",
      author: "Product Team",
      publishDate: "Upcoming",
      popular: false,
      icon: Video
    }
  ];

  const categories = ["All", "Threat Intelligence", "Case Study", "Compliance", "Implementation", "Business Value", "Product Demo"];

  const getResourceIcon = (type: string) => {
    switch (type) {
      case "whitepaper":
      case "research":
        return FileText;
      case "webinar":
        return Video;
      case "case-study":
      case "guide":
        return BookOpen;
      default:
        return FileText;
    }
  };

  return (
    <section className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">Resources</Badge>
          <h2 className="text-4xl font-bold text-foreground mb-6">
            Expert Insights & Resources
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Stay informed with the latest cybersecurity research, best practices, and implementation guides 
            from our team of healthcare security experts.
          </p>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap justify-center gap-2 mb-12">
          {categories.map((category) => (
            <Button
              key={category}
              variant={category === "All" ? "default" : "outline"}
              size="sm"
              className="rounded-full"
            >
              {category}
            </Button>
          ))}
        </div>

        {/* Resources Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {resources.map((resource, index) => {
            const Icon = getResourceIcon(resource.type);
            return (
              <Card key={index} className="hover-lift bg-white group">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-2">
                      <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {resource.category}
                      </Badge>
                    </div>
                    {resource.popular && (
                      <Badge className="bg-primary text-white text-xs">Popular</Badge>
                    )}
                  </div>
                  <CardTitle className="text-lg group-hover:text-primary transition-colors">
                    {resource.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground text-sm mb-6 leading-relaxed">
                    {resource.description}
                  </p>

                  {/* Meta Information */}
                  <div className="space-y-2 mb-6 text-xs text-muted-foreground">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>{resource.readTime}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <User className="w-3 h-3" />
                      <span>{resource.author}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-3 h-3" />
                      <span>{resource.publishDate}</span>
                    </div>
                  </div>

                  <Button 
                    variant="outline" 
                    className="w-full group-hover:border-primary group-hover:text-primary transition-colors"
                  >
                    {resource.type === "webinar" ? "Watch Now" : "Read More"}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Newsletter Signup */}
        <div className="bg-white rounded-2xl p-12 shadow-lg">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold text-foreground mb-4">
                Stay Updated on Healthcare Cybersecurity
              </h3>
              <p className="text-muted-foreground mb-6">
                Get the latest threat intelligence, compliance updates, and security best practices 
                delivered to your inbox monthly.
              </p>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Monthly industry insights</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Early access to research</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Exclusive webinar invitations</span>
              </div>
            </div>
            <div>
              <div className="bg-muted/50 rounded-xl p-6">
                <h4 className="font-semibold text-foreground mb-4">Subscribe to Healthcare Security Insights</h4>
                <div className="space-y-4">
                  <input
                    type="email"
                    placeholder="Enter your email address"
                    className="w-full px-4 py-3 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <Button className="w-full enterprise-gradient text-white">
                    Subscribe
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                  <p className="text-xs text-muted-foreground text-center">
                    No spam. Unsubscribe at any time. HIPAA-compliant communications.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Resource Categories */}
        <div className="mt-16 grid md:grid-cols-4 gap-6">
          <Card className="text-center hover-lift bg-white">
            <CardContent className="pt-8">
              <FileText className="w-12 h-12 text-primary mx-auto mb-4" />
              <h4 className="font-semibold text-foreground mb-2">White Papers</h4>
              <p className="text-sm text-muted-foreground mb-4">In-depth research and analysis</p>
              <Badge variant="outline">15+ Papers</Badge>
            </CardContent>
          </Card>

          <Card className="text-center hover-lift bg-white">
            <CardContent className="pt-8">
              <Video className="w-12 h-12 text-primary mx-auto mb-4" />
              <h4 className="font-semibold text-foreground mb-2">Webinars</h4>
              <p className="text-sm text-muted-foreground mb-4">Expert-led training sessions</p>
              <Badge variant="outline">10+ Sessions</Badge>
            </CardContent>
          </Card>

          <Card className="text-center hover-lift bg-white">
            <CardContent className="pt-8">
              <BookOpen className="w-12 h-12 text-primary mx-auto mb-4" />
              <h4 className="font-semibold text-foreground mb-2">Case Studies</h4>
              <p className="text-sm text-muted-foreground mb-4">Real-world implementation stories</p>
              <Badge variant="outline">25+ Studies</Badge>
            </CardContent>
          </Card>

          <Card className="text-center hover-lift bg-white">
            <CardContent className="pt-8">
              <Download className="w-12 h-12 text-primary mx-auto mb-4" />
              <h4 className="font-semibold text-foreground mb-2">Tools & Guides</h4>
              <p className="text-sm text-muted-foreground mb-4">Practical implementation resources</p>
              <Badge variant="outline">8+ Guides</Badge>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}