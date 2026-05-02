import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Quote, Star } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function CustomerTestimonials() {
  const testimonials = [
    {
      quote: "HealthSentinel has transformed our cybersecurity posture. We've seen a 99.7% reduction in successful attacks while maintaining full HIPAA compliance. The AI-powered detection caught threats our previous solution missed entirely.",
      author: "Dr. Sarah Mitchell",
      title: "Chief Information Security Officer",
      company: "Regional Medical Center",
      companySize: "5,000+ employees",
      image: "https://images.unsplash.com/photo-1585900464046-f713a61424dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZXhwZXJ0JTIwcHJvZmVzc2lvbmFsJTIwaGVhZHNob3R8ZW58MXx8fHwxNzU5NDgzODg0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      rating: 5,
      results: ["99.7% threat reduction", "Zero downtime incidents", "Full HIPAA compliance"]
    },
    {
      quote: "The implementation was seamless and the results immediate. HealthSentinel's AI detected and blocked a sophisticated ransomware attack that could have shut down our entire network. ROI was evident within the first month.",
      author: "Michael Thompson",
      title: "IT Director",
      company: "Community Health Network",
      companySize: "1,200+ employees",
      image: "https://images.unsplash.com/photo-1758691463582-11aea602cd4a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidXNpbmVzcyUyMGV4ZWN1dGl2ZSUyMGhlYWx0aGNhcmUlMjBDRU98ZW58MXx8fHwxNzU5NDgzODg0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      rating: 5,
      results: ["Ransomware attack prevented", "30-day ROI achieved", "Zero business disruption"]
    },
    {
      quote: "As a smaller practice, we needed enterprise-level security without the complexity. HealthSentinel delivers exactly that. The automated compliance reporting alone saves us 20 hours per month of manual work.",
      author: "Dr. Jennifer Park",
      title: "Practice Owner",
      company: "Park Family Medicine",
      companySize: "25 employees",
      image: "https://images.unsplash.com/photo-1585900464046-f713a61424dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZXhwZXJ0JTIwcHJvZmVzc2lvbmFsJTIwaGVhZHNob3R8ZW58MXx8fHwxNzU5NDgzODg0fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      rating: 5,
      results: ["20 hours/month saved", "Automated compliance", "Simple deployment"]
    }
  ];

  const stats = [
    { value: "750+", label: "Healthcare Customers" },
    { value: "4.9/5", label: "Customer Satisfaction" },
    { value: "99.9%", label: "Uptime SLA" },
    { value: "< 30 days", label: "Average ROI Timeline" }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">Customer Success</Badge>
          <h2 className="text-4xl font-bold text-foreground mb-6">
            Trusted by Healthcare Leaders
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            See how leading healthcare organizations are protecting their patients and data with HealthSentinel.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-4 gap-8 mb-16">
          {stats.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl font-bold text-primary mb-2">{stat.value}</div>
              <div className="text-muted-foreground">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Testimonials */}
        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial, index) => (
            <Card key={index} className="hover-lift">
              <CardContent className="p-8">
                {/* Quote Icon */}
                <Quote className="w-8 h-8 text-primary mb-6" />
                
                {/* Rating */}
                <div className="flex items-center space-x-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>

                {/* Quote */}
                <blockquote className="text-foreground mb-6 italic leading-relaxed">
                  "{testimonial.quote}"
                </blockquote>

                {/* Results */}
                <div className="space-y-2 mb-6">
                  {testimonial.results.map((result, resultIndex) => (
                    <div key={resultIndex} className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-muted-foreground">{result}</span>
                    </div>
                  ))}
                </div>

                {/* Author */}
                <div className="flex items-center space-x-4 pt-6 border-t border-border">
                  <div className="w-12 h-12 rounded-full overflow-hidden">
                    <ImageWithFallback 
                      src={testimonial.image}
                      alt={testimonial.author}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <div className="font-semibold text-foreground">{testimonial.author}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.title}</div>
                    <div className="text-sm text-muted-foreground">{testimonial.company}</div>
                    <div className="text-xs text-muted-foreground">{testimonial.companySize}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Case Study CTA */}
        <div className="bg-gradient-to-r from-primary/5 to-accent/5 rounded-2xl p-12 text-center">
          <h3 className="text-2xl font-bold text-foreground mb-4">
            Read Detailed Customer Success Stories
          </h3>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Explore in-depth case studies showing how HealthSentinel has helped healthcare organizations 
            prevent cyber attacks and achieve compliance goals.
          </p>
          <div className="space-x-4">
            <Badge variant="outline" className="mr-2">Mayo Clinic Case Study</Badge>
            <Badge variant="outline" className="mr-2">Johns Hopkins Implementation</Badge>
            <Badge variant="outline">Community Health ROI Analysis</Badge>
          </div>
        </div>

        {/* Industry Recognition */}
        <div className="mt-16 pt-12 border-t border-border">
          <div className="text-center mb-8">
            <h3 className="text-xl font-semibold text-foreground mb-4">Industry Recognition</h3>
            <div className="flex flex-wrap justify-center items-center gap-8 text-muted-foreground">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Star className="w-4 h-4 text-primary" />
                </div>
                <span>Gartner Cool Vendor 2024</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Star className="w-4 h-4 text-primary" />
                </div>
                <span>HIMSS Innovation Award</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Star className="w-4 h-4 text-primary" />
                </div>
                <span>Healthcare IT News Top Vendor</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}