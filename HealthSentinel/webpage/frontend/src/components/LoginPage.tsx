// src/components/LoginPage.tsx - EVERYTHING IN ONE FILE

import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Checkbox } from "./ui/checkbox";
import { Shield, Lock, Mail, Eye, EyeOff, ArrowLeft, Clock, CheckCircle } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface LoginPageProps {
  onBackToHome: () => void;
  onLoginSuccess: (token: string, email?: string) => void;
  onEmailChange?: (email: string) => void;
}

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export function LoginPage({ onBackToHome, onLoginSuccess, onEmailChange }: LoginPageProps) {
  // ============ STATE ============
  const [step, setStep] = useState<"login" | "otp" | "success">("login");
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [resendCountdown, setResendCountdown] = useState(0);

  // ============ RESEND COUNTDOWN EFFECT ============
  useEffect(() => {
    if (resendCountdown <= 0) return;

    const interval = setInterval(() => {
      setResendCountdown((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [resendCountdown]);

  // ============ API CALLS ============
  const login = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // DEMO MODE: Bypass backend auth for local testing
    setTimeout(() => {
      setStep("otp");
      setResendCountdown(30);
      setLoading(false);
    }, 800);
  };

  const verifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // DEMO MODE: Bypass backend auth for local testing
    setTimeout(() => {
      setStep("success");
      setTimeout(() => {
        onLoginSuccess("demo-token-12345", email);
      }, 1500);
    }, 800);
  };

  const resendOTP = async () => {
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/auth/resend-otp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        setError("Failed to resend OTP");
        setLoading(false);
        return;
      }

      setResendCountdown(30);
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const goBackToLogin = () => {
    setStep("login");
    setOtp("");
    setError("");
    setResendCountdown(0);
  };

  // ============ RENDER - LOGIN STEP ============
  if (step === "login") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary to-accent relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1655036387197-566206c80980?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZGFzaGJvYXJkJTIwcHJvZmVzc2lvbmFsfGVufDF8fHx8MTc1OTQ4Mzc5NXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
              alt="Background"
              className="w-full h-full object-cover"
            />
          </div>

          <div className="relative z-10 flex flex-col justify-center px-16 text-white">
            <div className="flex items-center space-x-3 mb-8">
              <Shield className="w-12 h-12" />
              <span className="text-3xl font-bold">HealthSentinel</span>
            </div>

            <h1 className="text-4xl font-bold mb-6 leading-tight">
              Secure Access to<br />
              Healthcare Cybersecurity
            </h1>

            <p className="text-xl mb-8 text-white/90 leading-relaxed">
              Protecting patient data and critical systems with AI-powered threat detection
              and enterprise-grade security.
            </p>

            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <Lock className="w-5 h-5 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Enterprise-Grade Security</h3>
                  <p className="text-white/80 text-sm">SOC 2 Type II and HIPAA compliant infrastructure</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Shield className="w-5 h-5 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">Multi-Factor Authentication</h3>
                  <p className="text-white/80 text-sm">Advanced security protocols protect your account</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Lock className="w-5 h-5 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold mb-1">24/7 Monitoring</h3>
                  <p className="text-white/80 text-sm">Continuous threat detection and response</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="flex-1 flex items-center justify-center px-6 sm:px-12">
          <div className="w-full max-w-md">
            {/* Back to Home */}
            <button
              onClick={onBackToHome}
              className="flex items-center space-x-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Home</span>
            </button>

            <Card className="border-0 shadow-xl">
              <CardHeader className="space-y-1 text-center pb-8">
                <div className="flex justify-center mb-4 lg:hidden">
                  <div className="flex items-center space-x-2">
                    <Shield className="w-8 h-8 text-primary" />
                    <span className="text-2xl font-bold text-foreground">HealthSentinel</span>
                  </div>
                </div>
                <CardTitle className="text-2xl">Welcome back</CardTitle>
                <CardDescription>
                  Sign in to your HealthSentinel account to access your security dashboard
                </CardDescription>
              </CardHeader>

              <CardContent>
                <form onSubmit={login} className="space-y-6">
                  {/* Email Field */}
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="you@company.com"
                        className="pl-10"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        disabled={loading}
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="password">Password</Label>
                      <a href="#" className="text-sm text-primary hover:underline">
                        Forgot password?
                      </a>
                    </div>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter your password"
                        className="pl-10 pr-10"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        disabled={loading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Error Message */}
                  {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                      {error}
                    </div>
                  )}

                  {/* Remember Me */}
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="remember"
                      checked={rememberMe}
                      onCheckedChange={(checked) => setRememberMe(checked as boolean)}
                      disabled={loading}
                    />
                    <label
                      htmlFor="remember"
                      className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                    >
                      Remember me for 30 days
                    </label>
                  </div>

                  {/* Sign In Button */}
                  <Button
                    type="submit"
                    className="w-full enterprise-gradient text-white h-11"
                    disabled={loading}
                  >
                    {loading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>

                {/* Divider */}
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border"></div>
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>

                {/* SSO Options */}
                <div className="grid grid-cols-2 gap-4">
                  <Button variant="outline" type="button" disabled={loading}>
                    <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                      <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    Google
                  </Button>
                  <Button variant="outline" type="button" disabled={loading}>
                    <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                    </svg>
                    LinkedIn
                  </Button>
                </div>
              </CardContent>

              <CardFooter className="flex flex-col space-y-4 border-t pt-6">
                <div className="text-center text-sm text-muted-foreground">
                  Don't have an account?{" "}
                  <a href="#" className="text-primary hover:underline font-medium">
                    Request a demo
                  </a>
                </div>

                <div className="text-center text-xs text-muted-foreground">
                  By signing in, you agree to our{" "}
                  <a href="#" className="text-primary hover:underline">Terms of Service</a>
                  {" "}and{" "}
                  <a href="#" className="text-primary hover:underline">Privacy Policy</a>
                </div>
              </CardFooter>
            </Card>

            {/* Security Notice */}
            <div className="mt-6 text-center">
              <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground">
                <Shield className="w-4 h-4 text-green-500" />
                <span>Secured with 256-bit SSL encryption</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ============ RENDER - OTP STEP ============
  if (step === "otp") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          {/* Back Button */}
          <button
            onClick={goBackToLogin}
            className="flex items-center space-x-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>

          <Card className="border-0 shadow-xl">
            <CardHeader className="space-y-1 text-center pb-8">
              <div className="flex justify-center mb-4">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Shield className="w-6 h-6 text-primary" />
                </div>
              </div>
              <CardTitle className="text-2xl">Verify Your Identity</CardTitle>
              <CardDescription>
                We sent a 6-digit code to <strong>{email}</strong>
              </CardDescription>
            </CardHeader>

            <CardContent>
              <form onSubmit={verifyOTP} className="space-y-6">
                {/* OTP Input */}
                <div className="space-y-2">
                  <Label htmlFor="otp">Enter OTP Code</Label>
                  <Input
                    id="otp"
                    type="text"
                    inputMode="numeric"
                    value={otp}
                    onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    placeholder="000000"
                    maxLength={6}
                    required
                    disabled={loading}
                    className="text-center text-2xl tracking-widest font-mono"
                  />
                </div>

                {/* Error Message */}
                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {error}
                  </div>
                )}

                {/* Verify Button */}
                <Button
                  type="submit"
                  className="w-full enterprise-gradient text-white h-11"
                  disabled={loading || otp.length !== 6}
                >
                  {loading ? "Verifying..." : "Verify OTP"}
                </Button>

                {/* Resend Button */}
                <button
                  type="button"
                  onClick={resendOTP}
                  disabled={resendCountdown > 0 || loading}
                  className="w-full text-primary hover:text-primary/80 font-semibold py-2 disabled:text-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
                >
                  {resendCountdown > 0 ? (
                    <>
                      <Clock className="w-4 h-4" />
                      Resend in {resendCountdown}s
                    </>
                  ) : (
                    "Resend OTP"
                  )}
                </button>
              </form>
            </CardContent>
          </Card>

          {/* Security Notice */}
          <div className="mt-6 text-center">
            <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground">
              <Shield className="w-4 h-4 text-green-500" />
              <span>Secured with 256-bit SSL encryption</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ============ RENDER - SUCCESS STEP ============
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="border-0 shadow-xl">
          <CardHeader className="space-y-1 text-center pb-8">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
            <CardTitle className="text-2xl">Login Successful!</CardTitle>
            <CardDescription>
              Redirecting to dashboard...
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}