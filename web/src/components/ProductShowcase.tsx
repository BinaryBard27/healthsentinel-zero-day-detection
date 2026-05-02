import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Brain, Shield, Activity, Database, ArrowRight, CheckCircle } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function ProductShowcase() {
  const products = [
    {
      id: "ai-engine",
      name: "HealthSentinel AI Engine",
      badge: "Core Platform",
      icon: Brain,
      description: "Advanced machine learning algorithms that adapt to emerging threats in real-time",
      features: [
        "Behavioral anomaly detection",
        "Zero-day exploit prevention", 
        "Automated threat response",
        "Continuous learning algorithms"
      ],
      image: "https://images.unsplash.com/photo-1655036387197-566206c80980?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZGFzaGJvYXJkJTIwcHJvZmVzc2lvbmFsfGVufDF8fHx8MTc1OTQ4Mzc5NXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: "compliance",
      name: "HIPAA Compliance Suite",
      badge: "Healthcare Focused",
      icon: Shield,
      description: "Comprehensive compliance management with automated reporting and audit trails",
      features: [
        "Automated compliance monitoring",
        "Audit trail generation",
        "Risk assessment reporting",
        "Regulatory update management"
      ],
      image: "https://images.unsplash.com/photo-1758691462848-ba1e929da259?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBob3NwaXRhbCUyMGhlYWx0aGNhcmUlMjB0ZWNobm9sb2d5fGVufDF8fHx8MTc1OTQ4Mzc5NHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    },
    {
      id: "monitoring",
      name: "Real-Time Monitoring",
      badge: "24/7 Protection",
      icon: Activity,
      description: "Continuous surveillance of all network activity with instant threat detection",
      features: [
        "Network traffic analysis",
        "Endpoint monitoring",
        "User behavior tracking",
        "Threat intelligence feeds"
      ],
      image: "https://images.unsplash.com/photo-1709803857154-d20ee16ff763?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMG1lZXRpbmclMjBoZWFsdGhjYXJlJTIwZXhlY3V0aXZlc3xlbnwxfHx8fDE3NTk0ODM3OTV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">Product Platform</Badge>
          <h2 className="text-4xl font-bold text-foreground mb-6">
            Comprehensive Security Platform
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            A unified cybersecurity platform designed specifically for healthcare organizations, 
            combining AI-powered threat detection with regulatory compliance and operational efficiency.
          </p>
        </div>

        {/* Product Tabs */}
        <Tabs defaultValue="ai-engine" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-12 h-auto p-1">
            {products.map((product) => {
              const Icon = product.icon;
              return (
                <TabsTrigger 
                  key={product.id} 
                  value={product.id}
                  className="flex flex-col items-center p-4 data-[state=active]:bg-primary data-[state=active]:text-white"
                >
                  <Icon className="w-6 h-6 mb-2" />
                  <span className="font-medium">{product.name}</span>
                  <Badge variant="outline" className="mt-1 text-xs">
                    {product.badge}
                  </Badge>
                </TabsTrigger>
              );
            })}
          </TabsList>

          {products.map((product) => (
            <TabsContent key={product.id} value={product.id} className="mt-0">
              <div className="grid lg:grid-cols-2 gap-12 items-center">
                {/* Product Details */}
                <div>
                  <div className="mb-6">
                    <Badge className="mb-4">{product.badge}</Badge>
                    <h3 className="text-3xl font-bold text-foreground mb-4">
                      {product.name}
                    </h3>
                    <p className="text-lg text-muted-foreground">
                      {product.description}
                    </p>
                  </div>

                  {/* Features */}
                  <div className="space-y-3 mb-8">
                    {product.features.map((feature, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-foreground">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <div className="flex space-x-4">
                    <Button className="enterprise-gradient text-white">
                      Learn More
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                    <Button variant="outline">
                      View Demo
                    </Button>
                  </div>
                </div>

                {/* Product Visual */}
                <div>
                  <Card className="overflow-hidden shadow-lg">
                    <ImageWithFallback 
                      src={product.image}
                      alt={product.name}
                      className="w-full h-80 object-cover"
                    />
                  </Card>
                </div>
              </div>
            </TabsContent>
          ))}
        </Tabs>

        {/* Integration Section */}
        <div className="mt-20 pt-16 border-t border-border">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Seamless Integration
            </h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              HealthSentinel integrates with your existing healthcare infrastructure without disrupting clinical workflows.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="text-center hover-lift">
              <CardHeader>
                <Database className="w-10 h-10 text-primary mx-auto mb-4" />
                <CardTitle className="text-lg">EHR Systems</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Native integration with Epic, Cerner, Allscripts, and other major EHR platforms.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover-lift">
              <CardHeader>
                <Activity className="w-10 h-10 text-primary mx-auto mb-4" />
                <CardTitle className="text-lg">SIEM Integration</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Connect with existing SIEM solutions for centralized security monitoring and reporting.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover-lift">
              <CardHeader>
                <Shield className="w-10 h-10 text-primary mx-auto mb-4" />
                <CardTitle className="text-lg">Legacy Systems</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Protect older medical devices and systems that can't be easily updated or replaced.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}